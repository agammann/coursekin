import { HOSTED_MODELS, validateQuestion, validateAnswer } from './answer-contract.mjs';

export async function answerHosted(question, { apiKey, model = 'gpt-5.4', signal } = {}) {
  signal?.throwIfAborted();
  const key = typeof apiKey === 'string' ? apiKey.trim() : '';
  if (!/^sk-[A-Za-z0-9_-]{16,512}$/.test(key)) throw Error('Enter your own OpenAI API key to use hosted answers.');
  if (!HOSTED_MODELS.includes(model)) throw Error('Choose a supported hosted model.');
  const input = validateQuestion(question);
  const response = await fetch('/api/answer/visitor', {
    method: 'POST', credentials: 'omit', cache: 'no-store', redirect: 'error', signal,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
    body: JSON.stringify({ question: input, model }),
  });
  let result;
  try { result = await response.json(); }
  catch (error) {
    signal?.throwIfAborted();
    if (error?.name === 'AbortError') throw error;
    throw Error('The hosted service did not return an answer. Use the Coursekin website or its Worker preview, then try again.');
  }
  signal?.throwIfAborted();
  if (!response.ok) throw Error(typeof result?.error === 'string' ? result.error : 'Hosted answers are unavailable. Your conversation is unchanged.');
  return { value: validateAnswer(result.value, input.excerpts), model: result.model };
}
