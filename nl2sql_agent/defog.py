# !pip install defog
from defog import Defog
import os
from dotenv import load_dotenv
load_dotenv()
defog_key = os.environ['DEFOG_API_KEY']

# for redshift

YOUR_DB_CREDS = {"host": "YOUR_HOST", "port": 8080, "database": "YOUR_DATABASE_NAME", "user": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}

defog = Defog(defog_key, db_type="YOUR_DB_TYPE", db_creds=YOUR_DB_CREDS)
# you only need to do this once. your api key, database credentials, and db_type will be saved in a config file in your home directory for future use
 
# if your db_type is postgres or redshift, then db_creds should be {"host": "YOUR_HOST", "port": YOUR_PORT, "database": "YOUR_DATABASE_NAME", "user": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}
# if your db_type is mysql, then db_creds should be {"host": "YOUR_HOST", "database": "YOUR_DATABASE_NAME", "user": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}
# if your database type is Snowflake, then db_creds should be {"account": "YOUR_ACCOUNT", "warehouse": "YOUR_WAREHOUSE", "user": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}
# if your database type is Databricks, then db_creds should be {"server_hostname": "YOUR_SERVER_HOSTNAME", "access_token": "YOUR_ACCESS_TOKEN", "http_path": "YOUR_HTTP_PATH"}
# if your database type is SQLServer, then db_creds should be {"server": "YOUR_SERVER", "database": "YOUR_DATABASE", "user": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}
# if your database type is Bigquery, then db_creds should be {"json_key_path": "/path/to/your/service_accoun_key.json"}
 
# defog = Defog()
 
defog.run_query(
  question="What is the average revenue by region?",
  previous_context=None
)