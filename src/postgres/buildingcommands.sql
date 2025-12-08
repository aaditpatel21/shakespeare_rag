
-- Create Table for shakespeare plays embedded for RAG
CREATE TABLE IF NOT EXISTS shakespeare_embeddings (

    id SERIAL PRIMARY KEY,
    play_name varchar(255),
    content TEXT,
    embedding vector(384)

)

-- Create HNSW index for speed
CREATE INDEX IF NOT EXISTS idx_shakespeare_hybrid
on shakespeare_embeddings using hnsw(embedding vector_cosine_ops);

--set max limit of HNSW search to 200
ALTER DATABASE postgres SET hnsw.ef_search = 400;

--ALTER Table shakespeare_embeddings add column meta_data JSONB

select count( id) from shakespeare_embeddings --where meta_data ->> 'act' = 'Sonnet';

--TRUNCATE TABLE shakespeare_embeddings RESTART IDENTITY;

select * from shakespeare_embeddings
--where meta_data ->> 'chunk_num_in_scene' in ('1','5','10')
order by random()
LIMIT 100;

--Add text search vector that is auto generated for each row
ALTER TABLE shakespeare_embeddings ADD COLUMN if not exists text_search tsvector
Generated always as (to_tsvector('english',play_name || ' ' || content)) STORED;


-- create Generalized Inverted Index (GIN) 
Create index if not exists idx_keyword_search
on shakespeare_embeddings using GIN(text_search)

