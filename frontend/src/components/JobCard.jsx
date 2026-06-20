import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, MapPin, Users, Eye } from 'lucide-react';
import { Badge } from './ui/badge';

const CAT_COLORS = {
  govt: 'bg-purple-100 text-purple-800',
  defence: 'bg-emerald-100 text-emerald-800',
  railway: 'bg-blue-100 text-blue-800',
  banking: 'bg-amber-100 text-amber-800',
  teaching: 'bg-pink-100 text-pink-800',
  police: 'bg-red-100 text-red-800',
  private: 'bg-slate-100 text-slate-800',
};

const TYPE_LABEL = {
  recruitment: 'Recruitment',
  admit_card: 'Admit Card',
  result: 'Result',
  answer_key: 'Answer Key',
  admission: 'Admission',
  scholarship: 'Scholarship',
};

const JobCard = ({ job }) => {
  const dateStr = job.posted_date ? new Date(job.posted_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '';
  return (
    <article className="job-card bg-white rounded-xl border border-purple-100 overflow-hidden">
      <div className="flex flex-col md:flex-row">
        <div className="md:w-48 md:flex-shrink-0 h-44 md:h-auto bg-purple-50">
          <img src={job.thumbnail} alt={job.title} className="w-full h-full object-cover" loading="lazy" />
        </div>
        <div className="p-5 flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <Badge className={`${CAT_COLORS[job.category] || 'bg-gray-100 text-gray-800'} border-0 capitalize`}>{job.category}</Badge>
            <Badge variant="outline" className="border-purple-200 text-purple-700">{TYPE_LABEL[job.job_type] || job.job_type}</Badge>
            {job.is_featured && <Badge className="bg-purple-600 text-white border-0">Featured</Badge>}
          </div>
          <Link to={`/job/${job.id}`}>
            <h2 className="text-lg md:text-xl font-bold text-purple-900 hover:text-purple-700 leading-snug">{job.title}</h2>
          </Link>
          <p className="text-sm text-gray-600 mt-2 line-clamp-2">{job.description}</p>
          <div className="flex flex-wrap gap-4 mt-3 text-xs text-gray-600">
            {job.vacancy_count && <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5 text-purple-600" /> {job.vacancy_count} posts</span>}
            {job.location && <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-purple-600" /> {job.location}</span>}
            {job.last_date && <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5 text-purple-600" /> Last: {job.last_date}</span>}
            <span className="flex items-center gap-1"><Eye className="w-3.5 h-3.5 text-purple-600" /> {job.views || 0}</span>
          </div>
          <div className="mt-4 flex items-center justify-between">
            <span className="text-xs text-gray-500">Posted: {dateStr}</span>
            <Link to={`/job/${job.id}`} className="text-sm font-semibold text-purple-700 hover:text-purple-900">Read more &raquo;</Link>
          </div>
        </div>
      </div>
    </article>
  );
};

export default JobCard;
