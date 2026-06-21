import { useEffect } from 'react';
import api from '../lib/api';

/**
 * Fetches the Google Search Console verification token once at app start
 * and injects <meta name="google-site-verification" content="..."> into
 * <head>. Admin can update the token via the admin dashboard; the change
 * takes effect on the next page reload.
 */
const SiteVerification = () => {
  useEffect(() => {
    let cancelled = false;
    api.get('/site/verification')
      .then((res) => {
        if (cancelled) return;
        const token = (res.data && res.data.google_site_verification) || '';
        let el = document.head.querySelector('meta[name="google-site-verification"]');
        if (token) {
          if (!el) {
            el = document.createElement('meta');
            el.setAttribute('name', 'google-site-verification');
            document.head.appendChild(el);
          }
          el.setAttribute('content', token);
        } else if (el) {
          el.remove();
        }
      })
      .catch(() => { /* silently ignore — non-critical */ });
    return () => { cancelled = true; };
  }, []);
  return null;
};

export default SiteVerification;
