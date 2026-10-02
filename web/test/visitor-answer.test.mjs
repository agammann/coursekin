import test from 'node:test';
import assert from 'node:assert/strict';
import { visitorAnswer } from '../visitor-answer.mjs';
import { validateQuestion, validateAnswer } from '../answer-contract.mjs';
const key = 'sk-' + 'coursekin_synthetic_unit_test_key_123456789';
const question = { question: 'What is the exam weight?', recentConversation: [], excerpts: [{ id: '1', name: 'syllabus.txt', page: 1, text: 'The final exam is 40% of the grade.' }] };
const body = () => ({ model: 'gpt-5.4', question: structuredClone(question) });
const request = (value = body(), headers = {}, signal) => new Request('https://coursekin.example/api/answer/visitor', { method: 'POST', signal, headers: { Origin: 'https://coursekin.example', Authorization: 'Bearer ' + key, 'Content-Type': 'application/json', ...headers }, body: typeof value === 'string' ? value : JSON.stringify(value) });
const completion = value => Response.json({ status: 'completed', output: [{ type: 'message', content: [{ type: 'output_text', text: typeof value === 'string' ? value : JSON.stringify(value) }] }] });
const answer = () => ({ answer: 'The final exam is 40% [source:1].', sourceIds: ['1'] });
const unexpected = () => { throw Error('Provider must not be called'); };

test('visitor request uses its key and bounded source context with no storage or redirect following', async () => {
  let calls = 0;
  const response = await visitorAnswer(request(), { fetchImpl: async (url, options) => {
    calls++; assert.equal(url, 'https://api.openai.com/v1/responses'); assert.equal(options.redirect, 'manual');
    assert.equal(options.headers.Authorization, 'Bearer ' + key);
    const payload = JSON.parse(options.body); assert.equal(payload.store, false); assert.equal(payload.model, 'gpt-5.4');
    assert.deepEqual(JSON.parse(payload.input), question); assert.equal(payload.text.format.strict, true);
    return completion(answer());
  } });
  assert.equal(response.status, 200); assert.equal(calls, 1); assert.match(response.headers.get('Cache-Control'), /no-store/);
  assert.deepEqual((await response.json()).value, answer());
});
test('invalid credentials, origins, model and source bounds never reach a provider', async () => {
  const duplicate = body(); duplicate.question.excerpts.push(duplicate.question.excerpts[0]);
  const oversized = body(); oversized.question.excerpts[0].text = 'x'.repeat(1201);
  for (const req of [request(body(), { Authorization: '' }), request(body(), { Origin: 'https://other.example' }), request({ ...body(), model: 'unknown' }), request(duplicate), request(oversized), request('x'.repeat(256 * 1024 + 1))]) {
    assert((await visitorAnswer(req, { fetchImpl: unexpected })).status >= 400);
  }
  assert.throws(() => validateQuestion({ ...question, excerpts: [{ ...question.excerpts[0], id: 1 }] }));
  assert.deepEqual(validateQuestion({ ...question, excerpts: [{ ...question.excerpts[0], score: 6.6029677386274175 }] }), question);
});
test('provider redirects and errors are returned safely without a second request', async () => {
  for (const status of [302, 401, 403, 429, 500]) {
    let calls = 0;
    const response = await visitorAnswer(request(), { fetchImpl: async () => { calls++; return new Response('provider private diagnostic ' + key, { status, headers: { Location: 'https://elsewhere.example' } }); } });
    assert.equal(calls, 1); assert(response.status >= 400); assert(!(await response.text()).includes(key));
  }
});
test('unknown, grouped, ranged and malformed explicit citations fail the source check', () => {
  for (const citation of ['[source:7]', '[source:1, 7]', '[source:7, 8]', '[source:7–8]', '[source:1-2]', '[source:]', '[source:one]', '[source:1', '[source:1 extra]', '[source: 1]', '[SOURCE:1]', '[ source:1]']) {
    assert.throws(() => validateAnswer({ answer: 'Claim ' + citation, sourceIds: ['1'] }, question.excerpts), citation);
  }
  assert.throws(() => validateAnswer({ answer: 'Claim [source:1]', sourceIds: [1] }, question.excerpts));
  assert.throws(() => validateAnswer({ answer: 'Claim [source:2]', sourceIds: ['1'] }, [...question.excerpts, { ...question.excerpts[0], id: '2' }]));
  assert.deepEqual(validateAnswer(answer(), question.excerpts), answer());
});
test('mathematical brackets are preserved alongside explicit citations', () => {
  for (const expression of ['[0, 1]', '[-1, 1]', '2[x + 1]']) {
    const value = { answer: `The expression is ${expression}. [source:1]`, sourceIds: ['1'] };
    assert.deepEqual(validateAnswer(value, question.excerpts), value);
  }
  assert.deepEqual(validateAnswer({ answer: 'The domain is [0, 1].', sourceIds: ['1'] }, question.excerpts), {
    answer: 'The domain is [0, 1].\n\nSource excerpts: [source:1]', sourceIds: ['1'],
  });
});
test('decoded input and output cannot contain the visitor key', async () => {
  const escaped = [...key].map(c => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0')).join('');
  const inbound = JSON.stringify(body()).replace('What is the exam weight?', escaped);
  assert.equal((await visitorAnswer(request(inbound), { fetchImpl: unexpected })).status, 400);
  const outbound = JSON.stringify({ answer: 'PLACEHOLDER [source:1]', sourceIds: ['1'] }).replace('PLACEHOLDER', escaped);
  const response = await visitorAnswer(request(), { fetchImpl: async () => completion(outbound) });
  assert.equal(response.status, 502); assert(!(await response.text()).includes(key));
});
test('stopped uploads release their body without waiting for the provider deadline', async () => {
  const controller = new AbortController(); let canceled = false;
  const stream = new ReadableStream({ start(c) { c.enqueue(new TextEncoder().encode('{')); }, cancel() { canceled = true; } });
  const req = new Request('https://coursekin.example/api/answer/visitor', { method: 'POST', duplex: 'half', signal: controller.signal, headers: { Origin: 'https://coursekin.example', Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' }, body: stream });
  const pending = visitorAnswer(req, { fetchImpl: unexpected }); controller.abort();
  assert.equal((await pending).status, 499); assert(canceled);
});
test('incomplete answers, refusals and invalid output preserve the failure boundary', async () => {
  for (const response of [Response.json({ status: 'incomplete' }), Response.json({ status: 'completed', output: [{ type: 'message', content: [{ type: 'refusal' }] }] }), completion({ answer: 'Unknown [source:2]', sourceIds: ['2'] }), completion({ answer: 'Malformed [source:1, 7]', sourceIds: ['1'] })]) {
    assert((await visitorAnswer(request(), { fetchImpl: async () => response })).status >= 400);
  }
});
