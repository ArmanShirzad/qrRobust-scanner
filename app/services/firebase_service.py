import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from app.core.config import settings
import os

class FirebaseService:
    def __init__(self):
        self.app = None
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                self.app = firebase_admin.get_app()
                return

            # Initialize Firebase Admin SDK
            # Option 1: Use service account key file
            if os.path.exists('firebase-service-account.json'):
                cred = credentials.Certificate('firebase-service-account.json')
                self.app = firebase_admin.initialize_app(cred)
                return

            # Option 2: Use environment variables (for production)
            firebase_config = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL')}"
            }

            # Check if all required environment variables are present
            if all(firebase_config.values()):
                cred = credentials.Certificate(firebase_config)
                self.app = firebase_admin.initialize_app(cred)
                return

            # Option 3: Use default credentials (for local development with gcloud)
            try:
                self.app = firebase_admin.initialize_app()
                return
            except Exception:
                pass

            # If all methods fail, raise an error
            raise Exception("Firebase initialization failed. Please provide service account credentials.")

        except Exception as e:
            print(f"Firebase initialization error: {e}")
            # For development, you can continue without Firebase
            # In production, you might want to raise the exception
            self.app = None

    def verify_id_token(self, id_token):
        """Verify Firebase ID token"""
        if not self.app:
            raise Exception("Firebase not initialized")

        try:
            # Verify the ID token
            decoded_token = firebase_auth.verify_id_token(id_token)
            return {
                'success': True,
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'email_verified': decoded_token.get('email_verified', False)
            }
        except firebase_auth.InvalidIdTokenError:
            return {'success': False, 'error': 'Invalid ID token'}
        except firebase_auth.ExpiredIdTokenError:
            return {'success': False, 'error': 'Expired ID token'}
        except Exception as e:
            return {'success': False, 'error': f'Token verification failed: {str(e)}'}

    def get_user_by_uid(self, uid):
        """Get user information by UID"""
        if not self.app:
            raise Exception("Firebase not initialized")

        try:
            user = firebase_auth.get_user(uid)
            return {
                'success': True,
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'photo_url': user.photo_url,
                'email_verified': user.email_verified,
                'disabled': user.disabled
            }
        except firebase_auth.UserNotFoundError:
            return {'success': False, 'error': 'User not found'}
        except Exception as e:
            return {'success': False, 'error': f'Failed to get user: {str(e)}'}

    def create_custom_token(self, uid, additional_claims=None):
        """Create a custom token for a user"""
        if not self.app:
            raise Exception("Firebase not initialized")

        try:
            custom_token = firebase_auth.create_custom_token(uid, additional_claims)
            return {
                'success': True,
                'custom_token': custom_token.decode('utf-8')
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to create custom token: {str(e)}'}

# Export singleton instance
firebase_service = FirebaseService()
