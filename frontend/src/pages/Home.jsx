import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchJobs, fetchStats } from '../lib/api';
import JobCard from '../components/JobCard';
import Sidebar from '../components/Sidebar';
import AdBanner from '../components/AdBanner';
import { Shield, Building2, Train, Landmark, GraduationCap, BookOpen, Briefcase, Award, Bell, ChevronRight } from 'lucide-react';

const CATS = [
  { key: 'govt', label: 'Govt Jobs', Icon: Landmark, color: 'from-purple-500 to-purple-700' },
  { key: 'defence', label: 'Defence', Icon: Shield, color: 'from-emerald-500 to-emerald-700' },
  { key: 'railway', label: 'Railway', Icon: Train, color: 'from-blue-500 to-blue-700' },
  { key: 'banking', label: 'Banking', Icon: Building2, color: 'from-amber-500 to-amber-700' },
  { key: 'teaching', label: 'Teaching', Icon: GraduationCap, color: 'from-pink-500 to-pink-700' },
  { key: 'police', label: 'Police', Icon: Shield, color: 'from-red-500 to-red-700' },
  { key: 'private', label: 'Private', Icon: Briefcase, color: 'from-slate-500 to-slate-700' },
];

const TYPES = [
  { key: 'admit_card', label: 'Admit Cards', Icon: BookOpen },
  { key: 'result', label: 'Results', Icon: Award },
  { key: 'answer_key', label: 'Answer Keys', Icon: Bell },
  { key: 'admission', label: 'Admissions', Icon: GraduationCap },
  { key: 'scholarship', label: 'Scholarships', Icon: Award },
];

const Home = () => {
  const [recruitments, setRecruitments] = useState([]);
  const [featured, setFeatured] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchJobs({ job_type: 'recruitment', limit: 10 }),
      fetchJobs({ featured: true, limit: 4 }),
      fetchStats(),
    ]).then(([r, f, s]) => {
      setRecruitments(r.jobs || []);
      setFeatured(f.jobs || []);
      setStats(s);
    }).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <section className="assam-gradient text-white">
        <div className="max-w-7xl mx-auto px-4 py-10 md:py-14">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-extrabold leading-tight title-font">Latest Jobs in Assam &amp; Northeast India</h1>
              <p className="text-purple-100 mt-3 max-w-2xl">Government &amp; private job notifications, admit cards, results, answer keys, admissions and scholarships — updated daily for Assam students &amp; job seekers.</p>
            </div>
            {stats && (
              <div className="grid grid-cols-3 gap-3 text-center min-w-[280px]">
                <div className="bg-white/10 backdrop-blur rounded-lg px-3 py-3">
                  <div className="text-2xl font-bold">{stats.total_jobs}</div>
                  <div className="text-[11px] uppercase tracking-wide text-purple-200">Total Jobs</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-lg px-3 py-3">
                  <div className="text-2xl font-bold">{stats.by_type?.recruitment || 0}</div>
                  <div className="text-[11px] uppercase tracking-wide text-purple-200">Active</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-lg px-3 py-3">
                  <div className="text-2xl font-bold">{stats.by_type?.result || 0}</div>
                  <div className="text-[11px] uppercase tracking-wide text-purple-200">Results</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      <div className="bg-purple-100 border-y border-purple-200">
        <div className="max-w-7xl mx-auto px-4 py-2 flex items-center gap-3 overflow-hidden">
          <span className="bg-purple-700 text-white text-xs font-bold px-3 py-1 rounded uppercase whitespace-nowrap">Latest</span>
          <div className="overflow-hidden flex-1">
            <div className="ticker text-sm text-purple-900">
              {featured.concat(featured).map((j, i) => (
                <Link key={i} to={`/job/${j.id}`} className="mx-6 hover:underline">• {j.title}</Link>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div>
            <h2 className="text-xl font-bold text-purple-900 mb-3 title-font">Browse by Category</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {CATS.map(c => (
                <Link key={c.key} to={`/category/${c.key}`} className={`group bg-gradient-to-br ${c.color} text-white rounded-xl p-4 hover:shadow-lg hover:-translate-y-0.5 transition`}>
                  <c.Icon className="w-7 h-7 mb-2" />
                  <div className="font-semibold">{c.label}</div>
                  <div className="text-xs opacity-80 mt-1">{stats?.by_category?.[c.key] || 0} listings</div>
                </Link>
              ))}
            </div>
          </div>

          <AdBanner size="wide" />

          <div>
            <h2 className="text-xl font-bold text-purple-900 mb-3 title-font">Quick Access</h2>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {TYPES.map(t => (
                <Link key={t.key} to={`/type/${t.key}`} className="bg-white border border-purple-100 hover:border-purple-400 rounded-xl p-4 text-center hover:shadow transition">
                  <t.Icon className="w-6 h-6 mx-auto text-purple-600 mb-2" />
                  <div className="text-sm font-semibold text-gray-800">{t.label}</div>
                  <div className="text-xs text-gray-500">{stats?.by_type?.[t.key] || 0}</div>
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between mt-4">
            <h2 className="text-xl font-bold text-purple-900 title-font">Latest Recruitment</h2>
            <Link to="/type/recruitment" className="text-sm font-semibold text-purple-700 hover:text-purple-900 flex items-center gap-1">View all <ChevronRight className="w-4 h-4" /></Link>
          </div>

          {loading ? (
            <div className="text-center py-10 text-purple-700">Loading jobs...</div>
          ) : (
            <div className="space-y-4">
              {recruitments.map((j, idx) => (
                <React.Fragment key={j.id}>
                  <JobCard job={j} />
                  {idx === 3 && <AdBanner size="medium" label="Sponsored" />}
                </React.Fragment>
              ))}
            </div>
          )}
        </div>
        <div>
          <Sidebar />
        </div>
      </div>
    </div>
  );
};

export default Home;
