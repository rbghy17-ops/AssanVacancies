import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const SITE_NAME = 'AssamVacancies.com';

const upsertMeta = (selector, attrs) => {
  let el = document.head.querySelector(selector);
  if (!el) {
    el = document.createElement('meta');
    document.head.appendChild(el);
  }
  Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
  return el;
};

const upsertLink = (rel, href) => {
  let el = document.head.querySelector(`link[rel="${rel}"]`);
  if (!el) {
    el = document.createElement('link');
    el.setAttribute('rel', rel);
    document.head.appendChild(el);
  }
  el.setAttribute('href', href);
  return el;
};

const setJsonLd = (id, data) => {
  let el = document.getElementById(id);
  if (data) {
    if (!el) {
      el = document.createElement('script');
      el.setAttribute('type', 'application/ld+json');
      el.id = id;
      document.head.appendChild(el);
    }
    el.textContent = JSON.stringify(data);
  } else if (el) {
    el.remove();
  }
};

const parseToIso = (s) => {
  if (!s) return null;
  const d = new Date(s);
  if (isNaN(d.getTime())) return null;
  return d.toISOString().split('T')[0];
};

const clip = (s, max) => (s && s.length > max ? s.slice(0, max - 3).trimEnd() + '...' : s || '');

const buildNoticeDescription = (notice) => {
  let desc = '';
  // Avoid duplicating organization name if the title already starts with it
  const orgPrefix = notice.organization && !notice.title.toLowerCase().startsWith(notice.organization.toLowerCase())
    ? `${notice.organization}: `
    : '';
  if (notice.type === 'job') {
    const parts = [];
    if (notice.vacancy_count) parts.push(`${notice.vacancy_count} vacancies`);
    if (notice.eligibility) {
      const elig = notice.eligibility.split(/[,.]/)[0].trim();
      parts.push(`Eligibility: ${elig}`);
    }
    if (notice.last_date) parts.push(`Last date ${notice.last_date}`);
    desc = `${orgPrefix}${notice.title} \u2014 ${parts.join(', ')}.`;
  } else {
    const dateText = notice.notice_date ? `Released ${notice.notice_date}` : 'Now available';
    desc = `${orgPrefix}${notice.title}. ${dateText}. Download official ${notice.type.replace('_', ' ')} on ${SITE_NAME}.`;
  }
  // Trim to 160
  if (desc.length > 160) desc = clip(desc, 160);
  // Pad to 150 with overview text
  if (desc.length < 150 && notice.description) {
    const padding = ' ' + notice.description.replace(/\s+/g, ' ').trim();
    desc = (desc + padding).slice(0, 160);
  }
  return desc;
};

const buildJobPostingJsonLd = (notice, origin, pagePath) => {
  return {
    '@context': 'https://schema.org/',
    '@type': 'JobPosting',
    title: notice.title,
    description: notice.description,
    datePosted: notice.posted_date,
    validThrough: parseToIso(notice.last_date) || undefined,
    employmentType: 'FULL_TIME',
    hiringOrganization: {
      '@type': 'Organization',
      name: notice.organization,
      sameAs: notice.official_website || undefined,
    },
    jobLocation: {
      '@type': 'Place',
      address: {
        '@type': 'PostalAddress',
        addressLocality: notice.district || 'Guwahati',
        addressRegion: 'Assam',
        addressCountry: 'IN',
      },
    },
    url: `${origin}${pagePath}`,
    identifier: {
      '@type': 'PropertyValue',
      name: notice.organization,
      value: notice.id,
    },
  };
};

/**
 * Single, reusable SEO layer applied to every Notice page (and other public pages).
 * Pass either `notice` (for detail/listing where data is loaded) OR explicit title/description.
 *
 * - <title>:                  "{title} {organization} — Last Date {lastDate} | {SiteName}"
 * - <meta description>:       150-160 chars from vacancy/eligibility/last_date
 * - JSON-LD JobPosting:       only when notice.type === 'job'
 * - Open Graph + Twitter:     on every page
 * - <link rel="canonical">:   strips filter/query params (uses pathname only)
 */
const SeoMeta = ({ notice, title, description, image, ogType = 'website' }) => {
  const loc = useLocation();

  useEffect(() => {
    const origin = window.location.origin;
    let docTitle, metaDesc, finalOgType = ogType, finalImage = image, jsonLd = null;

    if (notice) {
      const dateLabel = notice.last_date || notice.notice_date || '';
      const lastDatePart = dateLabel ? ` — Last Date ${dateLabel}` : '';
      docTitle = `${notice.title} ${notice.organization}${lastDatePart} | ${SITE_NAME}`;
      docTitle = clip(docTitle, 70);
      metaDesc = buildNoticeDescription(notice);
      finalOgType = 'article';
      finalImage = image || notice.thumbnail || '';
      if (notice.type === 'job') {
        jsonLd = buildJobPostingJsonLd(notice, origin, loc.pathname);
      }
    } else {
      docTitle = title ? `${title} | ${SITE_NAME}` : `${SITE_NAME} — Jobs, Admit Card, Result & Answer Key in Assam`;
      docTitle = clip(docTitle, 70);
      metaDesc = description || 'Latest government & private jobs, admit cards, results and answer keys for all 35 districts of Assam. Verified updates daily.';
      if (metaDesc.length > 160) metaDesc = clip(metaDesc, 160);
    }

    document.title = docTitle;
    upsertMeta('meta[name="description"]', { name: 'description', content: metaDesc });
    upsertMeta('meta[name="robots"]', { name: 'robots', content: 'index, follow, max-image-preview:large' });

    // Open Graph
    upsertMeta('meta[property="og:title"]', { property: 'og:title', content: docTitle });
    upsertMeta('meta[property="og:description"]', { property: 'og:description', content: metaDesc });
    upsertMeta('meta[property="og:type"]', { property: 'og:type', content: finalOgType });
    upsertMeta('meta[property="og:site_name"]', { property: 'og:site_name', content: SITE_NAME });
    upsertMeta('meta[property="og:url"]', { property: 'og:url', content: `${origin}${loc.pathname}` });
    upsertMeta('meta[property="og:locale"]', { property: 'og:locale', content: 'en_IN' });
    if (finalImage) {
      upsertMeta('meta[property="og:image"]', { property: 'og:image', content: finalImage });
      upsertMeta('meta[property="og:image:alt"]', { property: 'og:image:alt', content: docTitle });
    }

    // Twitter Card
    upsertMeta('meta[name="twitter:card"]', { name: 'twitter:card', content: finalImage ? 'summary_large_image' : 'summary' });
    upsertMeta('meta[name="twitter:title"]', { name: 'twitter:title', content: docTitle });
    upsertMeta('meta[name="twitter:description"]', { name: 'twitter:description', content: metaDesc });
    upsertMeta('meta[name="twitter:site"]', { name: 'twitter:site', content: '@AssamVacancies' });
    if (finalImage) {
      upsertMeta('meta[name="twitter:image"]', { name: 'twitter:image', content: finalImage });
    }

    // Canonical — strips ALL query params and trailing slashes
    upsertLink('canonical', `${origin}${loc.pathname}`);

    // JSON-LD JobPosting (only for type=job)
    setJsonLd('jsonld-jobposting', jsonLd);
  }, [notice, title, description, image, ogType, loc.pathname]);

  return null;
};

export default SeoMeta;
