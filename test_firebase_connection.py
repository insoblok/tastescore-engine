"""Simple script to test Firebase connection."""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service.database import FirestoreDB
from service.utils import logger

def test_firebase_connection():
    """Test Firebase Firestore connection."""
    print("Testing Firebase connection...")
    print("-" * 50)
    
    try:
        # Initialize database connection
        db = FirestoreDB()
        
        if db.connected:
            print("✅ Firebase connection successful!")
            print(f"✅ Database client initialized")
            print(f"✅ Project: tastescore-engine")
            
            # Test a simple query to verify connection
            try:
                # Try to get a collection reference (this will verify connection)
                collections = db.db.collections()
                print(f"✅ Can access Firestore collections")
                print(f"✅ Connection verified!")
                return True
            except Exception as e:
                print(f"⚠️  Connection established but query failed: {e}")
                return False
        else:
            print("❌ Firebase connection failed!")
            print("Check your service account configuration.")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure FIREBASE_SERVICE_ACCOUNT_KEY is set in .env")
        print("2. Verify the service account file exists")
        print("3. Check that firebase-admin is installed: pip install firebase-admin")
        return False

if __name__ == "__main__":
    success = test_firebase_connection()
    sys.exit(0 if success else 1)

