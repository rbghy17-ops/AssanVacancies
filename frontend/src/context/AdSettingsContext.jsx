import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import api from '../lib/api';

const AdSettingsContext = createContext({
  adsEnabled: true,
  disabledPaths: [],
  loading: true,
  refresh: () => {},
});

const DEFAULT_SETTINGS = {
  adsEnabled: true,
  disabledPaths: ['/privacy', '/terms', '/disclaimer', '/contact'],
};

export const AdSettingsProvider = ({ children }) => {
  const [state, setState] = useState({ ...DEFAULT_SETTINGS, loading: true });

  const refresh = useCallback(async () => {
    try {
      const res = await api.get('/ads/settings');
      setState({
        adsEnabled: res.data.ads_enabled !== false,
        disabledPaths: Array.isArray(res.data.disabled_paths) ? res.data.disabled_paths : [],
        loading: false,
      });
    } catch {
      setState((s) => ({ ...s, loading: false }));
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  return (
    <AdSettingsContext.Provider value={{ ...state, refresh }}>
      {children}
    </AdSettingsContext.Provider>
  );
};

export const useAdSettings = () => useContext(AdSettingsContext);

/** Returns true if ads should render on the given pathname. */
export const isAdsAllowed = (settings, pathname) => {
  if (!settings || !settings.adsEnabled) return false;
  if (!pathname) return true;
  if (pathname.startsWith('/admin')) return false;
  return !(settings.disabledPaths || []).some((p) => pathname === p || pathname.startsWith(p + '/'));
};
