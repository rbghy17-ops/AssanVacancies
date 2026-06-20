import React, { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { fetchNotices } from '../lib/api';
import NoticeCard from '../components/NoticeCard';
import Sidebar from '../components/Sidebar';
import AdBanner from '../components/AdBanner';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Button } from '../components/ui/button';
import { Filter, MapPin, Tag, X } from 'lucide-react';
import { DISTRICTS, CATEGORIES, SECTION_BY_TYPE } from '../lib/constants';

const ANY = '__any__';

const ListPage = ({ noticeType }) => {
  const { type: typeParam } = useParams();
  const loc = useLocation();
  const nav = useNavigate();
  const isSearch = loc.pathname.startsWith('/search');

  const noticeTypeResolved = noticeType || typeParam || null;
  const section = noticeTypeResolved ? SECTION_BY_TYPE[noticeTypeResolved] : null;

  const params = useMemo(() => new URLSearchParams(loc.search), [loc.search]);
  const q = params.get('q') || '';
  const category = params.get('category') || '';
  const district = params.get('district') || '';

  const [notices, setNotices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    setLoading(true);
    const p = { limit: 30 };
    if (noticeTypeResolved) p.type = noticeTypeResolved;
    if (category) p.category = category;
    if (district) p.district = district;
    if (isSearch && q) p.search = q;
    fetchNotices(p)
      .then(r => { setNotices(r.notices || []); setTotal(r.total || 0); })
      .finally(() => setLoading(false));
  }, [noticeTypeResolved, category, district, isSearch, q]);

  const updateFilter = (key, value) => {
    const next = new URLSearchParams(loc.search);
    if (value && value !== ANY) next.set(key, value);
    else next.delete(key);
    nav({ pathname: loc.pathname, search: next.toString() });
  };

  const clearFilters = () => nav({ pathname: loc.pathname, search: q ? `?q=${encodeURIComponent(q)}` : '' });

  const heading = isSearch
    ? `Search results: "${q}"`
    : section?.plural || 'All Notices';

  const activeFilters = [category && `Category: ${category}`, district && `District: ${district}`].filter(Boolean);

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="bg-gradient-to-r from-purple-700 to-purple-900 text-white rounded-xl p-6 mb-6">
        <h1 className="text-2xl md:text-3xl font-extrabold title-font">{heading}</h1>
        <p className="text-purple-100 text-sm mt-1">{total} {total === 1 ? 'listing' : 'listings'} found{activeFilters.length ? ` • ${activeFilters.join(' • ')}` : ''}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-4">
          {/* Filter bar */}
          <div className="bg-white rounded-xl border border-purple-100 p-4 flex flex-col sm:flex-row sm:items-center gap-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-purple-900">
              <Filter className="w-4 h-4" /> Filters
            </div>
            <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div className="flex items-center gap-2">
                <Tag className="w-4 h-4 text-purple-500 flex-shrink-0" />
                <Select value={category || ANY} onValueChange={(v) => updateFilter('category', v)}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue placeholder="Any category" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value={ANY}>Any category</SelectItem>
                    {CATEGORIES.map(c => <SelectItem key={c.key} value={c.key}>{c.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-purple-500 flex-shrink-0" />
                <Select value={district || ANY} onValueChange={(v) => updateFilter('district', v)}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue placeholder="Any district" /></SelectTrigger>
                  <SelectContent className="max-h-72">
                    <SelectItem value={ANY}>All districts</SelectItem>
                    {DISTRICTS.map(d => <SelectItem key={d} value={d}>{d}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            {(category || district) && (
              <Button variant="outline" size="sm" onClick={clearFilters} className="border-purple-200 text-purple-700"><X className="w-3.5 h-3.5 mr-1" /> Clear</Button>
            )}
          </div>

          {loading ? (
            <div className="text-center py-10 text-purple-700">Loading...</div>
          ) : notices.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-purple-100">
              <div className="text-gray-700 font-medium">No listings found</div>
              <div className="text-sm text-gray-500 mt-1">Try adjusting your filters or search query.</div>
            </div>
          ) : (
            notices.map((n, idx) => (
              <React.Fragment key={n.id}>
                <NoticeCard notice={n} />
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
