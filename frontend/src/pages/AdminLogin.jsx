import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Lock, User, Briefcase } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const AdminLogin = () => {
  const { login } = useAuth();
  const nav = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(username, password);
      toast({ title: 'Welcome, Admin' });
      nav('/admin');
    } catch {
      toast({ title: 'Invalid credentials', description: 'Try admin / admin' });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-10">
      <div className="max-w-md w-full bg-white rounded-2xl border border-purple-100 shadow-xl overflow-hidden">
        <div className="assam-gradient text-white p-6 text-center">
          <div className="w-14 h-14 mx-auto rounded-full bg-white/15 flex items-center justify-center mb-3">
            <Briefcase className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-extrabold">Admin Login</h1>
          <p className="text-purple-200 text-sm mt-1">AssamVacancies.com Control Panel</p>
        </div>
        <form onSubmit={onSubmit} className="p-6 space-y-4">
          <div>
            <Label htmlFor="u">Username</Label>
            <div className="relative mt-1">
              <User className="w-4 h-4 absolute left-3 top-3 text-purple-500" />
              <Input id="u" value={username} onChange={e=>setUsername(e.target.value)} placeholder="admin" className="pl-9" />
            </div>
          </div>
          <div>
            <Label htmlFor="p">Password</Label>
            <div className="relative mt-1">
              <Lock className="w-4 h-4 absolute left-3 top-3 text-purple-500" />
              <Input id="p" type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="admin" className="pl-9" />
            </div>
          </div>
          <Button type="submit" disabled={loading} className="w-full bg-purple-700 hover:bg-purple-800">
            {loading ? 'Signing in...' : 'Sign in'}
          </Button>
          <p className="text-xs text-center text-gray-500">Demo: username <b>admin</b> / password <b>admin</b></p>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;
