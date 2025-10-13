import { 
  signInWithPopup, 
  signOut, 
  onAuthStateChanged,
  getIdToken
} from 'firebase/auth';
import { auth, googleProvider } from './config';

class FirebaseAuthService {
  constructor() {
    this.user = null;
    this.listeners = [];
  }

  // Sign in with Google
  async signInWithGoogle() {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const user = result.user;
      
      // Get the ID token
      const idToken = await getIdToken(user);
      
      return {
        success: true,
        user: {
          uid: user.uid,
          email: user.email,
          displayName: user.displayName,
          photoURL: user.photoURL,
          idToken: idToken
        }
      };
    } catch (error) {
      console.error('Firebase sign-in error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Sign out
  async signOut() {
    try {
      await signOut(auth);
      return { success: true };
    } catch (error) {
      console.error('Firebase sign-out error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Get current user
  getCurrentUser() {
    return this.user;
  }

  // Get ID token
  async getIdToken() {
    if (this.user) {
      try {
        return await getIdToken(this.user);
      } catch (error) {
        console.error('Error getting ID token:', error);
        return null;
      }
    }
    return null;
  }

  // Listen to auth state changes
  onAuthStateChanged(callback) {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      this.user = user;
      callback(user);
      
      // Notify all listeners
      this.listeners.forEach(listener => {
        if (typeof listener === 'function') {
          listener(user);
        }
      });
    });

    return unsubscribe;
  }

  // Add auth state listener
  addAuthStateListener(callback) {
    this.listeners.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  // Verify ID token with backend
  async verifyTokenWithBackend(idToken) {
    try {
      const response = await fetch('/api/v1/auth/firebase-verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ idToken })
      });

      if (response.ok) {
        const data = await response.json();
        return {
          success: true,
          user: data.user,
          accessToken: data.access_token
        };
      } else {
        const error = await response.json();
        return {
          success: false,
          error: error.detail || 'Token verification failed'
        };
      }
    } catch (error) {
      console.error('Backend token verification error:', error);
      return {
        success: false,
        error: 'Network error'
      };
    }
  }
}

// Export singleton instance
export const firebaseAuth = new FirebaseAuthService();
export default firebaseAuth;
