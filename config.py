import os 
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", 300))
    
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
    VECTOR_DB_PATH = 'vector_db'
    AWS_EC2_REGION = os.getenv("AWS_EC2_REGION")