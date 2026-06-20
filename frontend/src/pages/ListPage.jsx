import React, { useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { fetchJobs } from '../lib/api';
import JobCard from '../components/JobCard';
import Sidebar from '../components/Sidebar';
import AdBanner from '../components/AdBanner';

const LABELS = {
  govt: 'Government Jobs',
  private: 'Private Jobs',
  defence: 'Defence Jobs',
  banking: 'Banking Jobs',
  railway: 'Railway Jobs',
  teaching: 'Teaching Jobs',
  police: 'Police Jobs',
  recruitment: 'Recruitment Notifications',
  admit_card: 'Admit Cards',
  result: 'Results',
  answer_key: 'Answer Keys',
  admission: 'Admission Updates',
  scholarship: 'Scholarships',
};

const ListPage = () => {
  const { category, type } = useParams();
  const loc = useLocation();
  const isSearch = loc.pathname.startsWith('/search');
  const params = new URLSearchParams(loc.search);
  const q = params.get('q') || '';
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    setLoading(true);
    const p = { limit: 30 };
    if (category) p.category = category;
    if (type) p.job_type = type;
    if (isSearch && q) p.search = q;
    fetchJobs(p).then(r => { setJobs(r.jobs || []); setTotal(r.total || 0); }).finally(() => setLoading(false));
  }, [category, type, isSearch, q]);

  const heading = isSearch ? `Search: "${q}"` : (LABELS[category || type] || 'Jobs');

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="bg-gradient-to-r from-purple-700 to-purple-900 text-white rounded-xl p-6 mb-6">
        <h1 className="text-2xl md:text-3xl font-extrabold title-font">{heading}</h1>
        <p className="text-purple-100 text-sm mt-1">{total} listings found</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-4">
          {loading ? (
            <div className="text-center py-10 text-purple-700">Loading...</div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-10 bg-white rounded-xl border border-purple-100 text-gray-700">No listings found.</div>
          ) : (
            jobs.map((j, idx) => (
              <React.Fragment key={j.id}>
                <JobCard job={j} />
                {idx === 3 && <AdBanner size="medium" />}
              </React.Fragment>
            ))
          )}
        </div>
        <div><Sidebar /></div>
      </div>
    </div>
  );
};

export default ListPage;
