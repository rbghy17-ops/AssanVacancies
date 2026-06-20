import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { changePassword } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Lock, User, Briefcase, AlertTriangle, Clock, KeyRound } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const AdminLogin = () => {
  const { login, updateMustReset } = useAuth();
  const nav = useNavigate();
  const [sp] = useSearchParams();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [resetMode, setResetMode] = useState(false);
  const [oldPwd, setOldPwd] = useState('');
  const [newPwd, setNewPwd] = useState('');
  const [confirmPwd, setConfirmPwd] = useState('');
  const [notice, setNotice] = useState('');

  useEffect(() => {
    if (sp.get('idle')) setNotice('Your session expired due to 30 minutes of inactivity. Please log in again.');
    else if (sp.get('expired')) setNotice('Your session has expired. Please log in again.');
  }, [sp]);

  const onLogin = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);
    try {
      const res = await login(username, password);
      if (res.must_reset) {
        setOldPwd(password);
        setResetMode(true);
        toast({ title: 'Password reset required', description: 'Please change your password before continuing.' });
      } else {
        toast({ title: 'Welcome back' });
        nav('/admin');
      }
    } catch (err) {
      const detail = err?.response?.data?.detail || 'Login failed';
      setErrorMsg(detail);
    }
    setLoading(false);
  };

  const onReset = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    if (newPwd.length < 8) { setErrorMsg('New password must be at least 8 characters.'); return; }
    if (newPwd !== confirmPwd) { setErrorMsg('Passwords do not match.'); return; }
    if (newPwd === oldPwd) { setErrorMsg('New password must differ from current password.'); return; }
    setLoading(true);
    try {
      const res = await changePassword({ old_password: oldPwd, new_password: newPwd });
      if (res?.token) localStorage.setItem('av_admin_token', res.token);
      updateMustReset(false);
      toast({ title: 'Password updated', description: 'Welcome to the admin dashboard.' });
      nav('/admin');
    } catch (err) {
      setErrorMsg(err?.response?.data?.detail || 'Password reset failed');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-10">
      <div className="max-w-md w-full bg-white rounded-2xl border border-purple-100 shadow-xl overflow-hidden">
        <div className="assam-gradient text-white p-6 text-center">
          <div className="w-14 h-14 mx-auto rounded-full bg-white/15 flex items-center justify-center mb-3">
            {resetMode ? <KeyRound className="w-7 h-7" /> : <Briefcase className="w-7 h-7" />}
          </div>
          <h1 className="text-2xl font-extrabold">{resetMode ? 'Reset Your Password' : 'Admin Login'}</h1>
          <p className="text-purple-200 text-sm mt-1">{resetMode ? 'First-time login requires a new password' : 'AssamVacancies.com Control Panel'}</p>
        </div>

        {notice && !resetMode && (
          <div className="px-6 pt-4">
            <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 text-amber-800 rounded-lg p-3 text-sm">
              <Clock className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{notice}</span>
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="px-6 pt-4">
            <div className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm">
              <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          </div>
        )}

        {!resetMode ? (
          <form onSubmit={onLogin} className="p-6 space-y-4">
            <div>
              <Label htmlFor="u">Username</Label>
              <div className="relative mt-1">
                <User className="w-4 h-4 absolute left-3 top-3 text-purple-500" />
                <Input id="u" value={username} onChange={e=>setUsername(e.target.value)} placeholder="Enter username" className="pl-9" autoComplete="username" />
              </div>
            </div>
            <div>
              <Label htmlFor="p">Password</Label>
              <div className="relative mt-1">
                <Lock className="w-4 h-4 absolute left-3 top-3 text-purple-500" />
                <Input id="p" type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Enter password" className="pl-9" autoComplete="current-password" />
              </div>
            </div>
            <Button type="submit" disabled={loading || !username || !password} className="w-full bg-purple-700 hover:bg-purple-800">
              {loading ? 'Signing in...' : 'Sign in'}
            </Button>
            <div className="text-xs text-center text-gray-500 leading-relaxed">
              Accounts lock for 15 minutes after 5 failed attempts.<br />
              Sessions expire after 30 minutes of inactivity.
            </div>
          </form>
        ) : (
          <form onSubmit={onReset} className="p-6 space-y-4">
            <div>
              <Label htmlFor="np">New Password</Label>
              <div className="relative mt-1">
                <Lock className="w-4 h-4 absolute left-3 top-3 text-purple-500" />
                <Input id="np" type="password" value={newPwd} onChange={e=>setNewPwd(e.target.value)} placeholder="At least 8 characters" className="pl-9" autoComplete="new-password" />
              </div>
            </div>
            <div>
              <Label htmlFor="cp">Confirm New Password</Label>
              <div className="relative mt-1">
                <Lock className="w-4 h-4 absolute left-3 top-3 text-purple-500" />
                <Input id="cp" type="password" value={confirmPwd} onChange={e=>setConfirmPwd(e.target.value)} placeholder="Re-enter new password" className="pl-9" autoComplete="new-password" />
              </div>
            </div>
            <Button type="submit" disabled={loading} className="w-full bg-purple-700 hover:bg-purple-800">
              {loading ? 'Updating...' : 'Update Password & Continue'}
            </Button>
            <div className="text-xs text-center text-gray-500">Your old password will be permanently invalidated.</div>
          </form>
        )}
      </div>
    </div>
  );
};

export default AdminLogin;
