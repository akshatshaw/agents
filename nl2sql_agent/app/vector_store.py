# import faiss
# import pickle
# from sentence_transformers import SentenceTransformer

# embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", token=False)

# def build_and_save_vector_store(schema: dict, index_path: str, metadata_path: str):
#     texts = []
#     table_keys = []
    
#     for table_name, table_info in schema.items():
#         text_blob = f"{table_name}. {table_info['description']}. {' '.join(table_info['columns'])}"
#         texts.append(text_blob)
#         table_keys.append(table_name)
    
#     embeddings = embedder.encode(texts, normalize_embeddings=True)
#     dimension = embeddings.shape[1]
#     index = faiss.IndexFlatIP(dimension)
#     index.add(embeddings)
    
#     # Save FAISS index
#     faiss.write_index(index, index_path)
    
#     # Save table_keys
#     with open(metadata_path, 'wb') as f:
#         pickle.dump(table_keys, f)

# def load_vector_store(index_path: str, metadata_path: str):
#     index = faiss.read_index(index_path)
#     with open(metadata_path, 'rb') as f:
#         table_keys = pickle.load(f)
#     return index, table_keys


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

from openai import OpenAI
import numpy as np
from pymongo import MongoClient
from typing import Dict
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
df = pd.read_csv("Final_schema.csv")

# for now i am taking only 1343 tables, as others do not have the description yet
df = df[:1343]
    
# updated schema with table description 
SCHEMA_SAMPLES = {}
for table_name, group in df.groupby('table_name'):
    description = group['Table description'].dropna().unique()
    if len(description) > 0:
        table_description = description[0]
    else:
        table_description = f"Schema for {table_name} table"
    SCHEMA_SAMPLES[table_name] = {
        'columns': group['column_name'].tolist(),
        'description': table_description,
        'column_details': group.to_dict(orient='records')
    } 


# Make sure your OpenAI API key is set
# openai.api_key = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "sql_agent"
COLLECTION_NAME = "test1"


def get_openai_embedding(text: str, model="text-embedding-ada-002") -> list:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def build_and_save_vector_store(schema: Dict, mongo_uri: str, db_name: str, collection_name: str):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Optional: clear previous entries
    collection.delete_many({})

    for table_name, table_info in schema.items():
        text_blob = f"{table_name}. {table_info['description']}. {' '.join(table_info['columns'])}"
        embedding = get_openai_embedding(text_blob)

        document = {
            "table_name": table_name,
            "description": table_info['description'],
            "columns": table_info['columns'],
            "embedding": embedding
        }

        collection.insert_one(document)

    print("Vector store built and stored in MongoDB.")

if __name__== "__main__":
    build_and_save_vector_store(SCHEMA_SAMPLES, MONGO_URI, DB_NAME, COLLECTION_NAME)
