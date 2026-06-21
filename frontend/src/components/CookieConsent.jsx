import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Cookie, X } from 'lucide-react';
import { Button } from './ui/button';
import { hasResponded, setConsent, ACCEPTED, REJECTED, CONSENT_EVENT } from '../lib/consent';

/**
 * Site-wide Cookie Consent banner shown on first visit.
 *
 * Until the visitor clicks Accept, the companion <ConsentScripts /> component
 * keeps Google AdSense and Google Analytics from being loaded — enforcement
 * happens at the script-injection layer, not just visually.
 */
const CookieConsent = () => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!hasResponded()) setVisible(true);
    const onChange = () => setVisible(!hasResponded());
    window.addEventListener(CONSENT_EVENT, onChange);
    return () => window.removeEventListener(CONSENT_EVENT, onChange);
  }, []);

  if (!visible) return null;

  const accept = () => { setConsent(ACCEPTED); setVisible(false); };
  const reject = () => { setConsent(REJECTED); setVisible(false); };

  return (
    <div
      role="dialog"
      aria-live="polite"
      aria-label="Cookie consent"
      className="fixed bottom-0 left-0 right-0 z-[60] bg-purple-950 text-white border-t border-purple-800 shadow-2xl"
    >
      <div className="max-w-7xl mx-auto px-4 py-4 flex flex-col md:flex-row md:items-center gap-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <div className="w-10 h-10 rounded-lg bg-purple-800 flex items-center justify-center flex-shrink-0">
            <Cookie className="w-5 h-5 text-purple-200" />
          </div>
          <div className="min-w-0">
            <h3 className="font-bold text-white">We value your privacy</h3>
            <p className="text-sm text-purple-100 mt-1">
              We use cookies and similar technologies to deliver content, serve ads via Google AdSense,
              and measure traffic with Google Analytics. These third-party scripts will only load after
              you accept. {' '}
              <Link to="/privacy" className="underline hover:text-white">Read our Privacy Policy</Link>.
            </p>
          </div>
        </div>
        <div className="flex gap-2 flex-shrink-0 self-end md:self-auto">
          <Button
            onClick={reject}
            variant="outline"
            className="border-purple-400 bg-transparent text-purple-100 hover:bg-purple-900 hover:text-white"
          >
            Reject non-essential
          </Button>
          <Button onClick={accept} className="bg-purple-600 hover:bg-purple-500 text-white">
            Accept all
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CookieConsent;
