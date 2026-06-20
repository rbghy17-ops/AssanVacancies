import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { fetchJobs, fetchStats, createJob, updateJob, deleteJob, listContacts, deleteContact } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Switch } from '../components/ui/switch';
import { LogOut, Plus, Pencil, Trash2, Briefcase, BarChart3, Mail, Users, FileText, Search } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const CATS = ['govt', 'private', 'defence', 'banking', 'railway', 'teaching', 'police'];
const TYPES = ['recruitment', 'admit_card', 'result', 'answer_key', 'admission', 'scholarship'];

const emptyJob = {
  title: '', organization: '', category: 'govt', job_type: 'recruitment',
  description: '', qualification: '', age_limit: '', application_fee: '',
  vacancy_count: '', salary: '', location: 'Assam', last_date: '', start_date: '',
  apply_link: '', notification_link: '', official_website: '', thumbnail: '',
  how_to_apply: '', selection_process: '', is_featured: false,
};

const AdminDashboard = () => {
  const { user, loading: authLoading, logout } = useAuth();
  const nav = useNavigate();
  const [stats, setStats] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [search, setSearch] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyJob);

  useEffect(() => {
    if (!authLoading && !user) nav('/admin/login');
  }, [user, authLoading, nav]);

  const refresh = () => {
    fetchStats().then(setStats);
    fetchJobs({ limit: 200, search: search || undefined }).then(r => setJobs(r.jobs || []));
    listContacts().then(setContacts).catch(() => {});
  };

  useEffect(() => { if (user) refresh(); }, [user]);
  useEffect(() => { if (user) { const t = setTimeout(() => fetchJobs({ limit: 200, search: search || undefined }).then(r => setJobs(r.jobs || [])), 300); return () => clearTimeout(t); } }, [search, user]);

  const openNew = () => { setEditing(null); setForm(emptyJob); setOpen(true); };
  const openEdit = (j) => { setEditing(j); setForm({ ...emptyJob, ...j }); setOpen(true); };

  const save = async () => {
    if (!form.title || !form.organization || !form.description) {
      toast({ title: 'Please fill title, organization, description' }); return;
    }
    try {
      if (editing) {
        await updateJob(editing.id, form);
        toast({ title: 'Job updated' });
      } else {
        await createJob(form);
        toast({ title: 'Job created' });
      }
      setOpen(false);
      refresh();
    } catch (e) {
      toast({ title: 'Save failed', description: String(e?.message || e) });
    }
  };

  const remove = async (j) => {
    if (!window.confirm(`Delete "${j.title}"?`)) return;
    await deleteJob(j.id);
    toast({ title: 'Deleted' });
    refresh();
  };

  const removeContact = async (c) => {
    if (!window.confirm('Delete this message?')) return;
    await deleteContact(c.id);
    refresh();
  };

  if (authLoading) return <div className="text-center py-20">Loading...</div>;
  if (!user) return null;

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-extrabold text-purple-900 title-font">Admin Dashboard</h1>
          <p className="text-sm text-gray-600">Welcome back, {user.username}</p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/" className="text-sm text-purple-700 hover:underline">View Site</Link>
          <Button variant="outline" onClick={() => { logout(); nav('/admin/login'); }} className="border-purple-300">
            <LogOut className="w-4 h-4 mr-1" /> Logout
          </Button>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard icon={Briefcase} label="Total Jobs" value={stats.total_jobs} />
          <StatCard icon={FileText} label="Recruitments" value={stats.by_type?.recruitment || 0} />
          <StatCard icon={BarChart3} label="Results" value={stats.by_type?.result || 0} />
          <StatCard icon={Mail} label="Messages" value={stats.messages || 0} />
        </div>
      )}

      <Tabs defaultValue="jobs">
        <TabsList className="bg-purple-100">
          <TabsTrigger value="jobs">Jobs</TabsTrigger>
          <TabsTrigger value="messages">Messages</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="jobs" className="mt-4">
          <div className="bg-white rounded-xl border border-purple-100 p-4">
            <div className="flex flex-col md:flex-row md:items-center gap-3 mb-4">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3 top-3 text-purple-500" />
                <Input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search jobs by title or organization" className="pl-9" />
              </div>
              <Button onClick={openNew} className="bg-purple-700 hover:bg-purple-800"><Plus className="w-4 h-4 mr-1" /> Add Job</Button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-purple-50 text-purple-900">
                  <tr>
                    <th className="text-left px-3 py-2">Title</th>
                    <th className="text-left px-3 py-2">Category</th>
                    <th className="text-left px-3 py-2">Type</th>
                    <th className="text-left px-3 py-2">Last Date</th>
                    <th className="text-left px-3 py-2">Views</th>
                    <th className="text-right px-3 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map(j => (
                    <tr key={j.id} className="border-b border-purple-50 hover:bg-purple-50/40">
                      <td className="px-3 py-2 max-w-md truncate">
                        {j.is_featured && <span className="text-purple-700 mr-1">★</span>}
                        {j.title}
                      </td>
                      <td className="px-3 py-2 capitalize">{j.category}</td>
                      <td className="px-3 py-2 capitalize">{j.job_type?.replace('_',' ')}</td>
                      <td className="px-3 py-2">{j.last_date || '—'}</td>
                      <td className="px-3 py-2">{j.views || 0}</td>
                      <td className="px-3 py-2 text-right">
                        <Button size="sm" variant="outline" onClick={()=>openEdit(j)} className="mr-1 border-purple-300"><Pencil className="w-3.5 h-3.5" /></Button>
                        <Button size="sm" variant="outline" onClick={()=>remove(j)} className="text-red-600 border-red-200 hover:bg-red-50"><Trash2 className="w-3.5 h-3.5" /></Button>
                      </td>
                    </tr>
                  ))}
                  {jobs.length === 0 && <tr><td colSpan={6} className="text-center py-6 text-gray-500">No jobs</td></tr>}
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
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-purple-900">{c.name} <span className="text-xs text-gray-500">&lt;{c.email}&gt;</span></div>
                      <div className="text-xs text-gray-500">{c.subject || '(no subject)'} • {new Date(c.created_at).toLocaleString()}</div>
                    </div>
                    <Button size="sm" variant="outline" onClick={()=>removeContact(c)} className="text-red-600 border-red-200"><Trash2 className="w-3.5 h-3.5" /></Button>
                  </div>
                  <p className="text-sm text-gray-700 mt-2 whitespace-pre-line">{c.message}</p>
                </div>
              ))}
              {contacts.length === 0 && <div className="text-center text-gray-500 py-6">No messages yet</div>}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="mt-4">
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded-xl border border-purple-100 p-5">
                <h3 className="font-bold text-purple-900 mb-3">By Category</h3>
                <div className="space-y-2">
                  {Object.entries(stats.by_category).map(([k, v]) => (
                    <Bar key={k} label={k} value={v} max={stats.total_jobs} />
                  ))}
                </div>
              </div>
              <div className="bg-white rounded-xl border border-purple-100 p-5">
                <h3 className="font-bold text-purple-900 mb-3">By Type</h3>
                <div className="space-y-2">
                  {Object.entries(stats.by_type).map(([k, v]) => (
                    <Bar key={k} label={k.replace('_',' ')} value={v} max={stats.total_jobs} />
                  ))}
                </div>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editing ? 'Edit Job' : 'Add New Job'}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Field label="Title *"><Input value={form.title} onChange={e=>setForm({...form, title: e.target.value})} /></Field>
            <Field label="Organization *"><Input value={form.organization} onChange={e=>setForm({...form, organization: e.target.value})} /></Field>
            <Field label="Category">
              <Select value={form.category} onValueChange={v=>setForm({...form, category: v})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>{CATS.map(c => <SelectItem key={c} value={c} className="capitalize">{c}</SelectItem>)}</SelectContent>
              </Select>
            </Field>
            <Field label="Type">
              <Select value={form.job_type} onValueChange={v=>setForm({...form, job_type: v})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>{TYPES.map(c => <SelectItem key={c} value={c} className="capitalize">{c.replace('_',' ')}</SelectItem>)}</SelectContent>
              </Select>
            </Field>
            <Field label="Vacancies"><Input value={form.vacancy_count} onChange={e=>setForm({...form, vacancy_count: e.target.value})} /></Field>
            <Field label="Salary"><Input value={form.salary} onChange={e=>setForm({...form, salary: e.target.value})} /></Field>
            <Field label="Qualification"><Input value={form.qualification} onChange={e=>setForm({...form, qualification: e.target.value})} /></Field>
            <Field label="Age Limit"><Input value={form.age_limit} onChange={e=>setForm({...form, age_limit: e.target.value})} /></Field>
            <Field label="Application Fee"><Input value={form.application_fee} onChange={e=>setForm({...form, application_fee: e.target.value})} /></Field>
            <Field label="Location"><Input value={form.location} onChange={e=>setForm({...form, location: e.target.value})} /></Field>
            <Field label="Start Date"><Input value={form.start_date} onChange={e=>setForm({...form, start_date: e.target.value})} placeholder="01 July 2025" /></Field>
            <Field label="Last Date"><Input value={form.last_date} onChange={e=>setForm({...form, last_date: e.target.value})} placeholder="31 July 2025" /></Field>
            <Field label="Apply Link"><Input value={form.apply_link} onChange={e=>setForm({...form, apply_link: e.target.value})} /></Field>
            <Field label="Notification Link"><Input value={form.notification_link} onChange={e=>setForm({...form, notification_link: e.target.value})} /></Field>
            <Field label="Official Website"><Input value={form.official_website} onChange={e=>setForm({...form, official_website: e.target.value})} /></Field>
            <Field label="Thumbnail URL"><Input value={form.thumbnail} onChange={e=>setForm({...form, thumbnail: e.target.value})} /></Field>
            <Field label="Description *" full><Textarea rows={3} value={form.description} onChange={e=>setForm({...form, description: e.target.value})} /></Field>
            <Field label="How to Apply" full><Textarea rows={2} value={form.how_to_apply} onChange={e=>setForm({...form, how_to_apply: e.target.value})} /></Field>
            <Field label="Selection Process" full><Textarea rows={2} value={form.selection_process} onChange={e=>setForm({...form, selection_process: e.target.value})} /></Field>
            <div className="md:col-span-2 flex items-center gap-3">
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
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value }) => (
  <div className="bg-white rounded-xl border border-purple-100 p-4 flex items-center gap-3">
    <div className="w-11 h-11 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center"><Icon className="w-5 h-5" /></div>
    <div>
      <div className="text-2xl font-extrabold text-purple-900">{value}</div>
      <div className="text-xs text-gray-600 uppercase tracking-wide">{label}</div>
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
