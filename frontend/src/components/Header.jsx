import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Search, Briefcase, Menu, X } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';

const NAV = [
  { label: 'Home', to: '/' },
  { label: 'Govt Jobs', to: '/category/govt' },
  { label: 'Private Jobs', to: '/category/private' },
  { label: 'Admit Card', to: '/type/admit_card' },
  { label: 'Results', to: '/type/result' },
  { label: 'Answer Key', to: '/type/answer_key' },
  { label: 'Admission', to: '/type/admission' },
  { label: 'Scholarship', to: '/type/scholarship' },
  { label: 'Contact', to: '/contact' },
];

const Header = () => {
  const [q, setQ] = useState('');
  const [open, setOpen] = useState(false);
  const nav = useNavigate();
  const loc = useLocation();

  const onSearch = (e) => {
    e.preventDefault();
    if (q.trim()) nav(`/search?q=${encodeURIComponent(q.trim())}`);
  };

  return (
    <header className="sticky top-0 z-50 shadow-md">
      <div className="bg-purple-950 text-white">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-11 h-11 rounded-lg bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center shadow-lg">
              <Briefcase className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="text-xl md:text-2xl font-extrabold tracking-tight title-font">ASSAMVACANCIES<span className="text-purple-300">.COM</span></div>
              <div className="text-[10px] md:text-xs text-purple-200 -mt-1">Latest Jobs, Admit Card, Result, Scholarship in Assam</div>
            </div>
          </Link>
          <form onSubmit={onSearch} className="hidden md:flex items-center gap-2 max-w-md w-full">
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search jobs, admit card, results..."
              className="bg-white text-gray-900 border-0 h-10"
            />
            <Button type="submit" className="bg-purple-600 hover:bg-purple-500 text-white h-10">
              <Search className="w-4 h-4 mr-1" /> Search
            </Button>
          </form>
          <button onClick={() => setOpen(!open)} className="md:hidden p-2">
            {open ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      <nav className="assam-gradient text-white">
        <div className="max-w-7xl mx-auto px-4 hidden md:flex items-center gap-1 overflow-x-auto">
          {NAV.map((n) => {
            const active = loc.pathname === n.to;
            return (
              <Link
                key={n.to}
                to={n.to}
                className={`px-4 py-3 text-sm font-semibold whitespace-nowrap hover:bg-white/10 transition-colors ${active ? 'nav-link-active' : ''}`}
              >
                {n.label}
              </Link>
            );
          })}
        </div>
        {open && (
          <div className="md:hidden flex flex-col p-2 gap-1">
            <form onSubmit={onSearch} className="flex gap-2 mb-2">
              <Input value={q} onChange={(e)=>setQ(e.target.value)} placeholder="Search..." className="bg-white text-gray-900" />
              <Button type="submit" className="bg-purple-600 text-white"><Search className="w-4 h-4" /></Button>
            </form>
            {NAV.map(n => (
              <Link key={n.to} to={n.to} onClick={()=>setOpen(false)} className="px-3 py-2 hover:bg-white/10 rounded text-sm">{n.label}</Link>
            ))}
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;
