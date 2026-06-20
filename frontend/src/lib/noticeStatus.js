/**
 * Single source of truth for notice lifecycle status, used by both the
 * listing template (NoticeCard) and the detail template (NoticeDetail).
 *
 * Mirrors backend `compute_status` so backend can filter out closed notices
 * from active listings while the URL stays live for SEO/archival.
 */

const HOURS_FOR_NEW = 72;
const MS_PER_DAY = 24 * 60 * 60 * 1000;

export const parseNoticeDate = (s) => {
  if (!s || typeof s !== 'string') return null;
  const d = new Date(s);
  if (!isNaN(d.getTime())) return d;
  // Fallback: try replacing dashes/slashes for common formats
  const cleaned = s.replace(/[-/]/g, ' ').trim();
  const d2 = new Date(cleaned);
  return isNaN(d2.getTime()) ? null : d2;
};

/**
 * @returns {{ status: 'open'|'closed', isClosed: boolean, isNew: boolean,
 *             daysLeft: number|null, urgency: 'green'|'amber'|'red'|null }}
 */
export const computeNoticeStatus = (notice) => {
  if (!notice) {
    return { status: 'open', isClosed: false, isNew: false, daysLeft: null, urgency: null };
  }
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  // Prefer backend-computed flag if present (more reliable for free-form dates)
  let isClosed = notice.is_closed === true;
  let daysLeft = typeof notice.days_left === 'number' ? notice.days_left : null;

  if (!isClosed && daysLeft === null) {
    const lastDate = parseNoticeDate(notice.last_date);
    if (lastDate) {
      const lastMidnight = new Date(lastDate.getFullYear(), lastDate.getMonth(), lastDate.getDate());
      const diffDays = Math.round((lastMidnight - today) / MS_PER_DAY);
      if (diffDays < 0) {
        isClosed = true;
      } else {
        daysLeft = diffDays;
      }
    }
  }

  // "New" badge: posted within last 72 hours
  let isNew = false;
  if (notice.posted_date) {
    const posted = new Date(notice.posted_date);
    if (!isNaN(posted.getTime())) {
      const hoursDiff = (now - posted) / (1000 * 60 * 60);
      isNew = hoursDiff >= 0 && hoursDiff <= HOURS_FOR_NEW;
    }
  }

  // Urgency colour, only for OPEN job-type notices
  let urgency = null;
  if (notice.type === 'job' && !isClosed && daysLeft !== null) {
    if (daysLeft > 7) urgency = 'green';
    else if (daysLeft >= 3) urgency = 'amber';
    else urgency = 'red';
  }

  return {
    status: isClosed ? 'closed' : 'open',
    isClosed,
    isNew,
    daysLeft,
    urgency,
  };
};
