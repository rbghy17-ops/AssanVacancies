import { useEffect } from 'react';
import { CONSENT_EVENT, hasConsented } from '../lib/consent';

/**
 * Conditionally injects Google Analytics and Google AdSense scripts ONLY when
 * the visitor has accepted cookies. Removes them on rejection / revocation.
 *
 * Replace the placeholder IDs below with your real GA Measurement ID and
 * AdSense Publisher ID when going to production. Until they're real, the
 * scripts won't fire (the guards block placeholder values).
 */
const GA_MEASUREMENT_ID = 'G-FE564JMZFY';                      // AssamVacancies.com GA4 property
const ADSENSE_CLIENT_ID = 'ca-pub-XXXXXXXXXXXXXXXX';           // e.g., 'ca-pub-1234567890123456'
const MANAGED_ATTR = 'data-av-managed';

const isPlaceholder = (id) => !id || id.includes('XXXXXX');

const loadScript = (src, attrs = {}) => {
  if (document.querySelector(`script[${MANAGED_ATTR}="${src}"]`)) return;
  const s = document.createElement('script');
  s.src = src;
  s.async = true;
  s.setAttribute(MANAGED_ATTR, src);
  Object.entries(attrs).forEach(([k, v]) => s.setAttribute(k, v));
  document.head.appendChild(s);
};

const removeManagedScripts = () => {
  document.querySelectorAll(`script[${MANAGED_ATTR}]`).forEach((s) => s.remove());
  // Clear globals so they can't be used by accident
  try {
    if (window.dataLayer) window.dataLayer = [];
    delete window.gtag;
    delete window.adsbygoogle;
  } catch { /* ignore */ }
};

const initGA = (id) => {
  loadScript(`https://www.googletagmanager.com/gtag/js?id=${id}`);
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag('js', new Date());
  gtag('config', id, { anonymize_ip: true });
};

const initAdSense = (clientId) => {
  loadScript(
    `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${clientId}`,
    { crossorigin: 'anonymous' },
  );
};

const ConsentScripts = () => {
  useEffect(() => {
    const apply = () => {
      if (hasConsented()) {
        if (!isPlaceholder(GA_MEASUREMENT_ID)) initGA(GA_MEASUREMENT_ID);
        if (!isPlaceholder(ADSENSE_CLIENT_ID)) initAdSense(ADSENSE_CLIENT_ID);
      } else {
        removeManagedScripts();
      }
    };
    apply();
    window.addEventListener(CONSENT_EVENT, apply);
    return () => window.removeEventListener(CONSENT_EVENT, apply);
  }, []);
  return null;
};

export default ConsentScripts;
