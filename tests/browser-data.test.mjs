import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readBackup, retrieve } from '../web/study-data.mjs';

const backup = () => ({
  format: 'coursekin-browser', version: 1, name: 'Chemistry',
  documents: [{ id: 'notes', name: 'notes.txt', pages: ['A neutral solution has a pH of 7.'] }],
  messages: [{ role: 'assistant', text: 'The value is 7. [1]', sources: [{ id: '1', name: 'notes.txt', page: 1, text: 'A neutral solution has a pH of 7.', score: 1 }] }],
});

test('valid backups retain class material and cited answers without arbitrary fields', () => {
  const value = backup(); value.apiKey = 'not-a-real-key';
  const restored = readBackup(value);
  assert.equal(restored.name, value.name);
  assert.deepEqual(restored.documents, value.documents);
  assert.equal(restored.messages[0].sources[0].text, value.messages[0].sources[0].text);
  assert.equal('apiKey' in restored, false);
  assert.equal('score' in restored.messages[0].sources[0], false);
});

test('malformed nested backup records fail before they can reach rendering or storage', () => {
  const invalid = [null, {}, { ...backup(), documents: [null] }, { ...backup(), messages: [null] }];
  for (const source of [null, {}, { id: '1', name: 'notes', page: '1', text: 'quote' }, { id: '1', name: 'notes', page: 0, text: 'quote' }, { id: '1', name: 'notes', page: 1, text: null }]) {
    invalid.push({ ...backup(), messages: [{ role: 'assistant', text: 'answer', sources: [source] }] });
  }
  for (const value of invalid) assert.throws(() => readBackup(value), /supported Coursekin backup/);
});

test('duplicate document identities and oversized source pages are rejected', () => {
  const duplicate = backup(); duplicate.documents.push({ ...duplicate.documents[0] });
  assert.throws(() => readBackup(duplicate), /supported Coursekin backup/);
  const oversized = backup(); oversized.documents[0].pages = ['x'.repeat(600001)];
  assert.throws(() => readBackup(oversized), /supported Coursekin backup/);
});

test('retrieval finds short and non-Latin terms without changing cited source text', () => {
  const course = { documents: [
    { name: 'chemistry.txt', pages: ['A neutral solution has a pH of 7.'] },
    { name: 'biology.txt', pages: ['光合作用把光能转化为化学能。'] },
    { name: 'history.txt', pages: ['Η δημοκρατία αναπτύχθηκε στην Αθήνα.'] },
  ] };
  for (const [question, name] of [['pH', 'chemistry.txt'], ['光合作用', 'biology.txt'], ['δημοκρατία', 'history.txt'], ['ｐＨ', 'chemistry.txt']]) {
    const sources = retrieve(course, question);
    assert.equal(sources[0]?.name, name);
    assert.equal(sources[0].text, course.documents.find(document => document.name === name).pages[0]);
  }
  assert.deepEqual(retrieve(course, 'quasars'), []);
});

test('retrieval stays within its six-excerpt and 1200-character bounds', () => {
  const sources = retrieve({ documents: [{ name: 'long.txt', pages: ['pH '.repeat(5000)] }] }, 'pH');
  assert.equal(sources.length, 6);
  assert.deepEqual(sources.map(source => source.id), ['1', '2', '3', '4', '5', '6']);
  assert(sources.every(source => source.text.length <= 1200));
});

test('exact short terms outrank more than six earlier passages matching common question words', () => {
  const course = { documents: [
    { name: 'biology.txt', pages: Array.from({ length: 8 }, () => 'What is photosynthesis? It is the conversion of light energy into chemical energy.') },
    { name: 'chemistry.txt', pages: ['A neutral solution has a pH of 7.'] },
  ] };
  assert.deepEqual(retrieve(course, 'pH').map(source => source.name), ['chemistry.txt']);
  const sources = retrieve(course, 'What is pH?');
  assert.equal(sources[0].name, 'chemistry.txt');
  assert.equal(sources[0].text, course.documents[1].pages[0]);
  assert.equal(sources[0].id, '1');
});
