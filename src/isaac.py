from flask import Flask, request, jsonify, session
from firebase_admin import credentials, auth, firestore, initialize_app, get_app, delete_app
import os
from dotenv import load_dotenv
import pyrebase

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        load_dotenv()
        self.app = Flask(__name__)
        
        # Initialize Firebase Admin SDK with app check
        try:
            # Check if any Firebase app exists
            try:
                existing_app = get_app()
                delete_app(existing_app)
                print("Cleaned up existing Firebase app")
            except ValueError:
                pass  # No existing app

            self.cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
            })

            self.firebase_app = initialize_app(self.cred, name='cutiehacks2024')
            self.db = firestore.client(app=self.firebase_app)

        except Exception as e:
            print(f"Error during Firebase Admin SDK initialization: {str(e)}")
            raise

        # Initialize Firebase for client-side operations
        try:
            self.firebase_config = {
                "apiKey": os.getenv("FIREBASE_API_KEY"),
                "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
                "projectId": os.getenv("FIREBASE_PROJECT_ID"),
                "databaseURL": "",
                "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
                "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
                "appId": os.getenv("FIREBASE_APP_ID")
            }

            self.firebase = pyrebase.initialize_app(self.firebase_config)
            self.auth = self.firebase.auth()

        except Exception as e:
            print(f"Error during Firebase client initialization: {str(e)}")
            raise

        # Initialize user IDs list
        self.user_ids = []
        try:
            accounts_ref = self.db.collection('accounts')
            accounts = accounts_ref.stream()
            self.user_ids = [account.id for account in accounts]
        except Exception as e:
            print(f"Warning: Error retrieving user IDs: {e}")

        self._initialized = True

    def add_user_to_firestore(self, user_data):
        """Add user information to Firestore."""
        try:
            accounts_ref = self.db.collection('accounts')
            
            account_data = {
                'Username': user_data.get('username'),
                'Password': '**HASHED**',  # Password is handled by Firebase Auth
                'IsCompany': user_data.get('is_company', False),
                'companyName': user_data.get('company_name', '') if user_data.get('is_company') else '',
                'region': user_data.get('region', ''),
                'ID': user_data['uid'],
                'RequestIDsAccepted': [],
                'accountBal': 0.0,
                'email': user_data['email']
            }
            
            accounts_ref.document(user_data['uid']).set(account_data)
            self.user_ids.append(user_data['uid'])
            return True
        except Exception as e:
            print(f"Error adding user to Firestore: {e}")
            return False

    def authenticate_user(self, email, password):
        """Authenticate user with email and password."""
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            account_doc = self.db.collection('accounts').document(user['localId']).get()
            
            if account_doc.exists:
                return {
                    'user': user,
                    'account': account_doc.to_dict()
                }
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None

    def register_user(self, email, password, additional_data):
        """Register new user with email and password."""
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            user_data = {
                "uid": user['localId'],
                "email": email,
                **additional_data
            }
            if self.add_user_to_firestore(user_data):
                return self.authenticate_user(email, password)
            return None
        except Exception as e:
            print(f"Error registering user: {e}")
            return None

# Example usage

if __name__ == "__main__":
   
    db = Database()

    # Register a company account
    try:
        company_data = {
            'username': 'CompanyXYZ',
            'is_company': True,
            'company_name': 'Company XYZ Ltd',
            'region': 'US-West'
        }
        result = db.register_user('company@example.com', 'secure_password', company_data)
    except Exception as e:
        print(f"Registration error: {e}")

    # Register a customer account
    try:
        customer_data = {
            'username': 'JohnDoe',
            'is_company': False,
            'region': 'US-East'
        }
        result = db.register_user('customer@example.com', 'secure_password', customer_data)
    except Exception as e:
        print(f"Registration error: {e}")

    # Authenticate user
    auth_result = db.authenticate_user('company@example.com', 'secure_password')
    if auth_result:
        print(f"Logged in as: {auth_result['account']['Username']}")