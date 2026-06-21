import React from 'react';
import { Link } from 'react-router-dom';
import LegalPage, { LegalSection, LegalList } from '../components/LegalPage';

const PrivacyPolicy = () => (
  <LegalPage
    title="Privacy Policy"
    subtitle="How we collect, use and protect your information"
    lastUpdated="2025-07-01"
    seoDescription="AssamVacancies.com privacy policy: what data we collect, how we use cookies, and our use of Google AdSense and Google Analytics."
  >
    <p>
      This Privacy Policy describes how AssamVacancies.com (“we”, “our”, “us”) collects, uses
      and shares information when you visit our website. By using the site, you agree to the
      terms set out below.
    </p>

    <LegalSection id="info-we-collect" heading="Information we collect">
      <p>We collect the minimum information needed to operate the site and improve our service:</p>
      <LegalList items={[
        'Information you submit voluntarily: name, email address and message text you provide via our Contact form.',
        'Technical data automatically logged by our servers and analytics providers: IP address, browser type, device type, pages viewed, referring URL and approximate location derived from IP.',
        'Cookies and similar identifiers placed on your device to remember your preferences (such as your cookie-consent choice) and to support analytics and advertising once you opt in.',
      ]} />
      <p>
        We do not knowingly collect personal information from children under the age of 13.
        If you believe a child has provided us personal information, please contact us and we
        will remove it.
      </p>
    </LegalSection>

    <LegalSection id="how-we-use" heading="How we use information">
      <LegalList items={[
        'To respond to messages you send us through the Contact form.',
        'To operate, maintain and improve the site, including diagnosing technical problems and preventing abuse.',
        'To understand aggregated usage patterns and improve the relevance of our content.',
        'To serve advertising that helps us keep the site free for all visitors (only after you opt in via our cookie banner).',
      ]} />
    </LegalSection>

    <LegalSection id="cookies" heading="Cookies">
      <p>
        Cookies are small text files stored in your browser. We use two broad categories:
      </p>
      <LegalList items={[
        'Essential cookies, used to remember your cookie-consent choice and to keep the site functioning. These cannot be disabled if you wish to use the site normally.',
        'Analytics and advertising cookies, which are only set after you click “Accept all” in the consent banner. If you decline, we do not load Google Analytics or Google AdSense, and no advertising cookies are placed by these providers.',
      ]} />
      <p>
        You can change your mind at any time by clearing the <code>av_cookie_consent_v1</code>
        entry in your browser's local storage and refreshing the page; the consent banner will
        re-appear.
      </p>
    </LegalSection>

    <LegalSection id="third-parties" heading="Third-party services">
      <p>
        We use two third-party services that may collect data through your browser <em>only after
        you opt in</em> through our cookie consent banner:
      </p>
      <LegalList items={[
        <><strong>Google AdSense</strong> serves the advertisements that appear on the site. AdSense uses cookies to deliver relevant ads and measure their effectiveness. See Google's <a className="text-purple-700 underline" href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener noreferrer">advertising privacy notice</a>.</>,
        <><strong>Google Analytics</strong> helps us understand how visitors use the site (which pages are read most, which devices are used, average session length). We have enabled IP anonymisation. See Google's <a className="text-purple-700 underline" href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">privacy policy</a>.</>,
      ]} />
      <p>
        We do not sell your personal data to any third party.
      </p>
    </LegalSection>

    <LegalSection id="retention" heading="Data retention">
      <p>
        Contact form messages are retained for as long as needed to respond and for a reasonable
        period afterwards for record-keeping. Server logs are typically retained for up to 30
        days. Analytics data is retained according to the default settings of our analytics
        provider.
      </p>
    </LegalSection>

    <LegalSection id="your-rights" heading="Your rights">
      <p>You may at any time:</p>
      <LegalList items={[
        'Request a copy of the personal information we hold about you.',
        'Request correction or deletion of your personal information.',
        'Withdraw your consent for analytics and advertising cookies.',
      ]} />
      <p>
        To exercise any of these rights, contact us at the email address listed on the {' '}
        <Link to="/contact" className="text-purple-700 underline">Contact</Link> page.
      </p>
    </LegalSection>

    <LegalSection id="security" heading="Security">
      <p>
        We apply reasonable technical and organisational measures — including HTTPS in transit,
        bcrypt-hashed admin credentials and access logging — to protect the limited data we
        hold. No internet transmission can be guaranteed completely secure.
      </p>
    </LegalSection>

    <LegalSection id="changes" heading="Changes to this policy">
      <p>
        We may update this Privacy Policy from time to time. Material changes will be reflected
        in the “Last updated” date at the top of this page. Continued use of the site after such
        changes constitutes acceptance of the revised policy.
      </p>
    </LegalSection>

    <LegalSection id="contact" heading="Contact us">
      <p>
        Questions about this Privacy Policy can be sent through our {' '}
        <Link to="/contact" className="text-purple-700 underline">Contact</Link> page.
      </p>
    </LegalSection>
  </LegalPage>
);

export default PrivacyPolicy;
