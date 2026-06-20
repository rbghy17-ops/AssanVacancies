import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchJob } from '../lib/api';
import Sidebar from '../components/Sidebar';
import AdBanner from '../components/AdBanner';
import { Calendar, MapPin, Users, IndianRupee, Clock, FileText, ExternalLink, ChevronRight, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

const Row = ({ label, value }) => (
  <tr className="border-b border-purple-50">
    <td className="py-3 px-4 font-semibold text-purple-900 bg-purple-50/40 w-1/3">{label}</td>
    <td className="py-3 px-4 text-gray-800">{value || '—'}</td>
  </tr>
);

const JobDetail = () => {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchJob(id).then(setJob).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="max-w-7xl mx-auto px-4 py-12 text-center text-purple-700">Loading...</div>;
  if (!job) return <div className="max-w-7xl mx-auto px-4 py-12 text-center text-gray-700">Job not found. <Link to="/" className="text-purple-700 underline">Go home</Link></div>;

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <nav className="text-xs text-gray-500 flex items-center gap-1 mb-4">
        <Link to="/" className="hover:text-purple-700">Home</Link>
        <ChevronRight className="w-3 h-3" />
        <Link to={`/category/${job.category}`} className="hover:text-purple-700 capitalize">{job.category}</Link>
        <ChevronRight className="w-3 h-3" />
        <span className="text-gray-700 truncate">{job.title}</span>
      </nav>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <Link to="/" className="inline-flex items-center gap-1 text-sm text-purple-700 hover:text-purple-900 mb-3"><ArrowLeft className="w-4 h-4" /> Back</Link>
          <article className="bg-white rounded-xl border border-purple-100 overflow-hidden">
            <div className="p-6">
              <div className="flex flex-wrap gap-2 mb-3">
                <Badge className="bg-purple-100 text-purple-800 border-0 capitalize">{job.category}</Badge>
                <Badge variant="outline" className="border-purple-200 text-purple-700 capitalize">{job.job_type?.replace('_', ' ')}</Badge>
                {job.is_featured && <Badge className="bg-purple-600 text-white border-0">Featured</Badge>}
              </div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-purple-900 leading-tight title-font">{job.title}</h1>
              <div className="flex flex-wrap gap-4 mt-3 text-sm text-gray-600">
                {job.organization && <span className="flex items-center gap-1"><FileText className="w-4 h-4 text-purple-600" /> {job.organization}</span>}
                {job.location && <span className="flex items-center gap-1"><MapPin className="w-4 h-4 text-purple-600" /> {job.location}</span>}
                {job.posted_date && <span className="flex items-center gap-1"><Clock className="w-4 h-4 text-purple-600" /> Posted {new Date(job.posted_date).toLocaleDateString()}</span>}
              </div>
            </div>
            {job.thumbnail && (
              <div className="w-full h-64 md:h-80 bg-purple-50">
                <img src={job.thumbnail} alt={job.title} className="w-full h-full object-cover" />
              </div>
            )}
            <div className="p-6 space-y-6">
              <section>
                <h2 className="text-lg font-bold text-purple-900 mb-2">About this opportunity</h2>
                <p className="text-gray-800 leading-relaxed whitespace-pre-line">{job.description}</p>
              </section>

              <section>
                <h2 className="text-lg font-bold text-purple-900 mb-3">Key Details</h2>
                <div className="overflow-hidden rounded-lg border border-purple-100">
                  <table className="w-full text-sm">
                    <tbody>
                      <Row label="Organization" value={job.organization} />
                      <Row label="No. of Vacancies" value={job.vacancy_count} />
                      <Row label="Qualification" value={job.qualification} />
                      <Row label="Age Limit" value={job.age_limit} />
                      <Row label="Application Fee" value={job.application_fee} />
                      <Row label="Salary" value={job.salary} />
                      <Row label="Location" value={job.location} />
                      <Row label="Start Date" value={job.start_date} />
                      <Row label="Last Date" value={job.last_date} />
                    </tbody>
                  </table>
                </div>
              </section>

              {job.selection_process && (
                <section>
                  <h2 className="text-lg font-bold text-purple-900 mb-2">Selection Process</h2>
                  <p className="text-gray-800 whitespace-pre-line">{job.selection_process}</p>
                </section>
              )}

              {job.how_to_apply && (
                <section>
                  <h2 className="text-lg font-bold text-purple-900 mb-2">How to Apply</h2>
                  <p className="text-gray-800 whitespace-pre-line">{job.how_to_apply}</p>
                </section>
              )}

              <AdBanner size="medium" />

              <section>
                <h2 className="text-lg font-bold text-purple-900 mb-3">Important Links</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {job.apply_link && (
                    <a href={job.apply_link} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between px-4 py-3 bg-purple-700 hover:bg-purple-800 text-white rounded-lg font-semibold">
                      Apply Online <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                  {job.notification_link && (
                    <a href={job.notification_link} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between px-4 py-3 bg-white border border-purple-300 text-purple-700 hover:bg-purple-50 rounded-lg font-semibold">
                      Download Notification <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                  {job.official_website && (
                    <a href={job.official_website} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between px-4 py-3 bg-white border border-purple-300 text-purple-700 hover:bg-purple-50 rounded-lg font-semibold">
                      Official Website <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </section>
            </div>
          </article>
        </div>
        <div>
          <Sidebar />
        </div>
      </div>
    </div>
  );
};

export default JobDetail;
