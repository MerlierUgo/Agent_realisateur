DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
create extension if not exists vector;

-- Créer la table messages pour la sauvegarde des conversations
CREATE TABLE IF NOT EXISTS messages (
  id bigserial primary key,
  session_id text NOT NULL,
  role text NOT NULL,
  content text NOT NULL,
  created_at timestamp default now()
);

-- Créer l'index sur session_id pour les requêtes rapides
CREATE INDEX IF NOT EXISTS messages_session_id_idx ON messages(session_id);

-- Activer RLS pour messages
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Autoriser les INSERT et SELECT pour messages
CREATE POLICY "Allow inserts on messages" ON messages
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow selects on messages" ON messages
  FOR SELECT USING (true);

-- Créer la table documents avec support vectoriel
CREATE TABLE IF NOT EXISTS documents (
  id bigserial primary key,
  content text NOT NULL,
  source text,
  embedding vector(768),
  created_at timestamp default now()
);

-- Activer RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Autoriser les INSERT
CREATE POLICY "Allow inserts" ON documents
  FOR INSERT WITH CHECK (true);

-- Autoriser les SELECT
CREATE POLICY "Allow selects" ON documents
  FOR SELECT USING (true);

-- NOTE: Index HNSW peut maintenant être utilisé car 768 < 2000 dimensions
-- La recherche sera rapide avec l'index vectoriel

-- Créer l'index HNSW pour les recherches vectorielles rapides
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
  ON documents USING hnsw (embedding vector_cosine_ops)
  WITH (m=16, ef_construction=64);

-- Créer la fonction RPC pour la recherche par similarité
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(768),
  match_count int DEFAULT 3,
  similarity_threshold float DEFAULT 0.5
)
RETURNS TABLE(
  id bigint,
  content text,
  source text,
  similarity float
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    documents.id,
    documents.content,
    documents.source,
    (1 - (documents.embedding <=> query_embedding)) as similarity
  FROM documents
  WHERE (1 - (documents.embedding <=> query_embedding)) > similarity_threshold
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
