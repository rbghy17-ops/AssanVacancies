import React from 'react';
import { Sparkles, Lock, Clock } from 'lucide-react';
import { Badge } from './ui/badge';
import { computeNoticeStatus } from '../lib/noticeStatus';

const URGENCY_STYLES = {
  green: 'bg-emerald-100 text-emerald-800 border border-emerald-200',
  amber: 'bg-amber-100 text-amber-800 border border-amber-200',
  red: 'bg-red-100 text-red-800 border border-red-200',
};

/**
 * Reusable lifecycle badge group used by both NoticeCard (listing) and
 * NoticeDetail (detail page). Renders:
 *   - "New" if posted within 72h
 *   - "Closed" if last_date has passed
 *   - "X days left" countdown for OPEN job-type notices (colour-coded)
 */
const NoticeStatusBadges = ({ notice, size = 'sm' }) => {
  const { isClosed, isNew, daysLeft, urgency } = computeNoticeStatus(notice);
  const sizeClass = size === 'lg' ? 'text-sm px-3 py-1' : 'text-xs px-2 py-0.5';

  return (
    <>
      {isNew && !isClosed && (
        <Badge className={`bg-purple-600 text-white border-0 ${sizeClass} font-semibold`}>
          <Sparkles className="w-3 h-3 mr-1" /> New
        </Badge>
      )}
      {isClosed && (
        <Badge className={`bg-gray-200 text-gray-700 border border-gray-300 ${sizeClass} font-semibold`}>
          <Lock className="w-3 h-3 mr-1" /> Closed
        </Badge>
      )}
      {!isClosed && urgency && daysLeft !== null && (
        <Badge className={`${URGENCY_STYLES[urgency]} ${sizeClass} font-semibold`}>
          <Clock className="w-3 h-3 mr-1" />
          {daysLeft === 0 ? 'Last day' : daysLeft === 1 ? '1 day left' : `${daysLeft} days left`}
        </Badge>
      )}
    </>
  );
};

export default NoticeStatusBadges;
