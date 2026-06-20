import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Twitter, Send, Youtube, TrendingUp, Award, Bell } from 'lucide-react';
import { fetchNotices } from '../lib/api';
import AdBanner from './AdBanner';

const Sidebar = () => {
  const [latest, setLatest] = useState([]);
  const [results, setResults] = useState([]);

  useEffect(() => {
    fetchNotices({ type: 'job', limit: 6 }).then(r => setLatest(r.notices || [])).catch(()=>{});
    fetchNotices({ type: 'result', limit: 4 }).then(r => setResults(r.notices || [])).catch(()=>{});
  }, []);

  return (
    <aside className="space-y-6">
      <div className="bg-white rounded-xl border border-purple-100 overflow-hidden">
        <div className="assam-gradient text-white px-4 py-3 font-bold flex items-center gap-2"><Award className="w-4 h-4" /> Follow Us</div>
        <div className="p-4 grid grid-cols-4 gap-2">
          <a href="#" className="flex items-center justify-center h-10 bg-blue-600 text-white rounded hover:opacity-90"><Facebook className="w-4 h-4" /></a>
          <a href="#" className="flex items-center justify-center h-10 bg-sky-500 text-white rounded hover:opacity-90"><Twitter className="w-4 h-4" /></a>
          <a href="#" className="flex items-center justify-center h-10 bg-blue-500 text-white rounded hover:opacity-90"><Send className="w-4 h-4" /></a>
          <a href="#" className="flex items-center justify-center h-10 bg-red-600 text-white rounded hover:opacity-90"><Youtube className="w-4 h-4" /></a>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-purple-100 overflow-hidden">
        <div className="assam-gradient text-white px-4 py-3 font-bold flex items-center gap-2"><TrendingUp className="w-4 h-4" /> Latest Jobs</div>
        <ul className="divide-y divide-purple-50">
          {latest.map(j => (
            <li key={j.id}>
              <Link to={`/notice/${j.id}`} className="block px-4 py-3 hover:bg-purple-50 text-sm text-gray-800">{j.title}</Link>
            </li>
          ))}
          {latest.length === 0 && <li className="px-4 py-3 text-sm text-gray-500">Loading...</li>}
        </ul>
      </div>

      <AdBanner size="large" />

      <div className="bg-white rounded-xl border border-purple-100 overflow-hidden">
        <div className="assam-gradient text-white px-4 py-3 font-bold flex items-center gap-2"><Bell className="w-4 h-4" /> Recent Results</div>
        <ul className="divide-y divide-purple-50">
          {results.map(j => (
            <li key={j.id}>
              <Link to={`/notice/${j.id}`} className="block px-4 py-3 hover:bg-purple-50 text-sm text-gray-800">{j.title}</Link>
            </li>
          ))}
          {results.length === 0 && <li className="px-4 py-3 text-sm text-gray-500">No results yet</li>}
        </ul>
      </div>

      <div className="bg-gradient-to-br from-purple-700 to-purple-900 text-white rounded-xl p-5">
        <div className="text-sm font-semibold mb-1">WhatsApp Channel</div>
        <p className="text-xs text-purple-200 mb-3">Get instant job updates on WhatsApp.</p>
        <a href="#" className="inline-block px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-white text-sm font-semibold rounded">Join Now</a>
      </div>
    </aside>
  );
};

export default Sidebar;
