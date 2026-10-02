const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value, maximum, nonempty = false) => typeof value === 'string' && value.length <= maximum && (!nonempty || value.trim().length > 0);
const invalidBackup = () => Error('This is not a supported Coursekin backup.');

// Reconstruct the supported fields so imported data cannot add arbitrary state.
export function readBackup(value) {
  if (!object(value) || value.format !== 'coursekin-browser' || value.version !== 1 ||
      !text(value.name, 100, true) || !Array.isArray(value.documents) || value.documents.length > 20 ||
      !Array.isArray(value.messages)) throw invalidBackup();
  const ids = new Set();
  const documents = value.documents.map(document => {
    if (!object(document) || !text(document.id, 100, true) || ids.has(document.id) ||
        !text(document.name, 1000, true) || !Array.isArray(document.pages) || document.pages.length < 1 ||
        document.pages.length > 1500 || document.pages.some(page => !text(page, 600000)) ||
        document.pages.reduce((size, page) => size + page.length, 0) > 600000) throw invalidBackup();
    ids.add(document.id);
    return { id: document.id, name: document.name, pages: [...document.pages] };
  });
  const messages = value.messages.map(message => {
    if (!object(message) || !['user', 'assistant'].includes(message.role) || typeof message.text !== 'string' ||
        (message.sources !== undefined && (!Array.isArray(message.sources) || message.sources.length > 6))) throw invalidBackup();
    const sources = message.sources?.map(source => {
      if (!object(source) || !text(source.id, 20, true) || !text(source.name, 1000, true) ||
          !Number.isInteger(source.page) || source.page < 1 || source.page > 1500 ||
          !text(source.text, 1200)) throw invalidBackup();
      return { id: source.id, name: source.name, page: source.page, text: source.text };
    });
    return { role: message.role, text: message.text, ...(sources === undefined ? {} : { sources }) };
  });
  return { name: value.name, documents, messages };
}

const normalize = value => value.normalize('NFKC').toLowerCase();
const segmenter = typeof Intl.Segmenter === 'function' ? new Intl.Segmenter(undefined, { granularity: 'word' }) : null;
function words(value) {
  const normalized = normalize(value);
  // Segment both query and source text: pH must not match inside photosynthesis.
  return new Set(segmenter
    ? [...segmenter.segment(normalized)].filter(part => part.isWordLike).map(part => part.segment)
    : normalized.match(/[\p{L}\p{M}\p{N}]+/gu) || []);
}
export function retrieve(course, question) {
  const terms = [...words(question)], chunks = [], frequency = new Map();
  if (!terms.length) return [];
  let chunkCount = 0;
  for (const document of course.documents) {
    for (let page = 0; page < document.pages.length; page++) {
      const content = document.pages[page];
      for (let start = 0; start < content.length; start += 1000) {
        const excerpt = content.slice(start, start + 1200), sourceWords = words(excerpt);
        const matched = terms.filter(term => sourceWords.has(term));
        chunkCount++;
        for (const term of matched) frequency.set(term, (frequency.get(term) || 0) + 1);
        if (matched.length) chunks.push({ name: document.name, page: page + 1, text: excerpt, matched });
      }
    }
  }
  // Common question words contribute less than terms appearing in few excerpts.
  return chunks.map(({ matched, ...source }) => ({
    ...source,
    score: matched.reduce((sum, term) => sum + Math.log(1 + (chunkCount - frequency.get(term) + 0.5) / (frequency.get(term) + 0.5)), 0),
  })).sort((a, b) => b.score - a.score).slice(0, 6).map((source, index) => ({ ...source, id: String(index + 1) }));
}
