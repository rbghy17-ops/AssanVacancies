import React from 'react';
import { Link } from 'react-router-dom';
import LegalPage, { LegalSection, LegalList } from '../components/LegalPage';

const About = () => (
  <LegalPage
    title="About AssamVacancies.com"
    subtitle="An independent information service for job seekers across Assam and the Northeast"
    lastUpdated="2025-07-01"
    seoDescription="AssamVacancies.com is an independent information service that aggregates verified job notifications, admit cards, results and answer keys for all 35 districts of Assam."
  >
    <LegalSection id="mission" heading="Our mission">
      <p>
        AssamVacancies.com was started with one simple goal: make it easier for job seekers in
        Assam and the Northeast to <strong>find verified, well-organised information</strong>
        {' '}about government and private recruitment, admit cards, results, answer keys,
        admissions and scholarships, without having to chase a dozen different official sites
        every day.
      </p>
    </LegalSection>

    <LegalSection id="what-we-cover" heading="What we cover">
      <p>We publish notifications across four content sections:</p>
      <LegalList items={[
        <><Link to="/jobs" className="text-purple-700 underline">Jobs</Link> — recruitment notifications from government departments, public-sector undertakings, banks, defence forces, railways, police forces and reputable private employers.</>,
        <><Link to="/admit-card" className="text-purple-700 underline">Admit cards</Link> — download links and release announcements from recruiting bodies and examination boards.</>,
        <><Link to="/result" className="text-purple-700 underline">Results</Link> — announcements covering recruitment exams, board results and selection lists.</>,
        <><Link to="/answer-key" className="text-purple-700 underline">Answer keys</Link> — official and provisional answer keys, with deadlines for raising objections where applicable.</>,
      ]} />
      <p>
        Listings are tagged by category (Government, Private, Defence, Banking, Railway, Teaching,
        Police) and by district so you can quickly narrow to what's relevant to you.
      </p>
    </LegalSection>

    <LegalSection id="coverage" heading="Geographic coverage">
      <p>
        Although our editorial focus is Assam — covering all 35 districts — we also publish
        all-India and Northeast-wide notifications that affect candidates from the region.
      </p>
    </LegalSection>

    <LegalSection id="how-we-work" heading="How we work">
      <p>
        Every notification is curated from the official source. We summarise the key facts —
        vacancies, eligibility, important dates, application links — and link straight back to
        the official notification PDF and application portal so you can verify every detail
        before applying.
      </p>
      <p>
        Notices automatically expire from active listings the day after their last date passes,
        but their pages remain available for archival reference.
      </p>
    </LegalSection>

    <LegalSection id="independence" heading="Independence">
      <p>
        AssamVacancies.com is an independent privately-run information service. We are not a
        government portal, are not affiliated with any recruiting authority, and never charge
        candidates a fee. See our{' '}
        <Link to="/disclaimer" className="text-purple-700 underline">Disclaimer</Link>{' '}
        for details.
      </p>
    </LegalSection>

    <LegalSection id="contact" heading="Get in touch">
      <p>
        Spotted an error, want to suggest a notification we missed, or have a question? Reach
        out via our{' '}
        <Link to="/contact" className="text-purple-700 underline">Contact</Link> page.
      </p>
    </LegalSection>
  </LegalPage>
);

export default About;
