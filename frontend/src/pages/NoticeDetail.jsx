import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchNotice } from '../lib/api';
import Sidebar from '../components/Sidebar';
import AdBanner from '../components/AdBanner';
import SeoMeta from '../components/SeoMeta';
import { Calendar, MapPin, Clock, FileText, ExternalLink, ChevronRight, ArrowLeft, Download, Link2 } from 'lucide-react';
import { Badge } from '../components/ui/badge';
import { SECTION_BY_TYPE } from '../lib/constants';

const Row = ({ label, value }) => (
  <tr className="border-b border-purple-50">
    <td className="py-3 px-4 font-semibold text-purple-900 bg-purple-50/40 w-1/3 align-top">{label}</td>
    <td className="py-3 px-4 text-gray-800">{value || '—'}</td>
  </tr>
);

const NoticeDetail = () => {
  const { id } = useParams();
  const [notice, setNotice] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchNotice(id).then(setNotice).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="max-w-7xl mx-auto px-4 py-12 text-center text-purple-700">Loading...</div>;
  if (!notice) return <div className="max-w-7xl mx-auto px-4 py-12 text-center text-gray-700">Notice not found. <Link to="/" className="text-purple-700 underline">Go home</Link></div>;

  const section = SECTION_BY_TYPE[notice.type] || { label: notice.type, path: '/' };
  const isJob = notice.type === 'job';

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <SeoMeta notice={notice} />
      <nav className="text-xs text-gray-500 flex items-center gap-1 mb-4 flex-wrap">
        <Link to="/" className="hover:text-purple-700">Home</Link>
        <ChevronRight className="w-3 h-3" />
        <Link to={section.path} className="hover:text-purple-700">{section.label}</Link>
        <ChevronRight className="w-3 h-3" />
        <span className="text-gray-700 truncate">{notice.title}</span>
      </nav>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <Link to={section.path} className="inline-flex items-center gap-1 text-sm text-purple-700 hover:text-purple-900 mb-3"><ArrowLeft className="w-4 h-4" /> Back to {section.label}</Link>
          <article className="bg-white rounded-xl border border-purple-100 overflow-hidden">
            <div className="p-6">
              <div className="flex flex-wrap gap-2 mb-3">
                <Badge className="bg-purple-100 text-purple-800 border-0 capitalize">{notice.category}</Badge>
                <Badge variant="outline" className="border-purple-200 text-purple-700">{section.label}</Badge>
                {notice.district && <Badge variant="outline" className="border-emerald-200 text-emerald-700"><MapPin className="w-3 h-3 mr-1" />{notice.district}</Badge>}
                {notice.is_featured && <Badge className="bg-purple-600 text-white border-0">Featured</Badge>}
              </div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-purple-900 leading-tight title-font">{notice.title}</h1>
              <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-sm text-gray-600">
                {notice.organization && <span className="flex items-center gap-1"><FileText className="w-4 h-4 text-purple-600" /> {notice.organization}</span>}
                {notice.location && <span className="flex items-center gap-1"><MapPin className="w-4 h-4 text-purple-600" /> {notice.location}</span>}
                {notice.posted_date && <span className="flex items-center gap-1"><Clock className="w-4 h-4 text-purple-600" /> Posted {new Date(notice.posted_date).toLocaleDateString()}</span>}
              </div>
            </div>
            {notice.thumbnail && (
              <div className="w-full h-56 md:h-72 bg-purple-50">
                <img src={notice.thumbnail} alt={notice.title} className="w-full h-full object-cover" />
              </div>
            )}
            <div className="p-6 space-y-6">
              <section>
                <h2 className="text-lg font-bold text-purple-900 mb-2">Overview</h2>
                <p className="text-gray-800 leading-relaxed whitespace-pre-line">{notice.description}</p>
              </section>

              {!isJob && notice.linked_job && (
                <section className="bg-purple-50 border border-purple-100 rounded-lg p-4">
                  <h3 className="text-sm font-bold text-purple-900 mb-1 flex items-center gap-2"><Link2 className="w-4 h-4" /> Related Job Notification</h3>
                  <Link to={`/notice/${notice.linked_job.id}`} className="text-purple-700 hover:text-purple-900 font-semibold">{notice.linked_job.title}</Link>
                  <div className="text-xs text-gray-600 mt-0.5">{notice.linked_job.organization}</div>
                </section>
              )}

              <section>
                <h2 className="text-lg font-bold text-purple-900 mb-3">Key Details</h2>
                <div className="overflow-hidden rounded-lg border border-purple-100">
                  <table className="w-full text-sm">
                    <tbody>
                      <Row label="Organization" value={notice.organization} />
                      <Row label="Category" value={notice.category && notice.category[0].toUpperCase() + notice.category.slice(1)} />
                      <Row label="District" value={notice.district} />
                      {isJob ? (
                        <>
                          <Row label="No. of Vacancies" value={notice.vacancy_count} />
                          <Row label="Eligibility" value={notice.eligibility} />
                          <Row label="Age Limit" value={notice.age_limit} />
                          <Row label="Application Fee" value={notice.application_fee} />
                          <Row label="Salary" value={notice.salary} />
                          <Row label="Start Date" value={notice.start_date} />
                          <Row label="Last Date" value={notice.last_date} />
                        </>
                      ) : (
                        <>
                          <Row label="Notice Date" value={notice.notice_date} />
                          {notice.last_date && <Row label="Important Date" value={notice.last_date} />}
                        </>
                      )}
                    </tbody>
                  </table>
                </div>
              </section>

              {isJob && notice.selection_process && (
                <section>
                  <h2 className="text-lg font-bold text-purple-900 mb-2">Selection Process</h2>
                  <p className="text-gray-800 whitespace-pre-line">{notice.selection_process}</p>
                </section>
              )}

              {isJob && notice.how_to_apply && (
                <section>
                  <h2 className="text-lg font-bold text-purple-900 mb-2">How to Apply</h2>
                  <p className="text-gray-800 whitespace-pre-line">{notice.how_to_apply}</p>
                </section>
              )}

              <AdBanner size="medium" />

              <section>
                <h2 className="text-lg font-bold text-purple-900 mb-3">Important Links</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {!isJob && notice.download_link && (
                    <a href={notice.download_link} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between px-4 py-3 bg-purple-700 hover:bg-purple-800 text-white rounded-lg font-semibold">
                      <span className="flex items-center gap-2"><Download className="w-4 h-4" /> Download {section.label}</span>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                  {isJob && notice.apply_link && (
                    <a href={notice.apply_link} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between px-4 py-3 bg-purple-700 hover:bg-purple-800 text-white rounded-lg font-semibold">
                      Apply Online <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                  {isJob && notice.notification_link && (
                    <a href={notice.notification_link} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between px-4 py-3 bg-white border border-purple-300 text-purple-700 hover:bg-purple-50 rounded-lg font-semibold">
                      Official Notification <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                  {notice.official_website && (
                    <a href={notice.official_website} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between px-4 py-3 bg-white border border-purple-300 text-purple-700 hover:bg-purple-50 rounded-lg font-semibold">
                      Official Website <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </section>
            </div>
          </article>
        </div>
        <div><Sidebar /></div>
      </div>
    </div>
  );
};

export default NoticeDetail;
