CREATE INDEX IF NOT EXISTS idx_documents_grade_subject ON documents(grade, subject);
CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_dims ON embeddings(dims);
