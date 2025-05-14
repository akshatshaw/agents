import pandas as pd
import json
import asyncio
from typing import List, Dict, Any
df = pd.read_csv(r"nl2sql_agent\Copy of Schema_dump_(1)(1).csv")
    

SCHEMA_SAMPLES = {}
for table_name, group in df.groupby('table_name'):
    SCHEMA_SAMPLES[table_name] = {
        'columns': group['column_name'].tolist(),
        'description': f"Schema for {table_name} table",
        'column_details': group.to_dict(orient='records')
    }
    

SQL_SAMPLES = [
    {
        "question": "Find all users who registered in the last month",
        "sql": "SELECT user_id, name, email FROM users WHERE registration_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)"
    },
    {
        "question": "Count the number of orders by status",
        "sql": "SELECT status, COUNT(*) as count FROM orders GROUP BY status ORDER BY count DESC"
    },
    {
        "question": "Find the top 5 products by sales revenue",
        "sql": """
        SELECT p.product_id, p.name, SUM(o.quantity * o.price) as revenue
        FROM order_items o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_id, p.name
        ORDER BY revenue DESC
        LIMIT 5
        """
    }
]


CUSTOM_INSTRUCTIONS = """
When generating SQL queries, follow these guidelines:
• Include driver license details (license_number, issue_date, expiration_date)
• Format dates according to SQL standards (YYYY-MM-DD)
• Include vehicle registration details when relevant
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
    # Search for similar examples
    similar_examples = search_similar_examples(question, SQL_SAMPLES)
    
    # Get relevant tables
    relevant_tables = get_relevant_tables(question, SCHEMA_SAMPLES)
    
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
    for table_name, table_info in relevant_tables.items():
        prompt += f"### Table: {table_name}\n"
        prompt += f"Description: {table_info['description']}\n"
        prompt += "Columns:\n"
        for column in table_info['columns']:
            prompt += f"- {column}\n"
        prompt += "\n"
    
    # Add custom instructions
    prompt += "## Custom Instructions\n"
    prompt += CUSTOM_INSTRUCTIONS
    
    # Final instruction
    prompt += "\n\nGenerate a SQL query to answer the user's question based on the available schema and examples. Include an explanation of the query."
    
    return prompt

