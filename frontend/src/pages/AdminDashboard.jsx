import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { fetchNotices, fetchStats, createNotice, updateNotice, deleteNotice, listContacts, deleteContact, fetchActivity, changePassword } from '../lib/api';
import api from '../lib/api';
import { useAdSettings } from '../context/AdSettingsContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Switch } from '../components/ui/switch';
import { Badge } from '../components/ui/badge';
import { LogOut, Plus, Pencil, Trash2, Briefcase, BarChart3, Mail, FileText, Search, Shield, KeyRound, Check, XCircle, Lock, Megaphone, LineChart, ExternalLink, TrendingUp } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import { DISTRICTS, CATEGORIES, SECTIONS } from '../lib/constants';
import { computeNoticeStatus } from '../lib/noticeStatus';

const TYPES = SECTIONS.map(s => ({ key: s.key, label: s.label }));

const emptyForm = {
  title: '', organization: '', type: 'job', category: 'govt', district: 'Kamrup Metropolitan',
  description: '', location: 'Assam', thumbnail: '', is_featured: false,
  // job-specific
  vacancy_count: '', eligibility: '', age_limit: '', application_fee: '', salary: '',
  start_date: '', last_date: '', selection_process: '', how_to_apply: '',
  apply_link: '', notification_link: '', official_website: '',
  // admit_card / result / answer_key-specific
  notice_date: '', linked_job_id: null, download_link: '',
};

const AdminDashboard = () => {
  const { user, loading: authLoading, logout } = useAuth();
  const nav = useNavigate();
  const [stats, setStats] = useState(null);
  const [notices, setNotices] = useState([]);
  const [linkableJobs, setLinkableJobs] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [activity, setActivity] = useState([]);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [pwdOpen, setPwdOpen] = useState(false);
  const [pwdForm, setPwdForm] = useState({ old: '', new1: '', new2: '' });
  const [pwdErr, setPwdErr] = useState('');
  // Ad settings
  const adSettingsCtx = useAdSettings();
  const [adsEnabled, setAdsEnabled] = useState(true);
  const [adsDisabledPathsText, setAdsDisabledPathsText] = useState('/privacy\n/terms\n/disclaimer\n/contact');
  const [adsSaving, setAdsSaving] = useState(false);
  // Search Console verification
  const [scToken, setScToken] = useState('');
  const [scSaving, setScSaving] = useState(false);
  // GA4 analytics widgets
  const [analytics, setAnalytics] = useState(null);
  const [analyticsError, setAnalyticsError] = useState('');
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [topWindow, setTopWindow] = useState('7d');

  useEffect(() => {
    if (!authLoading) {
      if (!user) { nav('/admin/login'); return; }
      if (user.must_reset) { nav('/admin/login'); return; }
    }
  }, [user, authLoading, nav]);

  const refresh = () => {
    fetchStats().then(setStats).catch(()=>{});
    const p = { limit: 300, include_closed: true };
    if (search) p.search = search;
    if (filterType !== 'all') p.type = filterType;
    fetchNotices(p).then(r => setNotices(r.notices || [])).catch(()=>{});
    fetchNotices({ type: 'job', limit: 200, include_closed: true }).then(r => setLinkableJobs(r.notices || [])).catch(()=>{});
    listContacts().then(setContacts).catch(()=>{});
    fetchActivity().then(setActivity).catch(()=>{});
  };

  useEffect(() => { if (user && !user.must_reset) refresh(); /* eslint-disable-next-line */ }, [user]);

  // Load ad settings once admin is authed
  useEffect(() => {
    if (user && !user.must_reset) {
      api.get('/ads/settings').then(r => {
        setAdsEnabled(r.data.ads_enabled !== false);
        const paths = Array.isArray(r.data.disabled_paths) ? r.data.disabled_paths : [];
        setAdsDisabledPathsText(paths.join('\n'));
      }).catch(()=>{});
      api.get('/site/verification').then(r => {
        setScToken(r.data?.google_site_verification || '');
      }).catch(()=>{});
    }
  }, [user]);

  const loadAnalytics = async () => {
    setAnalyticsLoading(true);
    setAnalyticsError('');
    try {
      const res = await api.get('/admin/analytics/dashboard');
      setAnalytics(res.data);
    } catch (e) {
      const detail = e?.response?.data?.detail || e?.message || 'Failed to load analytics';
      setAnalyticsError(String(detail));
      setAnalytics(null);
    }
    setAnalyticsLoading(false);
  };

  // Auto-load analytics once admin is authed (one-shot)
  useEffect(() => {
    if (user && !user.must_reset && analytics === null && !analyticsError) {
      loadAnalytics();
    }
    // eslint-disable-next-line
  }, [user]);

  const saveScToken = async () => {
    setScSaving(true);
    try {
      await api.put('/admin/site/verification', { google_site_verification: scToken.trim() });
      toast({ title: 'Verification token saved', description: 'Reload the public site to see the meta tag.' });
    } catch (e) {
      toast({ title: 'Save failed', description: String(e?.response?.data?.detail || e?.message) });
    }
    setScSaving(false);
  };

  const saveAdSettings = async () => {
    setAdsSaving(true);
    const paths = adsDisabledPathsText
      .split('\n')
      .map(p => p.trim())
      .filter(Boolean);
    try {
      await api.put('/admin/ads/settings', {
        ads_enabled: adsEnabled,
        disabled_paths: paths,
      });
      toast({ title: 'Ad settings saved' });
      adSettingsCtx.refresh();
    } catch (e) {
      toast({ title: 'Save failed', description: String(e?.response?.data?.detail || e?.message) });
    }
    setAdsSaving(false);
  };
  useEffect(() => {
    if (user && !user.must_reset) {
      const t = setTimeout(() => {
        const p = { limit: 300, include_closed: true };
        if (search) p.search = search;
        if (filterType !== 'all') p.type = filterType;
        fetchNotices(p).then(r => setNotices(r.notices || [])).catch(()=>{});
      }, 300);
      return () => clearTimeout(t);
    }
  }, [search, filterType, user]);

  const openNew = () => { setEditing(null); setForm(emptyForm); setOpen(true); };
  const openEdit = (n) => { setEditing(n); setForm({ ...emptyForm, ...n }); setOpen(true); };

  const save = async () => {
    if (!form.title || !form.organization || !form.description) {
      toast({ title: 'Please fill title, organization and description' }); return;
    }
    const payload = { ...form };
    if (payload.linked_job_id === '__none__') payload.linked_job_id = null;
    try {
      if (editing) {
        await updateNotice(editing.id, payload);
        toast({ title: 'Notice updated' });
      } else {
        await createNotice(payload);
        toast({ title: 'Notice created' });
      }
      setOpen(false);
      refresh();
    } catch (e) {
      toast({ title: 'Save failed', description: String(e?.response?.data?.detail || e?.message || e) });
    }
  };

  const remove = async (n) => {
    if (!window.confirm(`Delete "${n.title}"?`)) return;
    try {
      await deleteNotice(n.id);
      toast({ title: 'Deleted' });
      refresh();
    } catch (e) {
      toast({ title: 'Delete failed', description: String(e?.response?.data?.detail || e?.message) });
    }
  };

  const removeContact = async (c) => {
    if (!window.confirm('Delete this message?')) return;
    await deleteContact(c.id);
    refresh();
  };

  const submitPasswordChange = async (e) => {
    e.preventDefault();
    setPwdErr('');
    if (pwdForm.new1.length < 8) { setPwdErr('New password must be at least 8 characters.'); return; }
    if (pwdForm.new1 !== pwdForm.new2) { setPwdErr('Passwords do not match.'); return; }
    try {
      const res = await changePassword({ old_password: pwdForm.old, new_password: pwdForm.new1 });
      if (res?.token) localStorage.setItem('av_admin_token', res.token);
      toast({ title: 'Password updated' });
      setPwdOpen(false);
      setPwdForm({ old: '', new1: '', new2: '' });
    } catch (err) {
      setPwdErr(err?.response?.data?.detail || 'Update failed');
    }
  };

  if (authLoading) return <div className="text-center py-20">Loading...</div>;
  if (!user || user.must_reset) return null;

  const isJobType = form.type === 'job';
  const typeLabel = TYPES.find(t => t.key === form.type)?.label || form.type;

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-extrabold text-purple-900 title-font">Admin Dashboard</h1>
          <p className="text-sm text-gray-600">Welcome back, {user.username}</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Link to="/" className="text-sm text-purple-700 hover:underline px-2">View Site</Link>
          <Button variant="outline" onClick={()=>setPwdOpen(true)} className="border-purple-300"><KeyRound className="w-4 h-4 mr-1" /> Change Password</Button>
          <Button variant="outline" onClick={() => { logout(); nav('/admin/login'); }} className="border-purple-300"><LogOut className="w-4 h-4 mr-1" /> Logout</Button>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard icon={Briefcase} label="Total Notices" value={stats.total_notices || stats.total_jobs || 0} />
          <StatCard icon={FileText} label="Jobs" value={stats.by_type?.job || 0} />
          <StatCard icon={BarChart3} label="Results + Keys" value={(stats.by_type?.result || 0) + (stats.by_type?.answer_key || 0)} />
          <StatCard icon={Mail} label="Messages" value={stats.messages || 0} />
        </div>
      )}

      <Tabs defaultValue="notices">
        <TabsList className="bg-purple-100 flex flex-wrap h-auto">
          <TabsTrigger value="notices">Notices</TabsTrigger>
          <TabsTrigger value="messages">Messages</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="ads"><Megaphone className="w-3.5 h-3.5 mr-1" /> Ads</TabsTrigger>
          <TabsTrigger value="activity"><Shield className="w-3.5 h-3.5 mr-1" /> Activity Log</TabsTrigger>
        </TabsList>

        <TabsContent value="notices" className="mt-4">
          <div className="bg-white rounded-xl border border-purple-100 p-4">
            <div className="flex flex-col md:flex-row md:items-center gap-3 mb-4">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3 top-3 text-purple-500" />
                <Input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search by title or organization" className="pl-9" />
              </div>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="w-full md:w-44"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All types</SelectItem>
                  {TYPES.map(t => <SelectItem key={t.key} value={t.key}>{t.label}</SelectItem>)}
                </SelectContent>
              </Select>
              <Button onClick={openNew} className="bg-purple-700 hover:bg-purple-800"><Plus className="w-4 h-4 mr-1" /> Add Notice</Button>
            </div>
            <div className="overflow-x-auto -mx-4 sm:mx-0">
              <table className="w-full text-sm min-w-[800px]">
                <thead className="bg-purple-50 text-purple-900">
                  <tr>
                    <th className="text-left px-3 py-2">Title</th>
                    <th className="text-left px-3 py-2">Type</th>
                    <th className="text-left px-3 py-2">Category</th>
                    <th className="text-left px-3 py-2">District</th>
                    <th className="text-left px-3 py-2">Status</th>
                    <th className="text-left px-3 py-2">Views</th>
                    <th className="text-right px-3 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {notices.map(n => {
                    const { isClosed, daysLeft, urgency } = computeNoticeStatus(n);
                    return (
                    <tr key={n.id} className="border-b border-purple-50 hover:bg-purple-50/40">
                      <td className="px-3 py-2 max-w-md truncate">
                        {n.is_featured && <span className="text-purple-700 mr-1" title="Featured">★</span>}
                        {n.title}
                      </td>
                      <td className="px-3 py-2"><Badge variant="outline" className="border-purple-200 text-purple-700 text-xs">{TYPES.find(t=>t.key===n.type)?.label || n.type}</Badge></td>
                      <td className="px-3 py-2 capitalize">{n.category}</td>
                      <td className="px-3 py-2">{n.district || '—'}</td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        {isClosed
                          ? <Badge className="bg-gray-200 text-gray-700 border border-gray-300 text-xs"><Lock className="w-3 h-3 mr-1" />Closed</Badge>
                          : n.type === 'job' && daysLeft !== null
                            ? <Badge className={`text-xs border ${urgency === 'red' ? 'bg-red-100 text-red-800 border-red-200' : urgency === 'amber' ? 'bg-amber-100 text-amber-800 border-amber-200' : 'bg-emerald-100 text-emerald-800 border-emerald-200'}`}>{daysLeft}d left</Badge>
                            : <Badge className="bg-emerald-100 text-emerald-800 border border-emerald-200 text-xs">Open</Badge>}
                      </td>
                      <td className="px-3 py-2">{n.views || 0}</td>
                      <td className="px-3 py-2 text-right whitespace-nowrap">
                        <Button size="sm" variant="outline" onClick={()=>openEdit(n)} className="mr-1 border-purple-300"><Pencil className="w-3.5 h-3.5" /></Button>
                        <Button size="sm" variant="outline" onClick={()=>remove(n)} className="text-red-600 border-red-200 hover:bg-red-50"><Trash2 className="w-3.5 h-3.5" /></Button>
                      </td>
                    </tr>
                  );})}
                  {notices.length === 0 && <tr><td colSpan={7} className="text-center py-6 text-gray-500">No notices</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="messages" className="mt-4">
          <div className="bg-white rounded-xl border border-purple-100 p-4">
            <h3 className="font-semibold text-purple-900 mb-3">Contact Messages ({contacts.length})</h3>
            <div className="space-y-3">
              {contacts.map(c => (
                <div key={c.id} className="border border-purple-100 rounded-lg p-3">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div className="min-w-0">
                      <div className="font-semibold text-purple-900 truncate">{c.name} <span className="text-xs text-gray-500">&lt;{c.email}&gt;</span></div>
                      <div className="text-xs text-gray-500">{c.subject || '(no subject)'} • {new Date(c.created_at).toLocaleString()}</div>
                    </div>
                    <Button size="sm" variant="outline" onClick={()=>removeContact(c)} className="text-red-600 border-red-200 self-start sm:self-auto"><Trash2 className="w-3.5 h-3.5" /></Button>
                  </div>
                  <p className="text-sm text-gray-700 mt-2 whitespace-pre-line">{c.message}</p>
                </div>
              ))}
              {contacts.length === 0 && <div className="text-center text-gray-500 py-6">No messages yet</div>}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="mt-4">
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div>
                <h3 className="font-bold text-purple-900 flex items-center gap-2"><LineChart className="w-4 h-4" /> Live Analytics (GA4)</h3>
                <p className="text-xs text-gray-500 mt-0.5">{analytics?.property_id ? `Property ${analytics.property_id}` : 'Google Analytics 4'} — single combined API call</p>
              </div>
              <Button onClick={loadAnalytics} variant="outline" disabled={analyticsLoading} className="border-purple-300">
                {analyticsLoading ? 'Refreshing...' : 'Refresh'}
              </Button>
            </div>

            {analyticsError && (
              <div className="bg-amber-50 border border-amber-200 text-amber-900 rounded-lg p-3 text-sm">
                <strong>Analytics unavailable:</strong> {analyticsError}
                <div className="text-xs text-amber-800 mt-1">
                  This is expected on a brand-new GA4 property until data starts flowing — Google typically needs 24–48 hours
                  to attribute and surface property data.
                </div>
              </div>
            )}

            {analytics && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Widget 1: Top Viewed Notices */}
                <div className="bg-white rounded-xl border border-purple-100 p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-bold text-purple-900 flex items-center gap-2"><TrendingUp className="w-4 h-4" /> Top Viewed Notices</h4>
                    <div className="flex items-center gap-1 bg-purple-100 rounded p-0.5 text-xs">
                      <button onClick={() => setTopWindow('7d')} className={`px-2 py-0.5 rounded ${topWindow === '7d' ? 'bg-white text-purple-900 shadow-sm font-semibold' : 'text-purple-700'}`}>7 days</button>
                      <button onClick={() => setTopWindow('30d')} className={`px-2 py-0.5 rounded ${topWindow === '30d' ? 'bg-white text-purple-900 shadow-sm font-semibold' : 'text-purple-700'}`}>30 days</button>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 mb-3">
                    Total page views ({topWindow}): <strong className="text-purple-900">{analytics.totals?.[`views_${topWindow}`] ?? 0}</strong>
                  </div>
                  <div className="space-y-2">
                    {(topWindow === '7d' ? analytics.top_notices_7d : analytics.top_notices_30d).map((row, i) => (
                      <div key={`${row.notice_id}-${i}`} className="flex items-center justify-between gap-2 py-2 border-b border-purple-50 last:border-0">
                        <div className="min-w-0 flex-1">
                          <a href={`/notice/${row.notice_id}`} target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-purple-800 hover:text-purple-900 line-clamp-1">
                            {row.title || row.page_title || row.page_path}
                          </a>
                          {row.organization && <div className="text-xs text-gray-500 line-clamp-1">{row.organization}</div>}
                        </div>
                        <span className="text-sm font-semibold text-purple-900 whitespace-nowrap">{row.views}</span>
                      </div>
                    ))}
                    {(topWindow === '7d' ? analytics.top_notices_7d : analytics.top_notices_30d).length === 0 && (
                      <div className="text-sm text-gray-500 text-center py-6">No views recorded yet for this window.</div>
                    )}
                  </div>
                </div>

                {/* Widget 2: Traffic Sources */}
                <div className="bg-white rounded-xl border border-purple-100 p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-bold text-purple-900 flex items-center gap-2"><BarChart3 className="w-4 h-4" /> Traffic Sources</h4>
                    <span className="text-xs text-gray-500">Last 30 days</span>
                  </div>
                  <div className="text-xs text-gray-500 mb-3">
                    Total sessions: <strong className="text-purple-900">{analytics.totals?.sessions_30d ?? 0}</strong>
                  </div>
                  <div className="space-y-2">
                    {analytics.traffic_sources_30d.map((row) => (
                      <Bar
                        key={row.channel}
                        label={row.channel}
                        value={row.sessions}
                        max={analytics.totals?.sessions_30d || 1}
                      />
                    ))}
                    {analytics.traffic_sources_30d.length === 0 && (
                      <div className="text-sm text-gray-500 text-center py-6">No traffic recorded yet.</div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Existing static content breakdown — kept as a quick reference */}
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                <div className="bg-white rounded-xl border border-purple-100 p-5">
                  <h4 className="font-bold text-purple-900 mb-3 text-sm">Content by Type</h4>
                  <div className="space-y-2">
                    {Object.entries(stats.by_type || {}).map(([k, v]) => (
                      <Bar key={k} label={TYPES.find(t=>t.key===k)?.label || k.replace('_',' ')} value={v} max={stats.total_notices} />
                    ))}
                  </div>
                </div>
                <div className="bg-white rounded-xl border border-purple-100 p-5">
                  <h4 className="font-bold text-purple-900 mb-3 text-sm">Content by Category</h4>
                  <div className="space-y-2">
                    {Object.entries(stats.by_category || {}).map(([k, v]) => (
                      <Bar key={k} label={k} value={v} max={stats.total_notices} />
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="ads" className="mt-4">
          <div className="bg-white rounded-xl border border-purple-100 p-5 space-y-5">
            <div>
              <h3 className="font-semibold text-purple-900 flex items-center gap-2"><Megaphone className="w-4 h-4" /> Ad Settings</h3>
              <p className="text-xs text-gray-500 mt-1">Control where AdSense placeholders render across the public site. Admin routes (/admin/*) are always ad-free.</p>
            </div>

            <div className="flex items-center justify-between p-4 bg-purple-50 border border-purple-100 rounded-lg">
              <div>
                <Label htmlFor="ads-toggle" className="text-sm font-semibold text-purple-900">Enable ads site-wide</Label>
                <p className="text-xs text-gray-600 mt-0.5">Master switch. When off, no AdSlot renders anywhere on the site.</p>
              </div>
              <Switch id="ads-toggle" checked={adsEnabled} onCheckedChange={setAdsEnabled} />
            </div>

            <div>
              <Label htmlFor="ads-paths" className="text-sm font-semibold text-purple-900">Disable ads on these paths</Label>
              <p className="text-xs text-gray-600 mt-0.5 mb-2">One path per line. Matches the path exactly or any sub-path (e.g. <code>/privacy</code> covers <code>/privacy</code> and <code>/privacy/anything</code>).</p>
              <Textarea
                id="ads-paths"
                rows={6}
                value={adsDisabledPathsText}
                onChange={(e) => setAdsDisabledPathsText(e.target.value)}
                className="font-mono text-sm"
                placeholder="/privacy&#10;/terms&#10;/disclaimer"
              />
              <div className="mt-2 text-xs text-gray-500">
                Defaults exclude the legal pages and contact form. Add or remove paths as needed.
              </div>
            </div>

            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
              <strong>Note:</strong> Real AdSense scripts only load after a visitor accepts cookies AND the publisher ID is set
              in <code>ConsentScripts.jsx</code>. Until then, AdSlot renders a labelled placeholder. Apply for AdSense approval
              once the site has substantial original content.
            </div>

            <div className="flex justify-end">
              <Button onClick={saveAdSettings} disabled={adsSaving} className="bg-purple-700 hover:bg-purple-800">
                {adsSaving ? 'Saving...' : 'Save Ad Settings'}
              </Button>
            </div>
          </div>

          {/* Search Console verification token */}
          <div className="bg-white rounded-xl border border-purple-100 p-5 mt-4 space-y-4">
            <div>
              <h3 className="font-semibold text-purple-900 flex items-center gap-2"><Shield className="w-4 h-4" /> Google Search Console Verification</h3>
              <p className="text-xs text-gray-500 mt-1">
                Paste the content value from the meta-tag verification method in Search Console. We inject it as{' '}
                <code className="text-[11px]">&lt;meta name=&quot;google-site-verification&quot; content=&quot;...&quot;&gt;</code>{' '}
                on every public page.
              </p>
            </div>
            <div>
              <Label htmlFor="sc-token" className="text-xs">Verification token (content attribute value only)</Label>
              <Input
                id="sc-token"
                value={scToken}
                onChange={(e) => setScToken(e.target.value)}
                placeholder="e.g. abcDEF123_xyz...   (NOT the whole meta tag)"
                className="mt-1 font-mono text-sm"
              />
              <div className="mt-1 text-[11px] text-gray-500">
                Find it in Search Console → Settings → Ownership verification → HTML tag → copy the value inside{' '}
                <code>content=&quot;…&quot;</code>.
              </div>
            </div>
            <div className="rounded-lg border border-purple-100 bg-purple-50 p-3 text-xs text-purple-900">
              <strong>After saving:</strong> the meta tag will appear in <code>&lt;head&gt;</code> within a few seconds on every public page. Then go back to Search Console and click <em>Verify</em>. Then submit the sitemap URL <code>/api/sitemap.xml</code> in Search Console &rarr; Sitemaps.
            </div>
            <div className="flex justify-end">
              <Button onClick={saveScToken} disabled={scSaving} className="bg-purple-700 hover:bg-purple-800">
                {scSaving ? 'Saving...' : 'Save Verification Token'}
              </Button>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="activity" className="mt-4">
          <div className="bg-white rounded-xl border border-purple-100 p-4">
            <h3 className="font-semibold text-purple-900 mb-1 flex items-center gap-2"><Shield className="w-4 h-4" /> Login Activity</h3>
            <p className="text-xs text-gray-500 mb-4">Last {activity.length} login attempts. Failed attempts &amp; account lockouts are tracked here.</p>
            <div className="overflow-x-auto -mx-4 sm:mx-0">
              <table className="w-full text-sm min-w-[640px]">
                <thead className="bg-purple-50 text-purple-900">
                  <tr>
                    <th className="text-left px-3 py-2">Time</th>
                    <th className="text-left px-3 py-2">Username</th>
                    <th className="text-left px-3 py-2">IP Address</th>
                    <th className="text-left px-3 py-2">Status</th>
                    <th className="text-left px-3 py-2">Reason</th>
                    <th className="text-left px-3 py-2">Browser</th>
                  </tr>
                </thead>
                <tbody>
                  {activity.map(a => (
                    <tr key={a.id} className="border-b border-purple-50">
                      <td className="px-3 py-2 whitespace-nowrap text-xs">{new Date(a.timestamp).toLocaleString()}</td>
                      <td className="px-3 py-2 font-medium">{a.username}</td>
                      <td className="px-3 py-2 font-mono text-xs">{a.ip}</td>
                      <td className="px-3 py-2">{a.success ? <Badge className="bg-emerald-100 text-emerald-800 border-0"><Check className="w-3 h-3 mr-1" />Success</Badge> : <Badge className="bg-red-100 text-red-800 border-0"><XCircle className="w-3 h-3 mr-1" />Failed</Badge>}</td>
                      <td className="px-3 py-2 text-xs text-gray-700">{(a.reason||'').replace(/_/g,' ')}</td>
                      <td className="px-3 py-2 text-xs text-gray-500 max-w-[260px] truncate">{a.user_agent}</td>
                    </tr>
                  ))}
                  {activity.length === 0 && <tr><td colSpan={6} className="text-center py-6 text-gray-500">No login activity yet</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* CRUD dialog with conditional fields */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editing ? `Edit ${typeLabel}` : `Add New ${typeLabel}`}</DialogTitle>
          </DialogHeader>

          {/* Common fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Field label="Type *">
              <Select value={form.type} onValueChange={v=>setForm({...form, type: v})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>{TYPES.map(t => <SelectItem key={t.key} value={t.key}>{t.label}</SelectItem>)}</SelectContent>
              </Select>
            </Field>
            <Field label="Category">
              <Select value={form.category} onValueChange={v=>setForm({...form, category: v})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>{CATEGORIES.map(c => <SelectItem key={c.key} value={c.key}>{c.label}</SelectItem>)}</SelectContent>
              </Select>
            </Field>
            <Field label="Title *" full><Input value={form.title} onChange={e=>setForm({...form, title: e.target.value})} /></Field>
            <Field label="Organization *"><Input value={form.organization} onChange={e=>setForm({...form, organization: e.target.value})} /></Field>
            <Field label="District">
              <Select value={form.district} onValueChange={v=>setForm({...form, district: v})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent className="max-h-72">{DISTRICTS.map(d => <SelectItem key={d} value={d}>{d}</SelectItem>)}</SelectContent>
              </Select>
            </Field>
            <Field label="Location text"><Input value={form.location} onChange={e=>setForm({...form, location: e.target.value})} /></Field>
            <Field label="Thumbnail URL"><Input value={form.thumbnail} onChange={e=>setForm({...form, thumbnail: e.target.value})} /></Field>
            <Field label="Description *" full><Textarea rows={3} value={form.description} onChange={e=>setForm({...form, description: e.target.value})} /></Field>
          </div>

          {/* Conditional fields */}
          <div className="mt-5">
            <div className="text-xs uppercase tracking-wider text-purple-700 font-bold mb-3 flex items-center gap-2">
              <span className="h-px bg-purple-200 flex-1"></span>
              {typeLabel} Details
              <span className="h-px bg-purple-200 flex-1"></span>
            </div>
            {isJobType ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Field label="No. of Vacancies"><Input value={form.vacancy_count} onChange={e=>setForm({...form, vacancy_count: e.target.value})} placeholder="e.g., 1200" /></Field>
                <Field label="Salary"><Input value={form.salary} onChange={e=>setForm({...form, salary: e.target.value})} /></Field>
                <Field label="Eligibility" full><Textarea rows={2} value={form.eligibility} onChange={e=>setForm({...form, eligibility: e.target.value})} placeholder="Qualification, experience requirements" /></Field>
                <Field label="Age Limit"><Input value={form.age_limit} onChange={e=>setForm({...form, age_limit: e.target.value})} /></Field>
                <Field label="Application Fee"><Input value={form.application_fee} onChange={e=>setForm({...form, application_fee: e.target.value})} /></Field>
                <Field label="Start Date"><Input value={form.start_date} onChange={e=>setForm({...form, start_date: e.target.value})} placeholder="01 July 2025" /></Field>
                <Field label="Last Date"><Input value={form.last_date} onChange={e=>setForm({...form, last_date: e.target.value})} placeholder="31 July 2025" /></Field>
                <Field label="Selection Process" full><Textarea rows={2} value={form.selection_process} onChange={e=>setForm({...form, selection_process: e.target.value})} /></Field>
                <Field label="How to Apply" full><Textarea rows={2} value={form.how_to_apply} onChange={e=>setForm({...form, how_to_apply: e.target.value})} /></Field>
                <Field label="Apply Link"><Input value={form.apply_link} onChange={e=>setForm({...form, apply_link: e.target.value})} /></Field>
                <Field label="Official Notification Link"><Input value={form.notification_link} onChange={e=>setForm({...form, notification_link: e.target.value})} /></Field>
                <Field label="Official Website" full><Input value={form.official_website} onChange={e=>setForm({...form, official_website: e.target.value})} /></Field>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Field label="Notice Date"><Input value={form.notice_date} onChange={e=>setForm({...form, notice_date: e.target.value})} placeholder="15 July 2025" /></Field>
                <Field label="Important Date (optional)"><Input value={form.last_date} onChange={e=>setForm({...form, last_date: e.target.value})} placeholder="e.g., Exam date / Objection window" /></Field>
                <Field label="Linked Job" full>
                  <Select value={form.linked_job_id || '__none__'} onValueChange={v=>setForm({...form, linked_job_id: v === '__none__' ? null : v})}>
                    <SelectTrigger><SelectValue placeholder="Select related job notification (optional)" /></SelectTrigger>
                    <SelectContent className="max-h-72">
                      <SelectItem value="__none__">No linked job</SelectItem>
                      {linkableJobs.map(j => <SelectItem key={j.id} value={j.id}>{j.title.slice(0, 70)}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </Field>
                <Field label="Download Link" full><Input value={form.download_link} onChange={e=>setForm({...form, download_link: e.target.value})} placeholder="https://..." /></Field>
                <Field label="Official Website" full><Input value={form.official_website} onChange={e=>setForm({...form, official_website: e.target.value})} /></Field>
              </div>
            )}
            <div className="mt-4 flex items-center gap-3">
              <Switch checked={form.is_featured} onCheckedChange={v=>setForm({...form, is_featured: v})} />
              <Label>Mark as Featured</Label>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={()=>setOpen(false)}>Cancel</Button>
            <Button onClick={save} className="bg-purple-700 hover:bg-purple-800">{editing ? 'Update' : 'Create'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Password change dialog */}
      <Dialog open={pwdOpen} onOpenChange={setPwdOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Change Password</DialogTitle></DialogHeader>
          <form onSubmit={submitPasswordChange} className="space-y-3">
            <div><Label htmlFor="oldp">Current Password</Label><Input id="oldp" type="password" value={pwdForm.old} onChange={e=>setPwdForm({...pwdForm, old: e.target.value})} className="mt-1" /></div>
            <div><Label htmlFor="new1">New Password</Label><Input id="new1" type="password" value={pwdForm.new1} onChange={e=>setPwdForm({...pwdForm, new1: e.target.value})} className="mt-1" placeholder="At least 8 characters" /></div>
            <div><Label htmlFor="new2">Confirm New Password</Label><Input id="new2" type="password" value={pwdForm.new2} onChange={e=>setPwdForm({...pwdForm, new2: e.target.value})} className="mt-1" /></div>
            {pwdErr && <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded p-2">{pwdErr}</div>}
            <DialogFooter>
              <Button type="button" variant="outline" onClick={()=>setPwdOpen(false)}>Cancel</Button>
              <Button type="submit" className="bg-purple-700 hover:bg-purple-800">Update</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value }) => (
  <div className="bg-white rounded-xl border border-purple-100 p-4 flex items-center gap-3">
    <div className="w-11 h-11 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center flex-shrink-0"><Icon className="w-5 h-5" /></div>
    <div className="min-w-0">
      <div className="text-2xl font-extrabold text-purple-900">{value}</div>
      <div className="text-xs text-gray-600 uppercase tracking-wide truncate">{label}</div>
    </div>
  </div>
);

const Field = ({ label, children, full }) => (
  <div className={full ? 'md:col-span-2' : ''}>
    <Label className="text-xs">{label}</Label>
    <div className="mt-1">{children}</div>
  </div>
);

const Bar = ({ label, value, max }) => {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div>
      <div className="flex justify-between text-xs text-gray-700 mb-1"><span className="capitalize font-medium">{label}</span><span>{value}</span></div>
      <div className="h-2 bg-purple-100 rounded-full overflow-hidden"><div className="h-full bg-purple-600" style={{ width: `${pct}%` }} /></div>
    </div>
  );
};

export default AdminDashboard;
