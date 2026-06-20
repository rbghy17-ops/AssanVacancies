import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { verifyAdmin, loginAdmin, refreshAdmin } from '../lib/api';

const AuthContext = createContext(null);
const IDLE_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
const REFRESH_INTERVAL_MS = 10 * 60 * 1000; // refresh token every 10 min if user is active

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const lastActivityRef = useRef(Date.now());
  const idleTimerRef = useRef(null);
  const refreshTimerRef = useRef(null);

  const logout = useCallback((reason) => {
    localStorage.removeItem('av_admin_token');
    setUser(null);
    if (idleTimerRef.current) clearInterval(idleTimerRef.current);
    if (refreshTimerRef.current) clearInterval(refreshTimerRef.current);
    if (reason === 'idle' && window.location.pathname.startsWith('/admin') && window.location.pathname !== '/admin/login') {
      window.location.href = '/admin/login?idle=1';
    }
  }, []);

  const startIdleWatcher = useCallback(() => {
    if (idleTimerRef.current) clearInterval(idleTimerRef.current);
    if (refreshTimerRef.current) clearInterval(refreshTimerRef.current);

    lastActivityRef.current = Date.now();

    idleTimerRef.current = setInterval(() => {
      const idleFor = Date.now() - lastActivityRef.current;
      if (idleFor >= IDLE_TIMEOUT_MS) {
        logout('idle');
      }
    }, 30 * 1000); // check every 30s

    refreshTimerRef.current = setInterval(async () => {
      const idleFor = Date.now() - lastActivityRef.current;
      // Refresh only if user was active in the last 5 min
      if (idleFor < 5 * 60 * 1000) {
        try {
          const res = await refreshAdmin();
          if (res?.token) localStorage.setItem('av_admin_token', res.token);
        } catch {
          /* ignored */
        }
      }
    }, REFRESH_INTERVAL_MS);
  }, [logout]);

  useEffect(() => {
    const handler = () => { lastActivityRef.current = Date.now(); };
    ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'].forEach(e =>
      window.addEventListener(e, handler, { passive: true }),
    );
    return () => {
      ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'].forEach(e =>
        window.removeEventListener(e, handler),
      );
      if (idleTimerRef.current) clearInterval(idleTimerRef.current);
      if (refreshTimerRef.current) clearInterval(refreshTimerRef.current);
    };
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('av_admin_token');
    if (!token) { setLoading(false); return; }
    verifyAdmin()
      .then(d => { setUser(d); startIdleWatcher(); })
      .catch(() => localStorage.removeItem('av_admin_token'))
      .finally(() => setLoading(false));
  }, [startIdleWatcher]);

  const login = async (username, password) => {
    const res = await loginAdmin({ username, password });
    localStorage.setItem('av_admin_token', res.token);
    setUser({ username: res.username, must_reset: res.must_reset });
    startIdleWatcher();
    return res;
  };

  const updateMustReset = (val) => setUser(u => u ? { ...u, must_reset: val } : u);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, updateMustReset }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
