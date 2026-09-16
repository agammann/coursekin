import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

class Store:
    def __init__(self, path):
        self.path = str(path)
        with self.connect() as db:
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS courses(id TEXT PRIMARY KEY, name TEXT NOT NULL, created TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, course TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE, role TEXT NOT NULL, name TEXT NOT NULL, chunks INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS passages(id INTEGER PRIMARY KEY, course TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE, document TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE, location TEXT NOT NULL, text TEXT NOT NULL);
            CREATE VIRTUAL TABLE IF NOT EXISTS passage_search USING fts5(text, content='passages', content_rowid='id', tokenize='porter unicode61');
            CREATE TRIGGER IF NOT EXISTS passage_add AFTER INSERT ON passages BEGIN INSERT INTO passage_search(rowid,text) VALUES(new.id,new.text); END;
            CREATE TRIGGER IF NOT EXISTS passage_delete AFTER DELETE ON passages BEGIN INSERT INTO passage_search(passage_search,rowid,text) VALUES('delete',old.id,old.text); END;
            CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, course TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE, role TEXT NOT NULL, text TEXT NOT NULL, sources TEXT NOT NULL DEFAULT '[]');
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    def create(self, name, docs):
        cid = uuid.uuid4().hex
        with self.connect() as db:
            db.execute('INSERT INTO courses VALUES(?,?,?)', (cid, name, datetime.now(timezone.utc).isoformat()))
            self._insert_docs(db, cid, docs)
        return self.get(cid)

    def _insert_docs(self, db, cid, docs):
        for doc in docs:
            did = uuid.uuid4().hex
            db.execute('INSERT INTO documents VALUES(?,?,?,?,?)', (did, cid, doc['role'], doc['name'], len(doc['chunks'])))
            db.executemany('INSERT INTO passages(course,document,location,text) VALUES(?,?,?,?)', [(cid, did, p['location'], p['text']) for p in doc['chunks']])

    def add_documents(self, cid, docs):
        with self.connect() as db:
            self._insert_docs(db, cid, docs)
        return self.get(cid)

    def list(self):
        with self.connect() as db:
            return [dict(x) for x in db.execute('SELECT * FROM courses ORDER BY created DESC')]

    def get(self, cid):
        with self.connect() as db:
            row = db.execute('SELECT * FROM courses WHERE id=?', (cid,)).fetchone()
            if not row:
                return None
            result = dict(row)
            result['documents'] = [dict(x) for x in db.execute('SELECT id,role,name,chunks FROM documents WHERE course=? ORDER BY rowid', (cid,))]
            result['messages'] = [dict(x) for x in db.execute('SELECT role,text,sources FROM messages WHERE course=? ORDER BY id', (cid,))]
            for m in result['messages']:
                m['sources'] = json.loads(m['sources'])
            return result

    def search(self, cid, query):
        stop = set('a an the is are to of in for and or i my me you it this that what how can do does when with please about from on'.split())
        words = [w for w in re.findall(r'\w+', query.lower()) if w not in stop and len(w) > 1][:32]
        match = ' OR '.join('"' + w.replace('"', '') + '"' for w in dict.fromkeys(words))
        base = 'SELECT p.id,p.text,p.location,d.name,d.role FROM passages p JOIN documents d ON d.id=p.document '
        with self.connect() as db:
            hits = []
            if match:
                hits = db.execute(base + 'JOIN passage_search s ON s.rowid=p.id WHERE passage_search MATCH ? AND p.course=? ORDER BY bm25(passage_search) LIMIT 9', (match, cid)).fetchall()
            # Keep a little syllabus context even for conceptual textbook questions.
            syllabus = db.execute(base + "WHERE p.course=? AND d.role='syllabus' ORDER BY p.id LIMIT 2", (cid,)).fetchall()
            if not hits:
                hits = db.execute(base + 'WHERE p.course=? ORDER BY p.id LIMIT 6', (cid,)).fetchall()
            unique = {r['id']: dict(r) for r in [*hits, *syllabus]}
            return [dict(r, number=i+1) for i, r in enumerate(unique.values())]

    def save_exchange(self, cid, question, answer, sources):
        with self.connect() as db:
            db.execute('INSERT INTO messages(course,role,text) VALUES(?,?,?)', (cid, 'user', question))
            db.execute('INSERT INTO messages(course,role,text,sources) VALUES(?,?,?,?)', (cid, 'assistant', answer, json.dumps(sources)))

    def delete(self, cid):
        with self.connect() as db:
            db.execute('DELETE FROM courses WHERE id=?', (cid,))

    def export(self, cid):
        result = self.get(cid)
        with self.connect() as db:
            result['passages'] = [dict(x) for x in db.execute('SELECT document,location,text FROM passages WHERE course=? ORDER BY id', (cid,))]
        return result
