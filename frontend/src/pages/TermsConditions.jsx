import React from 'react';
import { Link } from 'react-router-dom';
import LegalPage, { LegalSection, LegalList } from '../components/LegalPage';

const TermsConditions = () => (
  <LegalPage
    title="Terms & Conditions"
    subtitle="The rules that govern your use of AssamVacancies.com"
    lastUpdated="2025-07-01"
    seoDescription="Terms and conditions for using AssamVacancies.com, including a disclaimer of liability for outcomes of third-party job applications."
  >
    <p>
      These Terms and Conditions (“Terms”) govern your access to and use of AssamVacancies.com
      (the “Site”). By accessing or using the Site you agree to be bound by these Terms. If you
      do not agree, please do not use the Site.
    </p>

    <LegalSection id="acceptance" heading="1. Acceptance of terms">
      <p>
        You confirm that you are at least 18 years old or have parental or guardian consent, and
        that you have the legal capacity to enter into a binding agreement.
      </p>
    </LegalSection>

    <LegalSection id="site-use" heading="2. Use of the site">
      <p>You agree to use the Site only for lawful purposes. You must not:</p>
      <LegalList items={[
        'Attempt to gain unauthorised access to any portion of the Site, including the administration area, accounts, computer systems or networks.',
        'Use any automated means, including bots or scrapers, to access or copy content in bulk without our prior written permission.',
        'Misrepresent yourself, impersonate any person, or submit false or misleading information through any form on the Site.',
        'Upload, post or transmit any material that is unlawful, defamatory, harmful or infringes any third-party rights.',
      ]} />
    </LegalSection>

    <LegalSection id="content" heading="3. Content and accuracy">
      <p>
        AssamVacancies.com is an independent information and aggregation service. We compile
        notifications about jobs, admit cards, results and answer keys from publicly available
        sources and from information provided by recruiting bodies.
      </p>
      <p>
        Although we make reasonable efforts to keep information accurate and up to date, we do
        not warrant the completeness, accuracy or timeliness of any content. Recruitment notices,
        eligibility criteria, dates and links can change without notice; you must verify all
        details directly on the official website of the recruiting authority before applying or
        making any decision.
      </p>
    </LegalSection>

    <LegalSection id="third-party-applications" heading="4. Third-party applications — disclaimer of liability">
      <p>
        Many notifications on the Site link to application portals operated by government
        departments, public-sector undertakings, private employers and other third parties. We
        do not control those portals, do not process applications, and do not accept any
        application fee.
      </p>
      <p>
        <strong>To the maximum extent permitted by applicable law, AssamVacancies.com, its
        owners, contributors and operators shall not be liable for any loss, damage or expense
        arising directly or indirectly from:</strong>
      </p>
      <LegalList items={[
        'Reliance on any notification, advertisement or content published on the Site.',
        'Errors, omissions, delays or changes in information published on or linked from the Site.',
        'The outcome of any job application, examination, interview or selection process you undertake via a link or notification appearing on the Site.',
        'Unavailability of, defects in or content displayed on any third-party website to which the Site links.',
        'Fraudulent recruitment offers or fee demands made by third parties; we never charge candidates a fee for listing a job or applying to one.',
      ]} />
      <p>
        Decisions about your career, applications, fees paid and personal information shared
        with any third party are made entirely at your own risk.
      </p>
    </LegalSection>

    <LegalSection id="ip" heading="5. Intellectual property">
      <p>
        The Site's branding, layout, original editorial content and codebase are owned by
        AssamVacancies.com or its licensors. Notice text, official notifications, government
        seals and logos belong to their respective owners and are reproduced for informational
        purposes only.
      </p>
      <p>
        You may share links to our pages freely. You may not reproduce, redistribute or
        republish substantial portions of our original editorial content without prior written
        permission.
      </p>
    </LegalSection>

    <LegalSection id="availability" heading="6. Availability">
      <p>
        We do not guarantee uninterrupted availability of the Site. We may temporarily suspend
        access for maintenance, security or operational reasons without prior notice.
      </p>
    </LegalSection>

    <LegalSection id="links" heading="7. External links">
      <p>
        Outbound links are provided for convenience only. Inclusion of a link does not imply
        endorsement. We are not responsible for the content, accuracy, opinions or privacy
        practices of any external website.
      </p>
    </LegalSection>

    <LegalSection id="liability-cap" heading="8. Limitation of liability">
      <p>
        The Site is provided on an “as is” and “as available” basis without warranties of any
        kind, express or implied. To the extent permitted by law, our total liability arising
        out of or in connection with your use of the Site is limited to one hundred Indian
        Rupees (₹100).
      </p>
    </LegalSection>

    <LegalSection id="changes" heading="9. Changes to these terms">
      <p>
        We may revise these Terms at any time by updating this page. Your continued use of the
        Site after changes are posted constitutes acceptance of the revised Terms.
      </p>
    </LegalSection>

    <LegalSection id="governing-law" heading="10. Governing law and jurisdiction">
      <p>
        These Terms are governed by the laws of India. Any dispute arising out of or in
        connection with these Terms shall be subject to the exclusive jurisdiction of the
        competent courts at Guwahati, Assam.
      </p>
    </LegalSection>

    <LegalSection id="contact" heading="11. Contact">
      <p>
        Questions about these Terms can be sent through our {' '}
        <Link to="/contact" className="text-purple-700 underline">Contact</Link> page.
      </p>
    </LegalSection>
  </LegalPage>
);

export default TermsConditions;
