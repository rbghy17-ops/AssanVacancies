import React, { createContext, useContext, useEffect, useState } from 'react';
import { verifyAdmin, loginAdmin } from '../lib/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('av_admin_token');
    if (!token) { setLoading(false); return; }
    verifyAdmin()
      .then(d => setUser(d))
      .catch(() => localStorage.removeItem('av_admin_token'))
      .finally(() => setLoading(false));
  }, []);

  const login = async (username, password) => {
    const res = await loginAdmin({ username, password });
    localStorage.setItem('av_admin_token', res.token);
    setUser({ username: res.username });
    return res;
  };

  const logout = () => {
    localStorage.removeItem('av_admin_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
