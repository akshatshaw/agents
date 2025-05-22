import pandas as pd
import json
import asyncio
import os
from dotenv import load_dotenv
import psycopg2
from samples import SQL_SAMPLES
load_dotenv()
from typing import List, Dict, Any
# from vector_store import load_vector_store, build_and_save_vector_store, embedder
from pymongo import MongoClient
from openai import OpenAI

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "sql_agent"
COLLECTION_NAME = "test2"

host = os.getenv("host_pgsql")
password = os.getenv("password_pgsql")


# df = pd.read_csv("Final_schema.csv")
    
# # updated schema with table description 
# SCHEMA_SAMPLES = {}
# for table_name, group in df.groupby('table_name'):
#     description = group['Table description'].dropna().unique()
#     if len(description) > 0:
#         table_description = description[0]
#     else:
#         table_description = f"Schema for {table_name} table"
#     SCHEMA_SAMPLES[table_name] = {
#         'columns': group['column_name'].tolist(),
#         'description': table_description,
#         'column_details': group.to_dict(orient='records')
#     } 


CUSTOM_INSTRUCTIONS = """
When generating SQL queries, follow these guidelines:
• Format dates according to SQL standards (YYYY-MM-DD)
• Use proper table aliases for clarity
• Include comments explaining complex logic
• Follow best practices for SQL performance
• Use appropriate JOIN types (INNER, LEFT, RIGHT) based on the requirements
• Format the SQL query with proper indentation and line breaks for readability
"""

def search_similar_examples(question: str, samples: List[Dict[str, str]], top_k: int = 3) -> List[Dict[str, str]]:
    # Simplified implementation - just keyword matching
    # In a real implementation, use embeddings and cosine similarity
    results = []
    keywords = question.lower().split()
    
    for sample in samples:
        score = sum(1 for keyword in keywords if keyword in sample["question"].lower())
        if score > 0:
            results.append({"sample": sample, "score": score})
    
    # Sort by score and return top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return [item["sample"] for item in results[:top_k]]

def get_relevant_tables(question: str, schema: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
   
    relevant_tables = {}
    keywords = question.lower().split()
    
    for table_name, table_info in schema.items():
        # Check if table name is mentioned
        if table_name.lower() in question.lower():
            relevant_tables[table_name] = table_info
            continue
            
        # Check if any column is mentioned
        for column in table_info["columns"]:
            if column.lower() in question.lower():
                relevant_tables[table_name] = table_info
                break
                
        # Check for semantic matches (simplified)
        description_words = table_info["description"].lower().split()
        match_score = sum(1 for keyword in keywords if keyword in description_words)
        if match_score > 1:  # If multiple keywords match the description
            relevant_tables[table_name] = table_info
    
    # If no tables found, return top 2 most likely tables
    if not relevant_tables:
        table_scores = {}
        for table_name, table_info in schema.items():
            # Create a score based on column matches
            score = sum(1 for keyword in keywords for column in table_info["columns"] if keyword in column.lower())
            table_scores[table_name] = score
        
        # Get top 2 tables by score
        top_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)[:2]
        for table_name, _ in top_tables:
            relevant_tables[table_name] = schema[table_name]
    
    return relevant_tables

# Search example
# def search_relevant_tables(query: str, index, table_keys, top_k=3):
#     query_embedding = embedder.encode([query], normalize_embeddings=True)
#     D, I = index.search(query_embedding, top_k)
#     return [table_keys[i] for i in I[0]]

# this search includes the table description

def get_openai_embedding(text: str, model="text-embedding-ada-002") -> list:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def search_mongodb_tables(query: str, mongo_uri: str, db_name: str, collection_name: str, top_k: int = 5):
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Embed the query
    query_embedding = get_openai_embedding(query)

    # Perform vector search with $vectorSearch
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",  # The name of your Atlas vector index
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,     # Number of candidates to search over
                "limit": top_k
            }
        },
        {
            "$project": {
                "_id": 0,
                "table_name": 1,
                "data_type": 1,
                "description": 1,
                # "columns": 1,  # Add this line if you want to include columns
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    return results

# def search_relevant_tables(query: str, index, table_keys, top_k=3):
#     query_embedding = embedder.encode([query], normalize_embeddings=True)
#     D, I = index.search(query_embedding, top_k)
#     results = {table_keys[i]: SCHEMA_SAMPLES[table_keys[i]] for i in I[0]}
#     return results


def generate_system_prompt(question: str) -> str:
    """
    Generates a comprehensive system prompt for SQL query generation.

    Args:
        question (str): The natural language query to generate a system prompt for.

    Returns:
        str: A markdown-formatted system prompt containing:
             - User's original question
             - Similar SQL query examples
             - Relevant database schema information
             - Custom SQL generation instructions

    Process:
        1. Search for similar SQL query examples
        2. Identify relevant database tables
        3. Construct a detailed prompt with context and instructions

    Notes:
        The system prompt is designed to provide maximum context to 
        the SQL query generation model, improving the accuracy of 
        generated queries.

    Example:
        prompt = generate_system_prompt("Show active user accounts")
        # Returns a detailed markdown prompt with examples, schema, 
        # and instructions for generating a SQL query
    """
    
    # INDEX_PATH = 'table_index.faiss'
    # METADATA_PATH = 'table_keys.pkl'

    # # Check and build if necessary
    # if not (os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH)):
    #     print("Vector store files not found. Building and saving...")
    #     build_and_save_vector_store(SCHEMA_SAMPLES, INDEX_PATH, METADATA_PATH)
    # else:
    #     print("Vector store files already exist. Skipping build.")

    # # Load 
    # index, table_keys = load_vector_store('table_index.faiss', 'table_keys.pkl')

    # Search for similar examples
    similar_examples = search_similar_examples(question, SQL_SAMPLES)
    
    # Get relevant tables
    # relevant_tables = get_relevant_tables(question, SCHEMA_SAMPLES)
    relevant_tables =search_mongodb_tables(question, MONGO_URI, DB_NAME, COLLECTION_NAME, top_k=5)
    
    # Build the system prompt
    prompt = "# SQL Query Generation\n\n"
    prompt += f"## User Question\n{question}\n\n"
    
    # Add similar examples
    prompt += "## Similar SQL Examples\n"
    for i, example in enumerate(similar_examples, 1):
        prompt += f"### Example {i}\n"
        prompt += f"Question: {example['question']}\n"
        prompt += f"SQL: ```sql\n{example['sql']}\n```\n\n"
    
    # Add relevant schema information
    prompt += "## Relevant Database Schema\n"
    prompt += "_________________________\n"
    prompt += f"### Table, Description and Columns:\n"
    
    for items in relevant_tables:
        prompt += f"### Table, Description and Columns: {items['table_name']}\n"
        prompt += f"Description: {items['description']}\n"
        prompt += f"Data_type: {items['data_type']}\n"
        # for column in items['data_type']:
        #     prompt += f"- {column}\n"
        prompt += "\n"
    
    # Add custom instructions
    prompt += "## Custom Instructions\n"
    prompt += CUSTOM_INSTRUCTIONS
    
    # Final instruction
    prompt += "\n\nGenerate a SQL query to answer the user's question based on the available schema and examples. Include an explanation of the query."
    
    return prompt

def sql_response(sql_query: str)-> str:
    """
    Executes the sql query generated by LLM agent, and retrun the response from the PostgreSQL database.
    Args:
        sql_query (str): The sql query generated by LLM agent.

    Returns:
        str: The response from the PostgreSQL database.
    """
    conn = psycopg2.connect(
        host = host,
        port = "55145",
        dbname = "railway",
        user = "postgres",
        password = password
    )
    # Open cursor and execute SQL file
    with open('script_test.sql', 'w') as f:
        f.write(sql_query)
    try:
        with conn:
            with conn.cursor() as cursor:
                with open('script_test.sql', 'r') as f:
                    sql = f.read()
                    cursor.execute(sql)
                    response = (cursor.fetchall())
        print("SQL script executed successfully.")
        return response
    except Exception as e:
        print(f"Error executing SQL: {e}")
    finally:
        conn.close()

