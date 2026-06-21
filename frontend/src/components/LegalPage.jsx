import React from 'react';
import SeoMeta from './SeoMeta';

/**
 * Reusable, accessible template for static informational pages (privacy,
 * terms, disclaimer, etc.). Reuses the site's existing typography — no new
 * visual design — with semantic HTML5 landmarks.
 */
const LegalPage = ({ title, subtitle, lastUpdated, seoDescription, children }) => (
  <div className="max-w-4xl mx-auto px-4 py-8">
    <SeoMeta title={title} description={seoDescription || subtitle} />
    <header className="bg-gradient-to-r from-purple-700 to-purple-900 text-white rounded-xl p-6 mb-6">
      <h1 className="text-2xl md:text-3xl font-extrabold title-font">{title}</h1>
      {subtitle && <p className="text-purple-100 text-sm mt-1">{subtitle}</p>}
      {lastUpdated && (
        <p className="text-purple-200 text-xs mt-2">
          Last updated: <time dateTime={lastUpdated}>{lastUpdated}</time>
        </p>
      )}
    </header>
    <article className="bg-white rounded-xl border border-purple-100 p-6 md:p-8">
      <div className="space-y-6 text-gray-800 leading-relaxed">
        {children}
      </div>
    </article>
  </div>
);

export const LegalSection = ({ heading, id, children }) => (
  <section id={id} aria-labelledby={id ? `${id}-h` : undefined}>
    <h2 id={id ? `${id}-h` : undefined} className="text-xl font-bold text-purple-900 mb-2 title-font">
      {heading}
    </h2>
    <div className="space-y-3">{children}</div>
  </section>
);

export const LegalList = ({ items }) => (
  <ul className="list-disc pl-6 space-y-1.5 text-gray-800">
    {items.map((it, i) => <li key={i}>{it}</li>)}
  </ul>
);

export default LegalPage;
