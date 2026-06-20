import React from 'react';
import SeoMeta from '../components/SeoMeta';
import { Briefcase, Target, Users, Award } from 'lucide-react';

const About = () => (
  <div className="max-w-7xl mx-auto px-4 py-8">
    <SeoMeta title="About Us" description="AssamVacancies.com is your trusted source for the latest government and private jobs, admit cards, results and answer keys across all 35 districts of Assam." />
    <div className="bg-gradient-to-r from-purple-700 to-purple-900 text-white rounded-xl p-8 mb-6">
      <h1 className="text-3xl md:text-4xl font-extrabold title-font">About AssamVacancies.com</h1>
      <p className="text-purple-100 mt-2 max-w-3xl">Your trusted source for the latest government and private job updates, admit cards, results, scholarships and admission notifications across Assam and Northeast India.</p>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white border border-purple-100 rounded-xl p-6">
        <Target className="w-8 h-8 text-purple-700 mb-3" />
        <h2 className="font-bold text-lg text-purple-900 mb-2">Our Mission</h2>
        <p className="text-gray-700 text-sm leading-relaxed">To empower job seekers in Assam by providing timely, accurate and comprehensive information about employment opportunities, exams and academic notifications.</p>
      </div>
      <div className="bg-white border border-purple-100 rounded-xl p-6">
        <Users className="w-8 h-8 text-purple-700 mb-3" />
        <h2 className="font-bold text-lg text-purple-900 mb-2">Who We Serve</h2>
        <p className="text-gray-700 text-sm leading-relaxed">Students, freshers, working professionals and aspirants across Assam looking for verified job notifications from government departments, PSUs, private companies and educational boards.</p>
      </div>
      <div className="bg-white border border-purple-100 rounded-xl p-6">
        <Briefcase className="w-8 h-8 text-purple-700 mb-3" />
        <h2 className="font-bold text-lg text-purple-900 mb-2">What We Offer</h2>
        <ul className="text-gray-700 text-sm leading-relaxed list-disc ml-5 space-y-1">
          <li>Latest job notifications &amp; recruitment alerts</li>
          <li>Admit card downloads &amp; exam schedules</li>
          <li>Results &amp; answer keys</li>
          <li>Scholarship &amp; admission updates</li>
          <li>Career guidance &amp; tips</li>
        </ul>
      </div>
      <div className="bg-white border border-purple-100 rounded-xl p-6">
        <Award className="w-8 h-8 text-purple-700 mb-3" />
        <h2 className="font-bold text-lg text-purple-900 mb-2">Why Trust Us</h2>
        <p className="text-gray-700 text-sm leading-relaxed">All notifications are curated from official sources. We ensure timely updates so candidates never miss a deadline. Disclaimer: This site is a private informational portal and is not affiliated with any government body.</p>
      </div>
    </div>
  </div>
);

export default About;
