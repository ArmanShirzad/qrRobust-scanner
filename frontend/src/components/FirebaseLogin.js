import React, { useState } from 'react';
import { Chrome } from 'lucide-react';
import { firebaseAuth } from '../firebase/auth';
import toast from 'react-hot-toast';

const FirebaseLogin = ({ onSuccess, onError }) => {
  const [loading, setLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setLoading(true);
    
    try {
      // Sign in with Firebase
      const firebaseResult = await firebaseAuth.signInWithGoogle();
      
      if (!firebaseResult.success) {
        throw new Error(firebaseResult.error);
      }

      // Verify token with backend
      const backendResult = await firebaseAuth.verifyTokenWithBackend(firebaseResult.user.idToken);
      
      if (!backendResult.success) {
        throw new Error(backendResult.error);
      }

      // Store tokens
      localStorage.setItem('access_token', backendResult.accessToken);
      localStorage.setItem('firebase_user', JSON.stringify(firebaseResult.user));
      
      toast.success('Signed in successfully!');
      
      if (onSuccess) {
        onSuccess(backendResult.user);
      }
      
    } catch (error) {
      console.error('Firebase login error:', error);
      toast.error(error.message || 'Login failed');
      
      if (onError) {
        onError(error);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleGoogleSignIn}
      disabled={loading}
      className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {loading ? (
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600"></div>
      ) : (
        <>
          <Chrome className="h-5 w-5 mr-2" />
          Continue with Google
        </>
      )}
    </button>
  );
};

export default FirebaseLogin;
