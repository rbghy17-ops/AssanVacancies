import React from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, Facebook, Twitter, Send, Youtube, Mail, MapPin } from 'lucide-react';

const Footer = () => (
  <footer className="bg-purple-950 text-purple-100 mt-12">
    <div className="max-w-7xl mx-auto px-4 py-10 grid grid-cols-1 md:grid-cols-4 gap-8">
      <div>
        <div className="flex items-center gap-2 mb-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center">
            <Briefcase className="w-5 h-5 text-white" />
          </div>
          <div className="text-lg font-extrabold text-white">AssamVacancies.com</div>
        </div>
        <p className="text-sm text-purple-200">Premier website for latest government and private jobs, admit cards, results, scholarships and admission updates in Assam and Northeast India.</p>
      </div>
      <div>
        <h4 className="text-white font-bold mb-3">Quick Links</h4>
        <ul className="space-y-2 text-sm">
          <li><Link to="/" className="hover:text-white">Home</Link></li>
          <li><Link to="/about" className="hover:text-white">About</Link></li>
          <li><Link to="/contact" className="hover:text-white">Contact</Link></li>
          <li><Link to="/admin/login" className="hover:text-white">Admin</Link></li>
        </ul>
      </div>
      <div>
        <h4 className="text-white font-bold mb-3">Categories</h4>
        <ul className="space-y-2 text-sm">
          <li><Link to="/category/govt" className="hover:text-white">Government Jobs</Link></li>
          <li><Link to="/category/defence" className="hover:text-white">Defence Jobs</Link></li>
          <li><Link to="/category/banking" className="hover:text-white">Banking Jobs</Link></li>
          <li><Link to="/category/railway" className="hover:text-white">Railway Jobs</Link></li>
          <li><Link to="/category/teaching" className="hover:text-white">Teaching Jobs</Link></li>
        </ul>
      </div>
      <div>
        <h4 className="text-white font-bold mb-3">Connect</h4>
        <div className="flex items-center gap-2 mb-2">
          <a href="#" className="w-9 h-9 rounded bg-purple-800 hover:bg-purple-700 flex items-center justify-center"><Facebook className="w-4 h-4" /></a>
          <a href="#" className="w-9 h-9 rounded bg-purple-800 hover:bg-purple-700 flex items-center justify-center"><Twitter className="w-4 h-4" /></a>
          <a href="#" className="w-9 h-9 rounded bg-purple-800 hover:bg-purple-700 flex items-center justify-center"><Send className="w-4 h-4" /></a>
          <a href="#" className="w-9 h-9 rounded bg-purple-800 hover:bg-purple-700 flex items-center justify-center"><Youtube className="w-4 h-4" /></a>
        </div>
        <div className="flex items-center gap-2 text-sm text-purple-200 mt-3"><Mail className="w-4 h-4" /> contact@assamvacancies.com</div>
        <div className="flex items-center gap-2 text-sm text-purple-200 mt-1"><MapPin className="w-4 h-4" /> Guwahati, Assam, India</div>
      </div>
    </div>
    <div className="border-t border-purple-900 py-4 text-center text-xs text-purple-300">
      &copy; {new Date().getFullYear()} AssamVacancies.com | All Rights Reserved | Disclaimer: This is a private informational website.
    </div>
  </footer>
);

export default Footer;
