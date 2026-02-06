import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy | Theta AI by TeraMind",
  description:
    "Privacy Policy for Theta AI — an AI-powered fact-verification chatbot operating on Facebook Messenger and Facebook Pages. A product of TeraMind, a TService lab.",
};

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mt-10">
      <h2 className="text-xl font-semibold tracking-tight text-foreground sm:text-2xl">
        {title}
      </h2>
      <div className="mt-4 space-y-4 leading-relaxed text-muted">{children}</div>
    </section>
  );
}

export default function PrivacyPolicy() {
  const effectiveDate = "February 5, 2026";
  const lastUpdated = "February 6, 2026";
  const appName = "Theta AI";
  const companyName = "TService";
  const labName = "TeraMind";
  const contactEmail = "privacy@tservice.tech";
  const websiteUrl = "https://theta.tservice.tech";

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="fixed top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-white">
              <span className="text-sm font-bold">T</span>
            </div>
            <span className="text-lg font-semibold tracking-tight">
              {appName}
            </span>
          </Link>
          <Link
            href="/"
            className="text-sm text-muted transition-colors hover:text-foreground"
          >
            &larr; Back to Home
          </Link>
        </div>
      </nav>

      {/* Content */}
      <main className="mx-auto max-w-3xl px-6 pt-32 pb-20">
        {/* Header */}
        <div className="border-b border-border pb-8">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Privacy Policy
          </h1>
          <p className="mt-3 text-muted">
            Effective Date: {effectiveDate} &middot; Last Updated:{" "}
            {lastUpdated}
          </p>
        </div>

        {/* Introduction */}
        <Section title="1. Introduction">
          <p>
            Welcome to <strong>{appName}</strong> (&quot;the Bot,&quot;
            &quot;we,&quot; &quot;us,&quot; or &quot;our&quot;), a product of{" "}
            <strong>{labName}</strong>, a research lab operated by{" "}
            <strong>{companyName}</strong>. {appName} is an AI-powered
            fact-verification assistant that operates on the Facebook platform,
            including Facebook Pages and Facebook Messenger.
          </p>
          <p>
            This Privacy Policy explains how we collect, use, disclose, and
            safeguard your information when you interact with {appName} through
            any Facebook integration, our website at{" "}
            <a
              href={websiteUrl}
              className="font-medium text-accent underline underline-offset-4 hover:text-accent-dark"
            >
              {websiteUrl}
            </a>
            , or any related services (collectively, the &quot;Service&quot;).
          </p>
          <p>
            By using our Service, you agree to the collection and use of
            information in accordance with this policy. If you do not agree with
            the terms of this Privacy Policy, please do not access or use the
            Service.
          </p>
        </Section>

        {/* Information We Collect */}
        <Section title="2. Information We Collect">
          <p>
            We are committed to collecting only the minimum data necessary to
            provide the Service. The types of information we may collect include:
          </p>

          <h3 className="mt-4 font-semibold text-foreground">
            2.1 Information Received from Facebook
          </h3>
          <p>
            When you interact with {appName} on Facebook (e.g., by mentioning
            our Page in a comment or sending a message via Messenger), we may
            receive the following data through the Facebook Platform and Webhooks
            API:
          </p>
          <ul className="ml-6 list-disc space-y-2">
            <li>
              <strong>Your Public Profile Information:</strong> Your Facebook
              name, profile picture, and public profile URL, as made available by
              Facebook&apos;s API.
            </li>
            <li>
              <strong>Message Content:</strong> The text content of messages you
              send to our Page via Messenger, or comments/posts in which you
              mention or tag our Page.
            </li>
            <li>
              <strong>Post & Comment Context:</strong> The content of public
              posts and comments that you tag us in, which we access via the
              Facebook Graph API to understand the context of your request.
            </li>
            <li>
              <strong>User & Page IDs:</strong> Facebook-assigned identifiers
              used to identify users, pages, posts, and comments within the
              Facebook ecosystem.
            </li>
          </ul>

          <h3 className="mt-6 font-semibold text-foreground">
            2.2 Automatically Collected Information
          </h3>
          <p>
            When you visit our website, we may automatically collect limited
            technical information, including:
          </p>
          <ul className="ml-6 list-disc space-y-2">
            <li>Browser type and version</li>
            <li>Operating system</li>
            <li>Referring URL and pages visited</li>
            <li>Date and time of access</li>
            <li>IP address (anonymized where possible)</li>
          </ul>

          <h3 className="mt-6 font-semibold text-foreground">
            2.3 Information We Do NOT Collect
          </h3>
          <ul className="ml-6 list-disc space-y-2">
            <li>We do not collect or store passwords or login credentials.</li>
            <li>
              We do not access your private Facebook messages with other users.
            </li>
            <li>
              We do not collect financial or payment information of any kind.
            </li>
            <li>
              We do not collect sensitive personal data such as health records,
              biometric data, or government-issued identifiers.
            </li>
          </ul>
        </Section>

        {/* How We Use Your Information */}
        <Section title="3. How We Use Your Information">
          <p>
            We use the information we collect solely for the following purposes:
          </p>
          <ul className="ml-6 list-disc space-y-2">
            <li>
              <strong>To Provide the Service:</strong> Processing your mentions
              and messages, fetching post context, generating AI-powered
              fact-check responses, and posting replies to your comments or
              messages.
            </li>
            <li>
              <strong>To Improve the Service:</strong> Analyzing aggregate,
              anonymized usage patterns to improve response quality, reduce
              errors, and optimize performance.
            </li>
            <li>
              <strong>To Ensure Security:</strong> Detecting and preventing
              abuse, spam, or unauthorized use of the Service.
            </li>
            <li>
              <strong>To Comply with Legal Obligations:</strong> Responding to
              lawful requests from governmental authorities where required by
              law.
            </li>
          </ul>
          <p>
            We do <strong>not</strong> use your data for advertising, profiling,
            or selling to third parties.
          </p>
        </Section>

        {/* Data Storage and Retention */}
        <Section title="4. Data Storage and Retention">
          <p>
            We store only the minimum data necessary to provide and improve the
            Service:
          </p>
          <ul className="ml-6 list-disc space-y-2">
            <li>
              <strong>Interaction Logs:</strong> We may retain anonymized records
              of interactions (e.g., post IDs, timestamps, and aggregate
              statistics) for a maximum period of <strong>90 days</strong> for
              debugging and service improvement purposes.
            </li>
            <li>
              <strong>No Long-Term User Profiles:</strong> We do not build
              persistent profiles or data stores tied to individual Facebook
              users.
            </li>
            <li>
              <strong>Message Content:</strong> The text content of messages is
              processed in real-time and is not permanently stored. It may be
              temporarily cached in server memory during processing and is
              discarded immediately after.
            </li>
          </ul>
          <p>
            Data is stored on secure servers hosted by DigitalOcean with
            industry-standard encryption and access controls.
          </p>
        </Section>

        {/* Data Sharing and Disclosure */}
        <Section title="5. Data Sharing and Disclosure">
          <p>
            We do <strong>not</strong> sell, trade, or rent your personal
            information. We may share limited data only under the following
            circumstances:
          </p>
          <ul className="ml-6 list-disc space-y-2">
            <li>
              <strong>With Facebook/Meta:</strong> As required by Facebook&apos;s
              Platform Terms and Policies for the operation of our integration.
              All interactions are subject to{" "}
              <a
                href="https://www.facebook.com/privacy/policy/"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-accent underline underline-offset-4 hover:text-accent-dark"
              >
                Meta&apos;s Privacy Policy
              </a>
              .
            </li>
            <li>
              <strong>With AI Service Providers:</strong> We send the text
              content of public posts to Google&apos;s Gemini API for analysis.
              This data is transmitted securely and is subject to{" "}
              <a
                href="https://policies.google.com/privacy"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-accent underline underline-offset-4 hover:text-accent-dark"
              >
                Google&apos;s Privacy Policy
              </a>
              .
            </li>
            <li>
              <strong>For Legal Compliance:</strong> If required by law, court
              order, or governmental authority, we may disclose data to comply
              with legal obligations.
            </li>
            <li>
              <strong>To Protect Rights:</strong> To enforce our policies,
              protect our rights or safety, or investigate potential violations.
            </li>
          </ul>
        </Section>

        {/* Third-Party Services */}
        <Section title="6. Third-Party Services">
          <p>Our Service integrates with the following third-party platforms:</p>
          <ul className="ml-6 list-disc space-y-2">
            <li>
              <strong>Facebook/Meta Platform:</strong> For receiving webhooks,
              reading public post content, and posting replies. Subject to{" "}
              <a
                href="https://www.facebook.com/privacy/policy/"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-accent underline underline-offset-4 hover:text-accent-dark"
              >
                Meta&apos;s Privacy Policy
              </a>
              .
            </li>
            <li>
              <strong>Google Gemini API:</strong> For AI-powered content analysis
              and fact-verification with search grounding. Subject to{" "}
              <a
                href="https://policies.google.com/privacy"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-accent underline underline-offset-4 hover:text-accent-dark"
              >
                Google&apos;s Privacy Policy
              </a>
              .
            </li>
            <li>
              <strong>DigitalOcean:</strong> For server hosting and
              infrastructure. Subject to{" "}
              <a
                href="https://www.digitalocean.com/legal/privacy-policy"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-accent underline underline-offset-4 hover:text-accent-dark"
              >
                DigitalOcean&apos;s Privacy Policy
              </a>
              .
            </li>
          </ul>
          <p>
            We encourage you to review the privacy policies of these third-party
            services.
          </p>
        </Section>

        {/* User Rights */}
        <Section title="7. Your Rights">
          <p>
            Depending on your jurisdiction, you may have the following rights
            regarding your personal data:
          </p>
          <ul className="ml-6 list-disc space-y-2">
            <li>
              <strong>Right of Access:</strong> You may request a copy of the
              personal data we hold about you.
            </li>
            <li>
              <strong>Right to Rectification:</strong> You may request that we
              correct any inaccurate or incomplete personal data.
            </li>
            <li>
              <strong>Right to Erasure:</strong> You may request deletion of your
              personal data. Since we do not maintain persistent user profiles,
              this can typically be fulfilled immediately.
            </li>
            <li>
              <strong>Right to Restriction:</strong> You may request that we
              restrict the processing of your personal data.
            </li>
            <li>
              <strong>Right to Object:</strong> You may object to our processing
              of your personal data for certain purposes.
            </li>
            <li>
              <strong>Right to Data Portability:</strong> Where applicable, you
              may request a machine-readable copy of your data.
            </li>
          </ul>
          <p>
            To exercise any of these rights, please contact us at{" "}
            <a
              href={`mailto:${contactEmail}`}
              className="font-medium text-accent underline underline-offset-4 hover:text-accent-dark"
            >
              {contactEmail}
            </a>
            . We will respond to your request within 30 days.
          </p>
        </Section>

        {/* Data Deletion */}
        <Section title="8. Data Deletion">
          <p>
            You may request the deletion of all data associated with your
            interactions with {appName} at any time. To initiate a data deletion
            request:
          </p>
          <ul className="ml-6 list-disc space-y-2">
            <li>
              Send an email to{" "}
              <a
                href={`mailto:${contactEmail}`}
                className="font-medium text-accent underline underline-offset-4 hover:text-accent-dark"
              >
                {contactEmail}
              </a>{" "}
              with the subject line &quot;Data Deletion Request.&quot;
            </li>
            <li>
              Include your Facebook username or the approximate date of your
              interactions.
            </li>
          </ul>
          <p>
            We will process your request within <strong>30 days</strong> and
            confirm the deletion via email. Note that since we do not maintain
            persistent user profiles, most user data is already ephemeral and
            automatically purged.
          </p>
        </Section>

        {/* Children's Privacy */}
        <Section title="9. Children&apos;s Privacy">
          <p>
            Our Service is not intended for children under the age of 13 (or the
            applicable age of digital consent in your jurisdiction). We do not
            knowingly collect personal information from children. If we become
            aware that we have inadvertently collected personal data from a
            child, we will take immediate steps to delete that information.
          </p>
          <p>
            If you are a parent or guardian and believe that your child has
            provided personal information to us, please contact us at{" "}
            <a
              href={`mailto:${contactEmail}`}
              className="font-medium text-accent underline underline-offset-4 hover:text-accent-dark"
            >
              {contactEmail}
            </a>
            .
          </p>
        </Section>

        {/* Security */}
        <Section title="10. Security">
          <p>
            We implement industry-standard security measures to protect your
            data, including:
          </p>
          <ul className="ml-6 list-disc space-y-2">
            <li>
              HTTPS/TLS encryption for all data in transit between our servers,
              Facebook&apos;s API, and third-party services.
            </li>
            <li>
              Environment-variable-based secret management (access tokens and API
              keys are never hardcoded or exposed in client-side code).
            </li>
            <li>
              Server-level firewalls and restricted SSH access on our hosting
              infrastructure.
            </li>
            <li>Regular security audits and dependency updates.</li>
          </ul>
          <p>
            While we strive to use commercially acceptable means to protect your
            personal data, no method of transmission over the Internet or
            electronic storage is 100% secure. We cannot guarantee absolute
            security.
          </p>
        </Section>

        {/* International Data Transfers */}
        <Section title="11. International Data Transfers">
          <p>
            Our servers are located in the United States (DigitalOcean). If you
            are accessing the Service from outside the United States, please be
            aware that your data may be transferred to, stored, and processed in
            the United States. By using the Service, you consent to the transfer
            of your information to the United States.
          </p>
        </Section>

        {/* Changes to This Policy */}
        <Section title="12. Changes to This Privacy Policy">
          <p>
            We may update this Privacy Policy from time to time to reflect
            changes in our practices, technology, legal requirements, or other
            factors. When we make material changes, we will:
          </p>
          <ul className="ml-6 list-disc space-y-2">
            <li>
              Update the &quot;Last Updated&quot; date at the top of this page.
            </li>
            <li>
              Post a notice on our website or Facebook Page for significant
              changes.
            </li>
          </ul>
          <p>
            Your continued use of the Service after any changes indicates your
            acceptance of the updated Privacy Policy.
          </p>
        </Section>

        {/* Contact Information */}
        <Section title="13. Contact Us">
          <p>
            If you have any questions, concerns, or requests regarding this
            Privacy Policy or our data practices, please contact us:
          </p>
          <div className="mt-4 rounded-xl border border-border bg-surface p-6">
            <p className="font-semibold text-foreground">{companyName}</p>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <strong>Email:</strong>{" "}
                <a
                  href={`mailto:${contactEmail}`}
                  className="text-accent underline underline-offset-4 hover:text-accent-dark"
                >
                  {contactEmail}
                </a>
              </li>
              <li>
                <strong>Website:</strong>{" "}
                <a
                  href={websiteUrl}
                  className="text-accent underline underline-offset-4 hover:text-accent-dark"
                >
                  {websiteUrl}
                </a>
              </li>
              <li>
                <strong>Facebook:</strong>{" "}
                <a
                  href="https://www.facebook.com/profile.php?id=61576227956295"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent underline underline-offset-4 hover:text-accent-dark"
                >
                  Theta AI on Facebook
                </a>
              </li>
            </ul>
          </div>
        </Section>

        {/* Consent */}
        <Section title="14. Consent">
          <p>
            By using {appName}, you hereby consent to this Privacy Policy and
            agree to its terms. This includes consent for {appName} to:
          </p>
          <ul className="ml-6 list-disc space-y-2">
            <li>
              Receive and process public post and comment data when you mention
              our Page.
            </li>
            <li>
              Receive and process messages you send to us via Facebook Messenger.
            </li>
            <li>
              Send AI-generated replies to your posts, comments, or messages.
            </li>
            <li>
              Use third-party AI services (Google Gemini) to analyze public
              content.
            </li>
          </ul>
        </Section>

        {/* Footer separator */}
        <div className="mt-16 border-t border-border pt-8">
          <p className="text-center text-sm text-muted">
            &copy; {new Date().getFullYear()} {companyName}. All rights
            reserved.
            <br />
            <Link
              href="/"
              className="mt-1 inline-block text-accent underline underline-offset-4 hover:text-accent-dark"
            >
              Return to Home
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
