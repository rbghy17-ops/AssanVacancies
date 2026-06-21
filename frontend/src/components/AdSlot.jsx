import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { X } from 'lucide-react';
import { useAdSettings, isAdsAllowed } from '../context/AdSettingsContext';
import { hasConsented, CONSENT_EVENT } from '../lib/consent';

/**
 * Single reusable ad slot.
 * Supported placements:
 *   - header         : full-width leaderboard above main content
 *   - sidebar        : tall medium rectangle in the sidebar (desktop only)
 *   - in-content     : medium rectangle dropped between listing items
 *   - mobile-sticky  : fixed bottom banner on phones only (dismissible)
 *
 * Renders nothing when:
 *   - The admin has disabled ads globally, or
 *   - The current path is on the admin-managed disabled list, or
 *   - For mobile-sticky: visitor hasn't given cookie consent yet, or has dismissed it.
 *
 * The real AdSense <ins> tag will only be wired up after AdSense approval;
 * until then the slot renders an inline labelled placeholder.
 */
const PLACEMENT_CLASSES = {
  header:        'w-full h-24 sm:h-28',
  sidebar:       'w-full aspect-[4/5] max-h-[600px]',
  'in-content':  'w-full h-36 sm:h-40',
  'mobile-sticky': 'h-16',
};

const PLACEMENT_LABEL = {
  header: 'Header Ad',
  sidebar: 'Sidebar Ad',
  'in-content': 'In-Content Ad',
  'mobile-sticky': 'Sticky Ad',
};

const AdSlot = ({ placement = 'in-content', className = '' }) => {
  const settings = useAdSettings();
  const loc = useLocation();
  const [dismissed, setDismissed] = useState(false);
  const [consented, setConsented] = useState(false);

  useEffect(() => {
    setConsented(hasConsented());
    const onChange = () => setConsented(hasConsented());
    window.addEventListener(CONSENT_EVENT, onChange);
    return () => window.removeEventListener(CONSENT_EVENT, onChange);
  }, []);

  if (settings.loading) return null;
  if (!isAdsAllowed(settings, loc.pathname)) return null;

  const sizeClass = PLACEMENT_CLASSES[placement] || PLACEMENT_CLASSES['in-content'];
  const label = PLACEMENT_LABEL[placement] || 'Advertisement';

  if (placement === 'mobile-sticky') {
    if (!consented || dismissed) return null;
    return (
      <div
        role="complementary"
        aria-label="Sticky advertisement"
        className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-purple-200 shadow-[0_-4px_12px_rgba(76,29,149,0.08)]"
      >
        <div className="relative flex items-center px-3 py-2">
          <div className={`flex-1 ${sizeClass} bg-gradient-to-br from-purple-50 to-purple-100 border border-dashed border-purple-300 rounded flex items-center justify-center`}>
            <span className="text-[10px] uppercase tracking-widest text-purple-500">Advertisement · Sticky</span>
          </div>
          <button
            type="button"
            onClick={() => setDismissed(true)}
            className="ml-2 w-7 h-7 rounded-full flex items-center justify-center bg-white border border-purple-200 text-purple-700 hover:bg-purple-50"
            aria-label="Dismiss advertisement"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    );
  }

  const wrapperClass = placement === 'sidebar' ? '' : 'my-4';
  return (
    <div
      role="complementary"
      aria-label={label}
      data-ad-placement={placement}
      className={`${wrapperClass} ${className}`}
    >
      <div className={`${sizeClass} bg-gradient-to-br from-purple-50 to-purple-100 border-2 border-dashed border-purple-300 rounded-lg flex flex-col items-center justify-center text-center px-3`}>
        <div className="text-[10px] uppercase tracking-widest text-purple-500">Advertisement</div>
        <div className="text-purple-400 text-xs mt-1">{label} — AdSense slot</div>
      </div>
    </div>
  );
};

export default AdSlot;
