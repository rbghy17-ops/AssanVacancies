import React from 'react';
import { Link } from 'react-router-dom';
import LegalPage, { LegalSection, LegalList } from '../components/LegalPage';

const Disclaimer = () => (
  <LegalPage
    title="Disclaimer"
    subtitle="AssamVacancies.com is an independent information service — not an official government portal"
    lastUpdated="2025-07-01"
    seoDescription="AssamVacancies.com is an independent information and aggregation site, not affiliated with any government body. Always verify with official sources."
  >
    <LegalSection id="independent" heading="Independent, unofficial site">
      <p>
        AssamVacancies.com is an <strong>independent information and aggregation website</strong>.
        We are <strong>not</strong> affiliated with, endorsed by, sponsored by or in any way
        officially connected with:
      </p>
      <LegalList items={[
        'The Government of Assam or the Government of India, or any of their ministries, departments, boards, autonomous bodies or public-sector undertakings.',
        'Recruiting agencies such as APSC, SSC, RRB, SLPRB, UPSC, IBPS, SBI, NHM Assam, DEE Assam, AHSEC, SEBA or any other entity referred to on the Site.',
        'Any private employer, university, examination body or scholarship authority whose notification may appear on the Site.',
      ]} />
      <p>
        Names, logos and trademarks of organisations referred to on the Site belong to their
        respective owners and are used only to identify the source of a notification.
      </p>
    </LegalSection>

    <LegalSection id="verify-officially" heading="Always verify with official sources">
      <p>
        Recruitment processes, examination schedules, eligibility criteria, fees, vacancies and
        result data can change without notice. Errors and delays in reporting are possible.
        Before applying, paying any fee or making any career decision, you <strong>must</strong>:
      </p>
      <LegalList items={[
        'Visit the official website of the recruiting authority listed in the notification.',
        'Read the official notification PDF in full.',
        'Confirm the dates, eligibility, application process and fee structure on the official portal.',
      ]} />
      <p>
        Where the Site links to an official source, the official source is authoritative; if a
        detail on our page differs from the official notification, treat the official version as
        correct.
      </p>
    </LegalSection>

    <LegalSection id="no-fee" heading="We never charge candidates a fee">
      <p>
        AssamVacancies.com is free to use. We do <strong>not</strong> ask for payment to publish,
        promote or guarantee selection in any recruitment, examination, admission or
        scholarship. If anyone approaches you claiming to represent this site and asks for money,
        please report it via our {' '}
        <Link to="/contact" className="text-purple-700 underline">Contact</Link> page.
      </p>
    </LegalSection>

    <LegalSection id="job-outcomes" heading="No guarantee of selection or outcome">
      <p>
        Listing a vacancy on this Site is not an offer of employment. Selection, eligibility
        determination, document verification, examinations, interviews and final appointments
        are conducted entirely by the recruiting authority. We have no role in, and no influence
        on, the outcome of any application made through links we publish.
      </p>
    </LegalSection>

    <LegalSection id="advertising" heading="Advertising">
      <p>
        The Site is supported in part by advertising delivered through Google AdSense. Ads are
        shown alongside editorial content but do not influence which notifications we publish
        and are not endorsed by us. See our {' '}
        <Link to="/privacy" className="text-purple-700 underline">Privacy Policy</Link>{' '}
        for details.
      </p>
    </LegalSection>

    <LegalSection id="errors" heading="Errors and corrections">
      <p>
        If you spot inaccurate or outdated information on any page, please tell us through the{' '}
        <Link to="/contact" className="text-purple-700 underline">Contact</Link> form. We make
        corrections as quickly as possible, but cannot guarantee a response time.
      </p>
    </LegalSection>
  </LegalPage>
);

export default Disclaimer;
