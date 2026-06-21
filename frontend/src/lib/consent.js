export const CONSENT_KEY = 'av_cookie_consent_v1';
export const CONSENT_EVENT = 'av:consent-change';

export const ACCEPTED = 'accepted';
export const REJECTED = 'rejected';

export const getConsent = () => {
  if (typeof window === 'undefined') return null;
  try { return localStorage.getItem(CONSENT_KEY) || null; }
  catch { return null; }
};

export const setConsent = (value) => {
  try {
    localStorage.setItem(CONSENT_KEY, value);
    window.dispatchEvent(new CustomEvent(CONSENT_EVENT, { detail: value }));
  } catch { /* ignore */ }
};

export const clearConsent = () => {
  try {
    localStorage.removeItem(CONSENT_KEY);
    window.dispatchEvent(new CustomEvent(CONSENT_EVENT, { detail: null }));
  } catch { /* ignore */ }
};

export const hasConsented = () => getConsent() === ACCEPTED;
export const hasResponded = () => getConsent() !== null;
