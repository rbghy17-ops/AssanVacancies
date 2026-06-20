import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchNotices, fetchStats } from '../lib/api';
import NoticeCard from '../components/NoticeCard';
import Sidebar from '../components/Sidebar';
import AdBanner from '../components/AdBanner';
import { Shield, Building2, Train, Landmark, GraduationCap, Briefcase, BookOpen, Award, Bell, ChevronRight, FileCheck } from 'lucide-react';
import { SECTIONS } from '../lib/constants';

const CATS = [
  { key: 'govt', label: 'Govt Jobs', Icon: Landmark, color: 'from-purple-500 to-purple-700' },
  { key: 'defence', label: 'Defence', Icon: Shield, color: 'from-emerald-500 to-emerald-700' },
  { key: 'railway', label: 'Railway', Icon: Train, color: 'from-blue-500 to-blue-700' },
  { key: 'banking', label: 'Banking', Icon: Building2, color: 'from-amber-500 to-amber-700' },
  { key: 'teaching', label: 'Teaching', Icon: GraduationCap, color: 'from-pink-500 to-pink-700' },
  { key: 'police', label: 'Police', Icon: Shield, color: 'from-red-500 to-red-700' },
  { key: 'private', label: 'Private', Icon: Briefcase, color: 'from-slate-500 to-slate-700' },
];

const SECTION_ICONS = {
  job: Briefcase,
  admit_card: BookOpen,
  result: Award,
  answer_key: FileCheck,
};

const Home = () => {
  const [jobs, setJobs] = useState([]);
  const [featured, setFeatured] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchNotices({ type: 'job', limit: 10 }),
      fetchNotices({ featured: true, limit: 4 }),
      fetchStats(),
    ]).then(([j, f, s]) => {
      setJobs(j.notices || []);
      setFeatured(f.notices || []);
      setStats(s);
    }).finally(() => setLoading(false));
  }, []);

  const jobCountByCategory = (cat) => stats?.by_category?.[cat] || 0;

  return (
    <div>
      <section className="assam-gradient text-white">
        <div className="max-w-7xl mx-auto px-4 py-10 md:py-14">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-extrabold leading-tight title-font">Latest Jobs in Assam &amp; Northeast India</h1>
              <p className="text-purple-100 mt-3 max-w-2xl">Job notifications, admit cards, results and answer keys — verified updates from across all 35 districts of Assam.</p>
            </div>
            {stats && (
              <div className="grid grid-cols-4 gap-2 text-center min-w-[280px]">
                <div className="bg-white/10 backdrop-blur rounded-lg px-2 py-3">
                  <div className="text-xl font-bold">{stats.by_type?.job || 0}</div>
                  <div className="text-[10px] uppercase tracking-wide text-purple-200">Jobs</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-lg px-2 py-3">
                  <div className="text-xl font-bold">{stats.by_type?.admit_card || 0}</div>
                  <div className="text-[10px] uppercase tracking-wide text-purple-200">Admit</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-lg px-2 py-3">
                  <div className="text-xl font-bold">{stats.by_type?.result || 0}</div>
                  <div className="text-[10px] uppercase tracking-wide text-purple-200">Results</div>
                </div>
                <div className="bg-white/10 backdrop-blur rounded-lg px-2 py-3">
                  <div className="text-xl font-bold">{stats.by_type?.answer_key || 0}</div>
                  <div className="text-[10px] uppercase tracking-wide text-purple-200">Keys</div>
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
              {(featured.length ? featured : jobs).concat(featured.length ? featured : jobs).map((j, i) => (
                <Link key={i} to={`/notice/${j.id}`} className="mx-6 hover:underline">• {j.title}</Link>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div>
            <h2 className="text-xl font-bold text-purple-900 mb-3 title-font">Browse by Section</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {SECTIONS.map(s => {
                const Icon = SECTION_ICONS[s.key] || Briefcase;
                return (
                  <Link key={s.key} to={s.path} className="bg-gradient-to-br from-purple-600 to-purple-800 text-white rounded-xl p-4 hover:shadow-lg hover:-translate-y-0.5 transition">
                    <Icon className="w-6 h-6 mb-2" />
                    <div className="font-semibold">{s.label}</div>
                    <div className="text-xs text-purple-200 mt-1">{stats?.by_type?.[s.key] || 0} listings</div>
                  </Link>
                );
              })}
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold text-purple-900 mb-3 title-font">Browse by Category</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {CATS.map(c => (
                <Link key={c.key} to={`/jobs?category=${c.key}`} className={`group bg-gradient-to-br ${c.color} text-white rounded-xl p-4 hover:shadow-lg hover:-translate-y-0.5 transition`}>
                  <c.Icon className="w-7 h-7 mb-2" />
                  <div className="font-semibold">{c.label}</div>
                  <div className="text-xs opacity-80 mt-1">{jobCountByCategory(c.key)} listings</div>
                </Link>
              ))}
            </div>
          </div>

          <AdBanner size="wide" />

          <div className="flex items-center justify-between mt-4">
            <h2 className="text-xl font-bold text-purple-900 title-font">Latest Jobs</h2>
            <Link to="/jobs" className="text-sm font-semibold text-purple-700 hover:text-purple-900 flex items-center gap-1">View all <ChevronRight className="w-4 h-4" /></Link>
          </div>

          {loading ? (
            <div className="text-center py-10 text-purple-700">Loading...</div>
          ) : (
            <div className="space-y-4">
              {jobs.map((j, idx) => (
                <React.Fragment key={j.id}>
                  <NoticeCard notice={j} />
                  {idx === 3 && <AdBanner size="medium" label="Sponsored" />}
                </React.Fragment>
              ))}
            </div>
          )}
        </div>
        <div><Sidebar /></div>
      </div>
    </div>
  );
};

export default Home;
