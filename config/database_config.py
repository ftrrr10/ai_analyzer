"""
Database Configuration Module
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

class SupabaseConfig:
    """Supabase configuration and client initialization"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Missing Supabase credentials in environment variables")
        
        self.client: Client = create_client(self.url, self.key)
        self.admin_client: Client = create_client(self.url, self.service_key) if self.service_key else None
    
    def get_client(self, use_admin=False) -> Client:
        """Get Supabase client"""
        if use_admin and self.admin_client:
            return self.admin_client
        return self.client
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            response = self.client.table('complaints').select("count", count='exact').limit(1).execute()
            print("✓ Supabase connection successful")
            return True
        except Exception as e:
            print(f"✗ Supabase connection failed: {e}")
            return False

# Global instance
supabase_config = SupabaseConfig()
supabase = supabase_config.get_client()
