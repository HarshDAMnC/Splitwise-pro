import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

_db = None

def get_db():
    global _db
    if _db is not None:
        return _db
        
    try:
        # We try to initialize with the default service account key path
        # Assuming the user places a serviceAccountKey.json at the root of backend
        key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'serviceAccountKey.json')
        
        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            # Check if already initialized (when importing multiple times in CLI vs Flask)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            _db = firestore.client()
            print("Firebase initialized securely.")
        else:
            print("WARNING: serviceAccountKey.json not found! Running in memory/mock mode unsupported directly, but continuing anyway. Add your key!")
            print(f"Looked in: {key_path}")
            # Could set up a local mock dict _db here if really needed, but keeping it strict to show Firebase design.
            _db = "MOCK_DB_MISSING_KEY"
            
    except Exception as e:
        print(f"Firebase initialization failed: {str(e)}")
        
    return _db
