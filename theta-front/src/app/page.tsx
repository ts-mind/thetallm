import Link from "next/link";

function BrainIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 2a7 7 0 0 0-7 7c0 3 1.5 5.5 4 7v2h6v-2c2.5-1.5 4-4 4-7a7 7 0 0 0-7-7Z" />
      <path d="M9 22h6" />
      <path d="M10 18h4" />
      <path d="M12 2v4" />
      <path d="M8 6l2 2" />
      <path d="M16 6l-2 2" />
    </svg>
  );
}

function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.3-4.3" />
    </svg>
  );
}

function BoltIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  );
}

function GlobeIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <ellipse cx="12" cy="12" rx="4" ry="10" />
      <path d="M2 12h20" />
    </svg>
  );
}

const features = [
  {
    icon: SearchIcon,
    title: "Real-Time Verification",
    description:
      "Theta uses search-grounded AI to cross-reference claims against live sources before responding.",
  },
  {
    icon: BoltIcon,
    title: "Instant Response",
    description:
      "Mention Theta on any post and receive a fact-checked reply within seconds, powered by Gemini 2.0 Flash.",
  },
  {
    icon: ShieldIcon,
    title: "Source-Cited Replies",
    description:
      "Every response includes verifiable sources so users can check the facts for themselves.",
  },
  {
    icon: GlobeIcon,
    title: "Context-Aware",
    description:
      "Theta walks the entire post tree — reading parent content, images, and thread context before replying.",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="fixed top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-white">
              <span className="text-sm font-bold">T</span>
            </div>
            <span className="text-lg font-semibold tracking-tight">
              Theta LLM
            </span>
          </div>
          <div className="flex items-center gap-6">
            <Link
              href="/privacy"
              className="text-sm text-muted transition-colors hover:text-foreground"
            >
              Privacy Policy
            </Link>
            <a
              href="https://github.com/ts-mind/thetallm"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-dark"
            >
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-32 pb-20">
        {/* Background gradient */}
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute left-1/2 top-0 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-accent/5 blur-3xl" />
        </div>

        <div className="mx-auto max-w-6xl px-6">
          <div className="mx-auto max-w-3xl text-center">
            {/* Badge */}
            <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-border bg-surface px-4 py-1.5 text-sm text-muted">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
              </span>
              System Operational
            </div>

            <h1 className="text-4xl font-bold leading-tight tracking-tight sm:text-5xl md:text-6xl">
              AI That Verifies
              <br />
              <span className="bg-gradient-to-r from-accent to-accent-light bg-clip-text text-transparent">
                Before You Believe
              </span>
            </h1>

            <p className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-muted">
              Theta is a research AI entity by{" "}
              <span className="font-medium text-foreground">
                TeraMind
              </span>
              , a lab of TService. It monitors social media mentions, verifies
              claims against live sources, and replies with cited facts — all in
              real time.
            </p>

            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <a
                href="https://www.facebook.com/thetallm/"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-accent px-8 text-sm font-medium text-white shadow-lg shadow-accent/25 transition-all hover:bg-accent-dark hover:shadow-xl hover:shadow-accent/30"
              >
                <BrainIcon className="h-4 w-4" />
                Try Theta AI on Facebook
              </a>
              <a
                href="#how-it-works"
                className="inline-flex h-12 items-center justify-center rounded-xl border border-border px-8 text-sm font-medium transition-colors hover:bg-surface"
              >
                How It Works
              </a>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="mx-auto mt-20 grid max-w-2xl grid-cols-3 divide-x divide-border rounded-2xl border border-border bg-surface p-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-accent">Gemini 2.0</p>
              <p className="mt-1 text-xs text-muted">LLM Engine</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-accent">&lt; 5s</p>
              <p className="mt-1 text-xs text-muted">Avg. Response</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-accent">24/7</p>
              <p className="mt-1 text-xs text-muted">Always Online</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="how-it-works" className="py-24">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              How Theta Works
            </h2>
            <p className="mt-4 text-lg text-muted">
              A modular pipeline that transforms a simple mention into a
              verified, source-cited response.
            </p>
          </div>

          <div className="mt-16 grid gap-8 sm:grid-cols-2">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="group rounded-2xl border border-border bg-surface p-8 transition-all hover:border-accent/30 hover:shadow-lg hover:shadow-accent/5"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10 text-accent transition-colors group-hover:bg-accent group-hover:text-white">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-semibold">{feature.title}</h3>
                <p className="mt-2 leading-relaxed text-muted">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="border-t border-border py-24">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              The Pipeline
            </h2>
            <p className="mt-4 text-lg text-muted">
              From webhook event to verified reply in four steps.
            </p>
          </div>

          <div className="mx-auto mt-16 max-w-3xl">
            <div className="relative space-y-8">
              {/* Vertical line */}
              <div className="absolute left-6 top-6 bottom-6 w-px bg-border" />

              {[
                {
                  step: "01",
                  title: "Webhook Event",
                  desc: "Facebook sends a real-time notification when someone mentions Theta on a post or comment.",
                },
                {
                  step: "02",
                  title: "Context Fetch",
                  desc: 'Theta "walks up the tree" — fetching the parent post\'s text, images, and thread context via Graph API.',
                },
                {
                  step: "03",
                  title: "AI Analysis",
                  desc: "Gemini 2.0 Flash with search grounding verifies claims against live web sources and generates a response.",
                },
                {
                  step: "04",
                  title: "Cited Reply",
                  desc: "A concise, source-cited reply is posted back to the original thread within seconds.",
                },
              ].map((item) => (
                <div key={item.step} className="relative flex gap-6 pl-0">
                  <div className="z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-border bg-background font-mono text-sm font-bold text-accent">
                    {item.step}
                  </div>
                  <div className="pt-2">
                    <h3 className="font-semibold">{item.title}</h3>
                    <p className="mt-1 text-sm leading-relaxed text-muted">
                      {item.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12">
        <div className="mx-auto max-w-6xl px-6">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <div className="flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent text-white">
                <span className="text-xs font-bold">T</span>
              </div>
              <span className="text-sm font-medium">
                Theta AI by TeraMind
              </span>
            </div>
            <div className="flex items-center gap-6 text-sm text-muted">
              <Link
                href="/privacy"
                className="transition-colors hover:text-foreground"
              >
                Privacy Policy
              </Link>
              <a
                href="https://github.com/ts-mind/thetallm"
                target="_blank"
                rel="noopener noreferrer"
                className="transition-colors hover:text-foreground"
              >
                GitHub
              </a>
              <span>&copy; {new Date().getFullYear()} TService</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
