import { HOSTED_MODELS, tutorInstructions, validateQuestion, answerSchema, validateAnswer } from './answer-contract.mjs';

class RequestError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}
async function limitedText(message, limit, signal) {
  const reader = message.body?.getReader();
  if (!reader) throw new RequestError('The request or response was empty.');
  const parts = []; let size = 0;
  const stop = () => { reader.cancel(signal.reason).catch(() => {}); };
  signal.addEventListener('abort', stop, { once: true });
  try {
    signal.throwIfAborted();
    while (true) {
      const { value, done } = await reader.read(); signal.throwIfAborted(); if (done) break;
      size += value.byteLength;
      if (size > limit) throw new RequestError('The question or response is too large.', 413);
      parts.push(value);
    }
    const bytes = new Uint8Array(size); let offset = 0;
    for (const part of parts) { bytes.set(part, offset); offset += part.byteLength; }
    return new TextDecoder().decode(bytes);
  } finally { signal.removeEventListener('abort', stop); await reader.cancel().catch(() => {}); reader.releaseLock(); }
}
const json = (value, status = 200) => Response.json(value, { status, headers: { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer' } });
function providerError(status) {
  if (status === 401) return new RequestError('OpenAI rejected this key. Check your API key and try again.', 401);
  if (status === 403 || status === 404) return new RequestError('This key cannot access the selected model. Check its permissions or choose another model.', 403);
  if (status === 429) return new RequestError('OpenAI reported a usage or rate limit. Check your API billing and limits.', 429);
  return new RequestError('OpenAI could not answer the question. Try again later.', 502);
}

// Only the visitor-supplied key is used. No environment fallback or automatic retry.
export async function visitorAnswer(request, { fetchImpl = fetch } = {}) {
  let signal;
  try {
    if (request.method !== 'POST') throw new RequestError('Method not allowed.', 405);
    if (request.headers.get('Origin') !== new URL(request.url).origin) throw new RequestError('Open Coursekin to ask a question.', 403);
    const key = /^Bearer (sk-[A-Za-z0-9_-]{16,512})$/.exec(request.headers.get('Authorization') || '')?.[1];
    if (!key) throw new RequestError('Enter your own OpenAI API key to use hosted answers.', 401);
    if (!/^application\/json(?:;|$)/i.test(request.headers.get('Content-Type') || '')) throw new RequestError('Send a JSON question.');
    signal = AbortSignal.any([request.signal, AbortSignal.timeout(180000)]);
    const raw = await limitedText(request, 256 * 1024, signal);
    let data, question;
    try {
      data = JSON.parse(raw);
      if (!HOSTED_MODELS.includes(data.model)) throw Error('model');
      question = validateQuestion(data.question);
    } catch { throw new RequestError('Provide a supported model, a question and up to six valid source excerpts.'); }
    if (raw.includes(key) || JSON.stringify(question).includes(key)) throw new RequestError('Keep the API key in its key field, not in course materials or questions.');
    signal.throwIfAborted();
    const response = await fetchImpl('https://api.openai.com/v1/responses', {
      method: 'POST', redirect: 'manual', signal,
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: data.model, store: false, max_output_tokens: 12000, reasoning: { effort: 'medium' },
        instructions: tutorInstructions, input: JSON.stringify(question),
        text: { format: { type: 'json_schema', name: 'coursekin_answer', strict: true, schema: answerSchema(question.excerpts) } },
      }),
    });
    if (!response.ok) { await response.body?.cancel(); throw providerError(response.status); }
    let completion;
    try { completion = JSON.parse(await limitedText(response, 2 * 1024 * 1024, signal)); }
    catch { throw new RequestError('OpenAI returned an unreadable answer. Your conversation is unchanged.', 502); }
    signal.throwIfAborted();
    if (completion.status !== 'completed') throw new RequestError('The answer did not finish. Your conversation is unchanged. Try again.', 502);
    const content = (completion.output || []).flatMap(item => item.type === 'message' ? item.content || [] : []);
    if (content.some(part => part.type === 'refusal')) throw new RequestError('The model could not answer this question. Try rephrasing it.', 422);
    const output = content.filter(part => part.type === 'output_text').map(part => part.text).join('');
    if (!output || output.includes(key)) throw new RequestError('The answer could not be returned safely.', 502);
    let value;
    try { value = validateAnswer(JSON.parse(output), question.excerpts); }
    catch { throw new RequestError('The answer did not pass source-reference checks. Your conversation is unchanged.', 502); }
    if (value.answer.includes(key)) throw new RequestError('The answer could not be returned safely.', 502);
    return json({ value, model: data.model });
  } catch (error) {
    if (request.signal.aborted) return json({ error: 'Answer canceled.' }, 499);
    if (signal?.aborted) return json({ error: 'The answer timed out. Your conversation is unchanged. Try again.' }, 504);
    return json({ error: error instanceof RequestError ? error.message : 'The answer could not be completed. Your conversation is unchanged. Try again.' }, error instanceof RequestError ? error.status : 502);
  }
}
