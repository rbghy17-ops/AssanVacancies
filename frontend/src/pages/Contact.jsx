import React, { useState } from 'react';
import { submitContact } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import SeoMeta from '../components/SeoMeta';
import { toast } from '../hooks/use-toast';
import { Mail, Phone, MapPin, Send } from 'lucide-react';

const Contact = () => {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.email || !form.message) {
      toast({ title: 'Please fill required fields' });
      return;
    }
    setSubmitting(true);
    try {
      await submitContact(form);
      toast({ title: 'Message sent!', description: 'We will get back to you shortly.' });
      setForm({ name: '', email: '', subject: '', message: '' });
    } catch {
      toast({ title: 'Failed to send. Please try again.' });
    }
    setSubmitting(false);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <SeoMeta title="Contact Us" description="Get in touch with AssamVacancies.com — submit a job, report an issue or ask a question about jobs, admit cards, results or answer keys in Assam." />
      <div className="bg-gradient-to-r from-purple-700 to-purple-900 text-white rounded-xl p-6 mb-6">
        <h1 className="text-2xl md:text-3xl font-extrabold title-font">Contact Us</h1>
        <p className="text-purple-100 text-sm mt-1">Have a question? Send us a message.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-white rounded-xl border border-purple-100 p-6">
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Your Name *</Label>
                <Input id="name" value={form.name} onChange={e=>setForm({...form, name: e.target.value})} className="mt-1" />
              </div>
              <div>
                <Label htmlFor="email">Email *</Label>
                <Input id="email" type="email" value={form.email} onChange={e=>setForm({...form, email: e.target.value})} className="mt-1" />
              </div>
            </div>
            <div>
              <Label htmlFor="subject">Subject</Label>
              <Input id="subject" value={form.subject} onChange={e=>setForm({...form, subject: e.target.value})} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="message">Message *</Label>
              <Textarea id="message" rows={6} value={form.message} onChange={e=>setForm({...form, message: e.target.value})} className="mt-1" />
            </div>
            <Button type="submit" disabled={submitting} className="bg-purple-700 hover:bg-purple-800 text-white">
              <Send className="w-4 h-4 mr-2" /> {submitting ? 'Sending...' : 'Send Message'}
            </Button>
          </form>
        </div>
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-purple-100 p-5">
            <div className="flex items-center gap-3 mb-3"><Mail className="w-5 h-5 text-purple-700" /><div><div className="font-semibold text-purple-900">Email</div><div className="text-sm text-gray-700">contact@assamvacancies.com</div></div></div>
            <div className="flex items-center gap-3 mb-3"><Phone className="w-5 h-5 text-purple-700" /><div><div className="font-semibold text-purple-900">Phone</div><div className="text-sm text-gray-700">+91 98XXX XXXXX</div></div></div>
            <div className="flex items-center gap-3"><MapPin className="w-5 h-5 text-purple-700" /><div><div className="font-semibold text-purple-900">Address</div><div className="text-sm text-gray-700">Guwahati, Assam, 781001</div></div></div>
          </div>
          <div className="bg-gradient-to-br from-purple-700 to-purple-900 text-white rounded-xl p-5">
            <h3 className="font-bold">Submit a Job</h3>
            <p className="text-sm text-purple-200 mt-1">Are you an employer? Reach out via contact form to list your job vacancies.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;
