import { createContext, useContext, useState, useEffect } from 'react';
import { login as loginApi } from '../api/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing authentication on mount
    const authData = localStorage.getItem('irop_auth');
    if (authData) {
      const { token, user } = JSON.parse(authData);
      setToken(token);
      setUser(user);
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const data = await loginApi(email, password);
      const { access_token } = data;
      
      // Store authentication data
      const authData = {
        token: access_token,
        user: { email } // We'll expand this when backend returns user info
      };
      
      localStorage.setItem('irop_auth', JSON.stringify(authData));
      setToken(access_token);
      setUser(authData.user);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('irop_auth');
    setToken(null);
    setUser(null);
  };

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};