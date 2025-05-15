import faiss
import pickle
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", token=False)

def build_and_save_vector_store(schema: dict, index_path: str, metadata_path: str):
    texts = []
    table_keys = []
    
    for table_name, table_info in schema.items():
        text_blob = f"{table_name}. {table_info['description']}. {' '.join(table_info['columns'])}"
        texts.append(text_blob)
        table_keys.append(table_name)
    
    embeddings = embedder.encode(texts, normalize_embeddings=True)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    # Save FAISS index
    faiss.write_index(index, index_path)
    
    # Save table_keys
    with open(metadata_path, 'wb') as f:
        pickle.dump(table_keys, f)

def load_vector_store(index_path: str, metadata_path: str):
    index = faiss.read_index(index_path)
    with open(metadata_path, 'rb') as f:
        table_keys = pickle.load(f)
    return index, table_keys


# build_and_save_vector_store(SCHEMA_SAMPLES, 'table_index.faiss', 'table_keys.pkl')

# # Load (anytime later)
# index, table_keys = load_vector_store('table_index.faiss', 'table_keys.pkl')

# # Search example
# def search_relevant_tables(query: str, index, table_keys, top_k=3):
#     query_embedding = embedder.encode([query], normalize_embeddings=True)
#     D, I = index.search(query_embedding, top_k)
#     return [table_keys[i] for i in I[0]]

# query = "customer payment history"
# relevant_tables = search_relevant_tables(query, index, table_keys)
# print("Relevant tables:", relevant_tables)