import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, MapPin, Users, Eye, Download, FileText } from 'lucide-react';
import { Badge } from './ui/badge';
import NoticeStatusBadges from './NoticeStatusBadges';
import { computeNoticeStatus } from '../lib/noticeStatus';
import { SECTION_BY_TYPE } from '../lib/constants';

const CAT_COLORS = {
  govt: 'bg-purple-100 text-purple-800',
  defence: 'bg-emerald-100 text-emerald-800',
  railway: 'bg-blue-100 text-blue-800',
  banking: 'bg-amber-100 text-amber-800',
  teaching: 'bg-pink-100 text-pink-800',
  police: 'bg-red-100 text-red-800',
  private: 'bg-slate-100 text-slate-800',
};

const NoticeCard = ({ notice }) => {
  const section = SECTION_BY_TYPE[notice.type] || { label: notice.type };
  const dateStr = notice.posted_date ? new Date(notice.posted_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '';
  const isJob = notice.type === 'job';
  const { isClosed } = computeNoticeStatus(notice);

  return (
    <article className={`job-card bg-white rounded-xl border border-purple-100 overflow-hidden ${isClosed ? 'opacity-75' : ''}`}>
      <div className="flex flex-col md:flex-row">
        <div className="md:w-48 md:flex-shrink-0 h-44 md:h-auto bg-purple-50 relative">
          {notice.thumbnail
            ? <img src={notice.thumbnail} alt={notice.title} className={`w-full h-full object-cover ${isClosed ? 'grayscale' : ''}`} loading="lazy" />
            : <div className="w-full h-full flex items-center justify-center"><FileText className="w-12 h-12 text-purple-300" /></div>}
        </div>
        <div className="p-5 flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge className={`${CAT_COLORS[notice.category] || 'bg-gray-100 text-gray-800'} border-0 capitalize`}>{notice.category}</Badge>
            <Badge variant="outline" className="border-purple-200 text-purple-700">{section.label}</Badge>
            {notice.is_featured && !isClosed && <Badge className="bg-purple-600 text-white border-0">Featured</Badge>}
            <NoticeStatusBadges notice={notice} />
          </div>
          <Link to={`/notice/${notice.id}`}>
            <h2 className="text-lg md:text-xl font-bold text-purple-900 hover:text-purple-700 leading-snug">{notice.title}</h2>
          </Link>
          <p className="text-sm text-gray-600 mt-2 line-clamp-2">{notice.description}</p>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-xs text-gray-600">
            {isJob && notice.vacancy_count && <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5 text-purple-600" /> {notice.vacancy_count} posts</span>}
            {notice.district && <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-purple-600" /> {notice.district}</span>}
            {isJob && notice.last_date && <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5 text-purple-600" /> Last: {notice.last_date}</span>}
            {!isJob && notice.notice_date && <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5 text-purple-600" /> Notice: {notice.notice_date}</span>}
            {!isJob && notice.download_link && <span className="flex items-center gap-1 text-purple-700"><Download className="w-3.5 h-3.5" /> Available</span>}
            <span className="flex items-center gap-1"><Eye className="w-3.5 h-3.5 text-purple-600" /> {notice.views || 0}</span>
          </div>
          <div className="mt-4 flex items-center justify-between">
            <span className="text-xs text-gray-500">Posted: {dateStr}</span>
            <Link to={`/notice/${notice.id}`} className="text-sm font-semibold text-purple-700 hover:text-purple-900">Read more &raquo;</Link>
          </div>
        </div>
      </div>
    </article>
  );
};

export default NoticeCard;
