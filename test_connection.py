"""
Test Supabase Connection
"""
from dotenv import load_dotenv
load_dotenv()

from config.database_config import supabase_config

# Test connection
if supabase_config.test_connection():
    print("\n✅ Connection successful!")
    print(f"Connected to: {supabase_config.url}")
else:
    print("\n❌ Connection failed!")
    print("Check your .env file and Supabase credentials")
