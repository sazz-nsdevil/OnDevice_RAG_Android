PRAGMA froreign key=ON;
CREATE TABLE IF NOT EXISTS meta(
    key TEXT primary key,
    value TEXT NOT NULL
);

--uploaded document
CREATE TABLE IF NOT EXISTS documents(
    doc_id INTEGER PRIMARY KEY ,
    title TEXT NOT NULL,
    grade INTEGER NOT NULL,
    subjects TEXT NOT NULL
   
);

--chunk size
CREATE TABLE IF NOT EXISTS chunks (
  chunk_id INTEGER PRIMARY KEY,
  doc_id   INTEGER NOT NULL,
  texts     TEXT NOT NULL,
  metadata TEXT,
  FOREIGN KEY(doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
);

 -- EMBEDDINGS
CREATE TABLE IF NOT EXISTS embeddings (
  chunk_id INTEGER PRIMARY KEY,
  dims     INTEGER NOT NULL,
  vec      BLOB NOT NULL,
  FOREIGN KEY(chunk_id) REFERENCES chunks(chunk_id) ON DELETE CASCADE
);


CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
USING fts5(chunk_id, doc_id, text, tokenize='unicode61');

CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
  INSERT INTO chunks_fts(rowid, chunk_id, doc_id, text)
  VALUES (new.rowid, new.chunk_id, new.doc_id, new.text);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
  INSERT INTO chunks_fts(chunks_fts, rowid, chunk_id, doc_id, text)
  VALUES('delete', old.rowid, old.chunk_id, old.doc_id, old.text);
END;

CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
  INSERT INTO chunks_fts(chunks_fts, rowid, chunk_id, doc_id, text)
  VALUES('delete', old.rowid, old.chunk_id, old.doc_id, old.text);
  INSERT INTO chunks_fts(rowid, chunk_id, doc_id, text)
  VALUES (new.rowid, new.chunk_id, new.doc_id, new.text);
END;