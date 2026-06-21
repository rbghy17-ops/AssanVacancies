import React, { useEffect, useState, useMemo } from 'react';
import {
  aggSources, aggCreateSource, aggUpdateSource, aggDeleteSource,
  aggRunSource, aggRunAll, aggRuns, aggDrafts,
  aggApproveDraft, aggRejectDraft, aggBulkDrafts,
  aggGetSettings, aggUpdateSettings,
} from '../lib/api';
import api from '../lib/api';import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from '../hooks/use-toast';
import {
  Plus, Pencil, Trash2, Play, ExternalLink, CheckCircle2, XCircle,
  Loader2, AlertCircle, RefreshCw, RotateCcw, ArrowUp, ArrowDown, Undo2,
} from 'lucide-react';

const TYPES = [
  { key: 'job', label: 'Job' },
  { key: 'admit_card', label: 'Admit Card' },
  { key: 'result', label: 'Result' },
  { key: 'answer_key', label: 'Answer Key' },
];
const CATEGORIES = ['govt', 'private', 'defence', 'banking', 'railway', 'teaching', 'police'];

const emptySource = {
  name: '', base_url: '', list_url: '',
  enabled: true, default_type: 'job', default_category: 'govt',
  default_district: 'Kamrup Metropolitan', notes: '',
};

const LEVEL_META = {
  new: { label: 'New', cls: 'bg-gray-100 text-gray-700 border-gray-300', dot: 'bg-gray-400' },
  probationary: { label: 'Probationary', cls: 'bg-amber-100 text-amber-800 border-amber-200', dot: 'bg-amber-500' },
  trusted: { label: 'Trusted', cls: 'bg-emerald-100 text-emerald-800 border-emerald-200', dot: 'bg-emerald-500' },
};
const NEXT_GOAL = { new: 10, probationary: 25, trusted: null };

const LevelBadge = ({ level }) => {
  const meta = LEVEL_META[level] || LEVEL_META.new;
  return (
    <Badge className={`${meta.cls} border text-xs inline-flex items-center gap-1.5`} data-testid={`level-badge-${level}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${meta.dot}`}></span>
      {meta.label}
    </Badge>
  );
};

const HighConfidenceFlag = ({ level }) => {
  if (level !== 'probationary') return null;
  return (
    <Badge className="bg-amber-50 text-amber-800 border border-amber-200 text-[10px] ml-2" data-testid="hc-flag">
      ⚡ high confidence
    </Badge>
  );
};

const emptyDraftEdit = {
  title: '', description: '', vacancy_count: '', last_date: '',
  application_fee: '', eligibility: '', apply_link: '', notification_link: '',
};

export default function AggregatorPanel() {
  const [sources, setSources] = useState([]);
  const [runs, setRuns] = useState([]);
  const [drafts, setDrafts] = useState([]);
  const [draftsTotal, setDraftsTotal] = useState(0);
  const [settings, setSettings] = useState({ enabled: false, interval_hours: 24 });
  const [loading, setLoading] = useState(false);
  const [sourceFilter, setSourceFilter] = useState('all');
  const [selectedIds, setSelectedIds] = useState([]);

  // Source dialog
  const [srcDialogOpen, setSrcDialogOpen] = useState(false);
  const [srcEditing, setSrcEditing] = useState(null);
  const [srcForm, setSrcForm] = useState(emptySource);

  // Draft edit dialog
  const [draftDialogOpen, setDraftDialogOpen] = useState(false);
  const [draftEditing, setDraftEditing] = useState(null);
  const [draftForm, setDraftForm] = useState(emptyDraftEdit);

  // Run-source spinner per row
  const [runningId, setRunningId] = useState(null);
  const [runAllBusy, setRunAllBusy] = useState(false);

  // Auto-publish log
  const [autoLog, setAutoLog] = useState([]);

  const refreshAutoLog = async () => {
    try {
      const r = await api.get('/admin/aggregator/auto-publish-log?limit=100');
      setAutoLog(r.data?.items || []);
    } catch (e) { /* noop */ }
  };
  const undoAuto = async (n) => {
    if (!window.confirm(`Undo auto-publish of "${n.title.slice(0, 80)}"?\nNotice will be deleted and the source demoted back to Probationary.`)) return;
    try {
      await api.post(`/admin/aggregator/auto-publish/${n.id}/undo`);
      toast({ title: 'Auto-publish undone', description: 'Source demoted to Probationary' });
      refreshAutoLog();
      refreshAll();
    } catch (e) { toast({ title: 'Undo failed', variant: 'destructive' }); }
  };

  const refreshAll = async () => {
    setLoading(true);
    try {
      const [s, r, st] = await Promise.all([aggSources(), aggRuns(25), aggGetSettings()]);
      setSources(s); setRuns(r); setSettings(st);
      await refreshDrafts(sourceFilter);
      await refreshAutoLog();
    } catch (e) {
      toast({ title: 'Failed to load aggregator data', variant: 'destructive' });
    }
    finally { setLoading(false); }
  };

  const refreshDrafts = async (sf = sourceFilter) => {
    try {
      const params = { limit: 100 };
      if (sf && sf !== 'all') params.source_id = sf;
      const d = await aggDrafts(params);
      setDrafts(d.drafts || []);
      setDraftsTotal(d.total || 0);
      setSelectedIds([]);
    } catch (e) {
      toast({ title: 'Failed to load drafts', variant: 'destructive' });
    }
  };

  useEffect(() => { refreshAll(); /* eslint-disable-next-line */ }, []);
  useEffect(() => { refreshDrafts(sourceFilter); /* eslint-disable-next-line */ }, [sourceFilter]);

  // ---------- Sources ----------
  const openNewSource = () => { setSrcEditing(null); setSrcForm(emptySource); setSrcDialogOpen(true); };
  const openEditSource = (s) => {
    setSrcEditing(s);
    setSrcForm({
      name: s.name || '', base_url: s.base_url || '', list_url: s.list_url || '',
      enabled: s.enabled !== false, default_type: s.default_type || 'job',
      default_category: s.default_category || 'govt',
      default_district: s.default_district || 'Kamrup Metropolitan',
      notes: s.notes || '',
    });
    setSrcDialogOpen(true);
  };
  const setLevel = async (s, level) => {
    if (!window.confirm(`Change trust level of "${s.name}" to ${level}? This is an admin override.`)) return;
    try {
      await api.post(`/admin/aggregator/sources/${s.id}/set-trust-level`, { trust_level: level, reason: 'admin override' });
      toast({ title: `Set to ${level}`, description: s.name });
      refreshAll();
    } catch (e) {
      toast({ title: 'Override failed', variant: 'destructive' });
    }
  };
  const resetTrust = async (s) => {
    if (!window.confirm(`Reset counters for "${s.name}"? Trust level stays the same.`)) return;
    try {
      await api.post(`/admin/aggregator/sources/${s.id}/reset-trust`);
      toast({ title: 'Counters reset' });
      refreshAll();
    } catch (e) {
      toast({ title: 'Reset failed', variant: 'destructive' });
    }
  };
  const saveSource = async () => {
    try {
      if (srcEditing) await aggUpdateSource(srcEditing.id, srcForm);
      else await aggCreateSource(srcForm);
      toast({ title: srcEditing ? 'Source updated' : 'Source added' });
      setSrcDialogOpen(false);
      refreshAll();
    } catch (e) {
      toast({ title: 'Save failed', description: e?.response?.data?.detail || 'Try again', variant: 'destructive' });
    }
  };
  const deleteSource = async (s) => {
    if (!window.confirm(`Delete source "${s.name}"? Existing drafts stay.`)) return;
    await aggDeleteSource(s.id);
    toast({ title: 'Source deleted' });
    refreshAll();
  };
  const runOne = async (s) => {
    setRunningId(s.id);
    try {
      const r = await aggRunSource(s.id);
      toast({ title: `${s.name}: ${r.new_drafts} new draft(s)`,
              description: r.parse_failed ? `Failed: ${r.errors?.[0] || ''}` : `Fetched ${r.fetched}, dup ${r.skipped_url_dup}+${r.skipped_fuzzy_dup}` });
    } catch (e) {
      toast({ title: 'Run failed', variant: 'destructive' });
    }
    setRunningId(null);
    refreshAll();
  };
  const runAll = async () => {
    setRunAllBusy(true);
    try {
      const r = await aggRunAll();
      const total = (r.runs || []).reduce((s, x) => s + (x.new_drafts || 0), 0);
      toast({ title: `Aggregator finished`, description: `${r.sources_checked} source(s), ${total} new draft(s).` });
    } catch (e) { toast({ title: 'Run-all failed', variant: 'destructive' }); }
    setRunAllBusy(false);
    refreshAll();
  };

  // ---------- Settings ----------
  const saveSettings = async (next) => {
    try {
      const s = await aggUpdateSettings(next);
      setSettings(s);
      toast({ title: 'Scheduler updated', description: `${s.enabled ? 'ON' : 'OFF'} • every ${s.interval_hours}h` });
    } catch (e) {
      toast({ title: 'Update failed', variant: 'destructive' });
    }
  };

  // ---------- Drafts ----------
  const toggleSelect = (id) => {
    setSelectedIds((prev) => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };
  const toggleSelectAll = () => {
    setSelectedIds((prev) => prev.length === drafts.length ? [] : drafts.map(d => d.id));
  };
  const approveOne = async (d) => {
    try {
      await aggApproveDraft(d.id);
      toast({ title: 'Approved & published', description: d.title.slice(0, 80) });
      refreshDrafts();
    } catch (e) {
      toast({ title: 'Approve failed', variant: 'destructive' });
    }
  };
  const rejectOne = async (d) => {
    if (!window.confirm('Reject and delete this draft?')) return;
    try {
      await aggRejectDraft(d.id);
      toast({ title: 'Rejected' });
      refreshDrafts();
    } catch (e) {
      toast({ title: 'Reject failed', variant: 'destructive' });
    }
  };
  const bulkAction = async (action) => {
    if (selectedIds.length === 0) return;
    if (action === 'reject' && !window.confirm(`Reject ${selectedIds.length} draft(s)?`)) return;
    try {
      const r = await aggBulkDrafts({ ids: selectedIds, action });
      toast({ title: `Bulk ${action} done`, description: `${r.affected} item(s) affected` });
      refreshDrafts();
    } catch (e) {
      toast({ title: `Bulk ${action} failed`, variant: 'destructive' });
    }
  };
  const openEditDraft = (d) => {
    setDraftEditing(d);
    setDraftForm({
      title: d.title || '', description: d.description || '',
      vacancy_count: d.vacancy_count || '', last_date: d.last_date || '',
      application_fee: d.application_fee || '', eligibility: d.eligibility || '',
      apply_link: d.apply_link || '', notification_link: d.notification_link || '',
    });
    setDraftDialogOpen(true);
  };
  const saveDraftEdit = async () => {
    try {
      await api.put(`/admin/notices/${draftEditing.id}`, draftForm);
      toast({ title: 'Draft updated' });
      setDraftDialogOpen(false);
      refreshDrafts();
    } catch (e) {
      toast({ title: 'Save failed', variant: 'destructive' });
    }
  };

  const sourcesById = useMemo(() => Object.fromEntries(sources.map(s => [s.id, s])), [sources]);

  return (
    <div className="space-y-4" data-testid="aggregator-panel">
      <Tabs defaultValue="review">
        <TabsList className="bg-purple-100 flex flex-wrap h-auto">
          <TabsTrigger value="review" data-testid="agg-tab-review">
            Review Queue <Badge className="ml-2 bg-purple-700 text-white">{draftsTotal}</Badge>
          </TabsTrigger>
          <TabsTrigger value="sources" data-testid="agg-tab-sources">Sources ({sources.length})</TabsTrigger>
          <TabsTrigger value="autolog" data-testid="agg-tab-autolog">
            Auto-publish log <Badge className="ml-2 bg-emerald-700 text-white">{autoLog.length}</Badge>
          </TabsTrigger>
          <TabsTrigger value="runs" data-testid="agg-tab-runs">Run Log</TabsTrigger>
          <TabsTrigger value="settings" data-testid="agg-tab-settings">Scheduler</TabsTrigger>
        </TabsList>

        {/* REVIEW QUEUE */}
        <TabsContent value="review" className="mt-4">
          <div className="bg-white rounded-xl border border-purple-100 p-4">
            <div className="flex flex-col md:flex-row md:items-center gap-3 mb-3">
              <div className="flex items-center gap-2 flex-1">
                <Label className="text-xs text-purple-900">Filter by source</Label>
                <Select value={sourceFilter} onValueChange={setSourceFilter}>
                  <SelectTrigger className="w-72" data-testid="agg-drafts-source-filter"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All sources</SelectItem>
                    {sources.map(s => <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => refreshDrafts()} className="border-purple-300" data-testid="agg-drafts-refresh">
                  <RefreshCw className="w-3.5 h-3.5 mr-1" /> Refresh
                </Button>
                <Button size="sm" onClick={() => bulkAction('approve')}
                        disabled={!selectedIds.length}
                        className="bg-emerald-600 hover:bg-emerald-700" data-testid="agg-bulk-approve-btn">
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Approve ({selectedIds.length})
                </Button>
                <Button size="sm" variant="outline" onClick={() => bulkAction('reject')}
                        disabled={!selectedIds.length}
                        className="text-red-600 border-red-300 hover:bg-red-50" data-testid="agg-bulk-reject-btn">
                  <XCircle className="w-3.5 h-3.5 mr-1" /> Reject ({selectedIds.length})
                </Button>
              </div>
            </div>

            <div className="overflow-x-auto -mx-4 sm:mx-0">
              <table className="w-full text-sm min-w-[860px]">
                <thead className="bg-purple-50 text-purple-900">
                  <tr>
                    <th className="px-3 py-2 w-10"><input type="checkbox"
                      checked={drafts.length > 0 && selectedIds.length === drafts.length}
                      onChange={toggleSelectAll}
                      data-testid="agg-drafts-select-all" /></th>
                    <th className="text-left px-3 py-2">Title / source</th>
                    <th className="text-left px-3 py-2">Facts</th>
                    <th className="text-left px-3 py-2">Last date</th>
                    <th className="text-right px-3 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {drafts.map(d => (
                    <tr key={d.id} className="border-b border-purple-50 hover:bg-purple-50/40" data-testid={`agg-draft-row-${d.id}`}>
                      <td className="px-3 py-2 align-top">
                        <input type="checkbox" checked={selectedIds.includes(d.id)}
                               onChange={() => toggleSelect(d.id)}
                               data-testid={`agg-draft-select-${d.id}`} />
                      </td>
                      <td className="px-3 py-2 align-top max-w-md">
                        <div className="font-medium text-purple-900 inline-flex items-center">
                          {d.title}
                          <HighConfidenceFlag level={d.source_trust_level} />
                        </div>
                        <div className="text-xs text-gray-500 mt-0.5">
                          {sourcesById[d.source_id]?.name || d.source_name || '—'}
                          {d.source_url && (
                            <a href={d.source_url} target="_blank" rel="noopener noreferrer"
                               className="ml-2 text-purple-700 hover:underline inline-flex items-center"
                               data-testid={`agg-draft-source-link-${d.id}`}>
                              source <ExternalLink className="w-3 h-3 ml-1" />
                            </a>
                          )}
                        </div>
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">{d.description}</p>
                      </td>
                      <td className="px-3 py-2 align-top text-xs text-gray-700 w-56">
                        {d.vacancy_count && <div><span className="text-gray-500">Vacancies:</span> {d.vacancy_count}</div>}
                        {d.application_fee && <div><span className="text-gray-500">Fee:</span> {d.application_fee}</div>}
                        {d.eligibility && <div className="truncate"><span className="text-gray-500">Elig:</span> {d.eligibility}</div>}
                        {d.department && <div className="truncate"><span className="text-gray-500">Dept:</span> {d.department}</div>}
                      </td>
                      <td className="px-3 py-2 align-top text-xs">{d.last_date || '—'}</td>
                      <td className="px-3 py-2 align-top text-right whitespace-nowrap">
                        <Button size="sm" variant="outline" onClick={() => openEditDraft(d)}
                                className="mr-1 border-purple-300" data-testid={`agg-draft-edit-${d.id}`}>
                          <Pencil className="w-3.5 h-3.5" />
                        </Button>
                        <Button size="sm" onClick={() => approveOne(d)}
                                className="bg-emerald-600 hover:bg-emerald-700 mr-1"
                                data-testid={`agg-draft-approve-${d.id}`}>
                          <CheckCircle2 className="w-3.5 h-3.5" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => rejectOne(d)}
                                className="text-red-600 border-red-300 hover:bg-red-50"
                                data-testid={`agg-draft-reject-${d.id}`}>
                          <XCircle className="w-3.5 h-3.5" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {drafts.length === 0 && (
                    <tr><td colSpan={5} className="text-center py-8 text-gray-500" data-testid="agg-drafts-empty">
                      No drafts in queue. Trigger a run from the Sources tab.
                    </td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        {/* SOURCES */}
        <TabsContent value="sources" className="mt-4">
          <div className="bg-white rounded-xl border border-purple-100 p-4">
            <div className="flex items-center justify-between mb-3 gap-2 flex-wrap">
              <div className="text-sm text-gray-700">
                Use <strong>only</strong> official government / recruitment-board / PSU / university sites.
                No aggregator or competitor sites.
              </div>
              <div className="flex items-center gap-2">
                <Button onClick={runAll} disabled={runAllBusy}
                        className="bg-purple-700 hover:bg-purple-800" data-testid="agg-run-all-btn">
                  {runAllBusy ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Play className="w-4 h-4 mr-1" />}
                  Run All Enabled
                </Button>
                <Button onClick={openNewSource} variant="outline" className="border-purple-300" data-testid="agg-add-source-btn">
                  <Plus className="w-4 h-4 mr-1" /> Add source
                </Button>
              </div>
            </div>

            <div className="overflow-x-auto -mx-4 sm:mx-0">
              <table className="w-full text-sm min-w-[920px]">
                <thead className="bg-purple-50 text-purple-900">
                  <tr>
                    <th className="text-left px-3 py-2">Name</th>
                    <th className="text-left px-3 py-2">List URL</th>
                    <th className="text-left px-3 py-2">Trust</th>
                    <th className="text-left px-3 py-2">Last run</th>
                    <th className="text-left px-3 py-2">Enabled</th>
                    <th className="text-right px-3 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sources.map(s => (
                    <tr key={s.id} className="border-b border-purple-50 hover:bg-purple-50/40">
                      <td className="px-3 py-2 align-top">
                        <div className="font-medium text-purple-900">{s.name}</div>
                        {s.notes && <div className="text-xs text-gray-500">{s.notes}</div>}
                        <div className="mt-1">
                          <Badge variant="outline" className="border-purple-200 text-purple-700 text-[10px]">
                            {TYPES.find(t => t.key === s.default_type)?.label || s.default_type}
                          </Badge>
                        </div>
                      </td>
                      <td className="px-3 py-2 align-top text-xs">
                        <a href={s.list_url} target="_blank" rel="noopener noreferrer" className="text-purple-700 hover:underline break-all">
                          {s.list_url}
                        </a>
                      </td>
                      <td className="px-3 py-2 align-top">
                        <LevelBadge level={s.trust_level} />
                        <div className="text-[11px] text-gray-600 mt-1">
                          ✓ {s.approvals || 0} / ✗ {s.rejections || 0}
                        </div>
                        {NEXT_GOAL[s.trust_level] !== null && (
                          <div className="text-[10px] text-gray-500 mt-1">
                            Streak: <span className="font-semibold text-purple-900">{s.consecutive_clean_approvals || 0}</span> / {NEXT_GOAL[s.trust_level]} clean approvals to promote
                          </div>
                        )}
                        {s.trust_level === 'trusted' && (
                          <div className="text-[10px] text-emerald-700 mt-1">auto-publishes</div>
                        )}
                        {s.consecutive_parse_failures > 0 && (
                          <div className="text-[10px] text-red-600 mt-1">
                            ⚠ {s.consecutive_parse_failures} parse fail{s.consecutive_parse_failures === 1 ? '' : 's'} in a row
                          </div>
                        )}
                        {s.last_demoted_reason && (
                          <div className="text-[10px] text-gray-500 mt-1 italic" title={new Date(s.last_demoted_at).toLocaleString()}>
                            last demoted: {s.last_demoted_reason.slice(0, 60)}
                          </div>
                        )}
                      </td>
                      <td className="px-3 py-2 align-top text-xs">
                        {s.last_run_at
                          ? <>
                              {new Date(s.last_run_at).toLocaleString()}
                              {s.last_run_summary && (
                                <div className="text-[11px] text-gray-500">
                                  {s.last_run_summary.parse_failed
                                    ? <span className="text-red-600 inline-flex items-center"><AlertCircle className="w-3 h-3 mr-1" /> failed</span>
                                    : <>+{s.last_run_summary.new_drafts || 0} draft, +{s.last_run_summary.new_published || 0} pub, {s.last_run_summary.fetched || 0} fetched</>}
                                </div>
                              )}
                            </>
                          : <span className="text-gray-400">never</span>}
                      </td>
                      <td className="px-3 py-2 align-top">
                        <Switch checked={s.enabled !== false}
                                onCheckedChange={async v => { await aggUpdateSource(s.id, { enabled: v }); refreshAll(); }}
                                data-testid={`agg-source-toggle-${s.id}`} />
                      </td>
                      <td className="px-3 py-2 align-top text-right whitespace-nowrap">
                        <Button size="sm" onClick={() => runOne(s)} disabled={runningId === s.id}
                                className="bg-purple-700 hover:bg-purple-800 mr-1" data-testid={`agg-source-run-${s.id}`}>
                          {runningId === s.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => openEditSource(s)} className="mr-1 border-purple-300" data-testid={`agg-source-edit-${s.id}`}>
                          <Pencil className="w-3.5 h-3.5" />
                        </Button>
                        {s.trust_level !== 'trusted' && (
                          <Button size="sm" variant="outline" onClick={() => setLevel(s, s.trust_level === 'new' ? 'probationary' : 'trusted')}
                                  className="mr-1 border-emerald-300 text-emerald-700 hover:bg-emerald-50"
                                  title="Promote one level"
                                  data-testid={`agg-source-promote-${s.id}`}>
                            <ArrowUp className="w-3.5 h-3.5" />
                          </Button>
                        )}
                        {s.trust_level !== 'new' && (
                          <Button size="sm" variant="outline" onClick={() => setLevel(s, s.trust_level === 'trusted' ? 'probationary' : 'new')}
                                  className="mr-1 border-amber-300 text-amber-700 hover:bg-amber-50"
                                  title="Demote one level"
                                  data-testid={`agg-source-demote-${s.id}`}>
                            <ArrowDown className="w-3.5 h-3.5" />
                          </Button>
                        )}
                        <Button size="sm" variant="outline" onClick={() => resetTrust(s)} className="mr-1 border-purple-300" title="Reset counters" data-testid={`agg-source-reset-trust-${s.id}`}>
                          <RotateCcw className="w-3.5 h-3.5" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => deleteSource(s)} className="text-red-600 border-red-300 hover:bg-red-50" data-testid={`agg-source-delete-${s.id}`}>
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {sources.length === 0 && (
                    <tr><td colSpan={6} className="text-center py-6 text-gray-500">No sources yet.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        {/* AUTO-PUBLISH LOG */}
        <TabsContent value="autolog" className="mt-4">
          <div className="bg-white rounded-xl border border-purple-100 p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-semibold text-purple-900">Trusted-source auto-publishes</h3>
                <p className="text-xs text-gray-600">Items that bypassed the review queue because their source is Trusted. Click <strong>Undo</strong> to unpublish + delete the notice and demote the source back to Probationary.</p>
              </div>
              <Button variant="outline" size="sm" onClick={refreshAutoLog} className="border-purple-300" data-testid="agg-autolog-refresh">
                <RefreshCw className="w-3.5 h-3.5 mr-1" /> Refresh
              </Button>
            </div>
            <div className="overflow-x-auto -mx-4 sm:mx-0">
              <table className="w-full text-sm min-w-[760px]">
                <thead className="bg-purple-50 text-purple-900">
                  <tr>
                    <th className="text-left px-3 py-2">When</th>
                    <th className="text-left px-3 py-2">Title</th>
                    <th className="text-left px-3 py-2">Source</th>
                    <th className="text-right px-3 py-2">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {autoLog.map(n => (
                    <tr key={n.id} className="border-b border-purple-50" data-testid={`autolog-row-${n.id}`}>
                      <td className="px-3 py-2 align-top text-xs whitespace-nowrap">
                        {n.approved_at ? new Date(n.approved_at).toLocaleString() : '—'}
                      </td>
                      <td className="px-3 py-2 align-top">
                        <div className="font-medium text-purple-900">{n.title}</div>
                        <div className="text-[11px] text-gray-500">
                          {n.source_url && (
                            <a href={n.source_url} target="_blank" rel="noopener noreferrer" className="text-purple-700 hover:underline inline-flex items-center">
                              source <ExternalLink className="w-3 h-3 ml-1" />
                            </a>
                          )}
                        </div>
                      </td>
                      <td className="px-3 py-2 align-top text-xs">{n.source_name || sourcesById[n.source_id]?.name || '—'}</td>
                      <td className="px-3 py-2 align-top text-right whitespace-nowrap">
                        <Button size="sm" variant="outline"
                                onClick={() => undoAuto(n)}
                                className="text-amber-700 border-amber-300 hover:bg-amber-50"
                                data-testid={`agg-autolog-undo-${n.id}`}>
                          <Undo2 className="w-3.5 h-3.5 mr-1" /> Undo & demote
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {autoLog.length === 0 && (
                    <tr><td colSpan={4} className="text-center py-6 text-gray-500" data-testid="agg-autolog-empty">
                      No trusted-source auto-publishes yet.
                    </td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        {/* RUN LOG */}
        <TabsContent value="runs" className="mt-4">
          <div className="bg-white rounded-xl border border-purple-100 p-4">
            <h3 className="font-semibold text-purple-900 mb-3">Recent runs ({runs.length})</h3>
            <div className="overflow-x-auto -mx-4 sm:mx-0">
              <table className="w-full text-sm min-w-[800px]">
                <thead className="bg-purple-50 text-purple-900">
                  <tr>
                    <th className="text-left px-3 py-2">When</th>
                    <th className="text-left px-3 py-2">Source</th>
                    <th className="text-left px-3 py-2">Fetched</th>
                    <th className="text-left px-3 py-2">New drafts</th>
                    <th className="text-left px-3 py-2">URL dup</th>
                    <th className="text-left px-3 py-2">Fuzzy dup</th>
                    <th className="text-left px-3 py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map(r => (
                    <tr key={r.id} className="border-b border-purple-50 align-top">
                      <td className="px-3 py-2 text-xs">{r.run_at ? new Date(r.run_at).toLocaleString() : '—'}</td>
                      <td className="px-3 py-2 text-xs">{r.name}</td>
                      <td className="px-3 py-2">{r.fetched}</td>
                      <td className="px-3 py-2 font-medium text-emerald-700">{r.new_drafts}</td>
                      <td className="px-3 py-2 text-gray-600">{r.skipped_url_dup}</td>
                      <td className="px-3 py-2 text-gray-600">{r.skipped_fuzzy_dup}</td>
                      <td className="px-3 py-2 text-xs">
                        {r.parse_failed
                          ? <span className="text-red-600 inline-flex items-center"><AlertCircle className="w-3 h-3 mr-1" /> {r.errors?.[0]?.slice(0, 120) || 'failed'}</span>
                          : <span className="text-emerald-700">ok</span>}
                      </td>
                    </tr>
                  ))}
                  {runs.length === 0 && (
                    <tr><td colSpan={7} className="text-center py-6 text-gray-500">No runs yet.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        {/* SETTINGS */}
        <TabsContent value="settings" className="mt-4">
          <div className="bg-white rounded-xl border border-purple-100 p-4 max-w-xl">
            <h3 className="font-semibold text-purple-900 mb-3">Scheduler</h3>
            <div className="flex items-center justify-between mb-4">
              <Label htmlFor="agg-enabled">Automatic runs</Label>
              <Switch id="agg-enabled" checked={settings.enabled}
                      onCheckedChange={(v) => saveSettings({ ...settings, enabled: v })}
                      data-testid="agg-settings-enabled-toggle" />
            </div>
            <div className="mb-2">
              <Label htmlFor="agg-interval">Run every (hours, 1–168)</Label>
              <Input id="agg-interval" type="number" min={1} max={168}
                     value={settings.interval_hours}
                     onChange={e => setSettings(s => ({ ...s, interval_hours: parseInt(e.target.value || '0', 10) }))}
                     data-testid="agg-settings-interval-input" />
            </div>
            <Button className="bg-purple-700 hover:bg-purple-800 mt-3"
                    onClick={() => saveSettings(settings)}
                    data-testid="agg-settings-save-btn">
              Save scheduler settings
            </Button>
            <p className="text-xs text-gray-500 mt-3">
              When enabled, every {settings.interval_hours}h all enabled sources are fetched and parsed.
              All extracted items go into the Review Queue as drafts. Nothing is auto-published.
            </p>
          </div>
        </TabsContent>
      </Tabs>

      {/* Source dialog */}
      <Dialog open={srcDialogOpen} onOpenChange={setSrcDialogOpen}>
        <DialogContent className="max-w-xl">
          <DialogHeader><DialogTitle>{srcEditing ? 'Edit source' : 'Add source'}</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div>
              <Label>Display name</Label>
              <Input value={srcForm.name} onChange={e => setSrcForm({ ...srcForm, name: e.target.value })} data-testid="agg-src-name" />
            </div>
            <div>
              <Label>Base URL</Label>
              <Input value={srcForm.base_url} onChange={e => setSrcForm({ ...srcForm, base_url: e.target.value })} placeholder="https://example.gov.in" data-testid="agg-src-base" />
            </div>
            <div>
              <Label>List page URL (where notifications are listed)</Label>
              <Input value={srcForm.list_url} onChange={e => setSrcForm({ ...srcForm, list_url: e.target.value })} placeholder="https://example.gov.in/recruitment" data-testid="agg-src-list" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Default type</Label>
                <Select value={srcForm.default_type} onValueChange={(v) => setSrcForm({ ...srcForm, default_type: v })}>
                  <SelectTrigger data-testid="agg-src-type"><SelectValue /></SelectTrigger>
                  <SelectContent>{TYPES.map(t => <SelectItem key={t.key} value={t.key}>{t.label}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div>
                <Label>Default category</Label>
                <Select value={srcForm.default_category} onValueChange={(v) => setSrcForm({ ...srcForm, default_category: v })}>
                  <SelectTrigger data-testid="agg-src-cat"><SelectValue /></SelectTrigger>
                  <SelectContent>{CATEGORIES.map(c => <SelectItem key={c} value={c} className="capitalize">{c}</SelectItem>)}</SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Notes</Label>
              <Textarea rows={2} value={srcForm.notes} onChange={e => setSrcForm({ ...srcForm, notes: e.target.value })} />
            </div>
            <div className="flex items-center gap-2">
              <Switch checked={srcForm.enabled} onCheckedChange={(v) => setSrcForm({ ...srcForm, enabled: v })} data-testid="agg-src-enabled" />
              <Label>Enabled</Label>
            </div>
            <p className="text-[11px] text-gray-500">
              Trust level is earned automatically (10 clean approvals → Probationary, 25 → Trusted).
              Use the ↑↓ buttons on the Sources tab for manual overrides.
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSrcDialogOpen(false)}>Cancel</Button>
            <Button className="bg-purple-700 hover:bg-purple-800" onClick={saveSource} data-testid="agg-src-save">
              {srcEditing ? 'Save' : 'Add source'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Draft edit dialog */}
      <Dialog open={draftDialogOpen} onOpenChange={setDraftDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader><DialogTitle>Edit draft before approving</DialogTitle></DialogHeader>
          <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-2">
            <div><Label>Title</Label><Input value={draftForm.title} onChange={e => setDraftForm({ ...draftForm, title: e.target.value })} data-testid="agg-draftedit-title" /></div>
            <div><Label>Description (auto-generated original summary)</Label>
              <Textarea rows={4} value={draftForm.description} onChange={e => setDraftForm({ ...draftForm, description: e.target.value })} data-testid="agg-draftedit-desc" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div><Label>Vacancy count</Label><Input value={draftForm.vacancy_count} onChange={e => setDraftForm({ ...draftForm, vacancy_count: e.target.value })} /></div>
              <div><Label>Last date</Label><Input value={draftForm.last_date} onChange={e => setDraftForm({ ...draftForm, last_date: e.target.value })} /></div>
              <div><Label>Application fee</Label><Input value={draftForm.application_fee} onChange={e => setDraftForm({ ...draftForm, application_fee: e.target.value })} /></div>
              <div><Label>Eligibility</Label><Input value={draftForm.eligibility} onChange={e => setDraftForm({ ...draftForm, eligibility: e.target.value })} /></div>
            </div>
            <div><Label>Apply link</Label><Input value={draftForm.apply_link} onChange={e => setDraftForm({ ...draftForm, apply_link: e.target.value })} /></div>
            <div><Label>Notification link</Label><Input value={draftForm.notification_link} onChange={e => setDraftForm({ ...draftForm, notification_link: e.target.value })} /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDraftDialogOpen(false)}>Cancel</Button>
            <Button className="bg-purple-700 hover:bg-purple-800" onClick={saveDraftEdit} data-testid="agg-draftedit-save">
              Save changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
