import Link from "next/link"

const contactEmail = "Rishna.renikunta@gmail.com"

const team = [
  {
    name: "Rishna Renikunta",
    role: "Team Lead / Backend Developer",
    // focus: "Backend architecture, APIs, and integrations",
  },
  {
    name: "Nidhi Majoju",
    role: "Scrum Master / Backend Developer",
    // focus: "Roadmap, delivery, and data science workflows",
  },
  {
    name: "Nivedha Sreenivasan",
    role: "Data Scientist",
    // focus: "Narrative extraction, clustering, and evaluation",
  },
  {
    name: "Aaryaa Moharir",
    role: "Backend Developer",
    // focus: "Pipelines, services, and performance",
  },
  {
    name: "Abhiram Tadepalli",
    role: "Data Scientist",
    // focus: "Modeling, analytics, and product instrumentation",
  },
  {
    name: "Zubiya Syeda",
    role: "Frontend Developer",
    // focus: "UX, UI systems, and Next.js implementation",
  },
]

const faqs = [
  {
    q: "What’s the fastest way to get help?",
    a: `Email us at ${contactEmail} with a short description of what you’re trying to do, plus any relevant links or screenshots.`,
  },
  {
    q: "Can we request a demo or walkthrough?",
    a: "Yes. Tell us your goal (e.g., creator vetting, destination marketing, brand-safety reviews) and we’ll tailor a walkthrough.",
  },
  {
    q: "How should we report a bug?",
    a: "Include steps to reproduce, what you expected, what happened, your browser/device, and (if possible) a screenshot.",
  },
]

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">
        <header className="space-y-3">
          <p className="text-xs uppercase tracking-[0.3em] text-gray-400">Contact</p>
          <h1 className="text-4xl font-semibold leading-tight">Let’s talk narratives, creators, and brand safety</h1>
          <p className="text-sm text-gray-300 max-w-3xl">
            Questions, feedback, or collaboration ideas? Reach out and we’ll connect you with the right person on the
            team.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-6 shadow-2xl shadow-black/40">
            <p className="text-[11px] uppercase tracking-[0.25em] text-gray-400">Primary channel</p>
            <h2 className="mt-2 text-xl font-semibold">Email us</h2>
            <p className="mt-2 text-sm text-gray-300">
              Use email for product questions, demos, partnerships, and general support.
            </p>
            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
              <a
                href={`mailto:${contactEmail}?subject=${encodeURIComponent("YouTravel — Contact request")}`}
                className="inline-flex items-center justify-center rounded-xl bg-[#E4CAFF] px-4 py-2 text-sm font-medium text-[#1c1b22] transition hover:bg-white/80"
              >
                {contactEmail}
              </a>
              <Link
                href="/about"
                className="inline-flex items-center justify-center rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10"
              >
                Learn more
              </Link>
            </div>
            <p className="mt-3 text-xs text-gray-400">
              Tip: include what you’re trying to do, the page you were on, and any screenshots that help.
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-inner shadow-black/30">
            <div className="space-y-1">
              <h2 className="text-lg font-semibold">What to include</h2>
              <p className="text-sm text-gray-300">A few details help us respond faster.</p>
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <Bullet title="Goal" body="What decision you’re trying to make." />
              <Bullet title="Context" body="Creator, narrative, or destination links." />
              <Bullet title="Timing" body="Any deadlines or launch windows." />
              <Bullet title="Artifacts" body="Screenshots or export files (if any)." />
            </div>
          </div>
        </section>

        <section className="space-y-4">
          <div className="space-y-1">
            <h2 className="text-lg font-semibold">Meet the team</h2>
            <p className="text-sm text-gray-300">
              A cross-functional crew building narrative intelligence end-to-end.
            </p>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {team.map((member) => (
              <TeamCard key={member.name} name={member.name} role={member.role} />
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-6 shadow-2xl shadow-black/40 space-y-4">
          <div className="space-y-1">
            <h2 className="text-lg font-semibold">FAQ</h2>
            <p className="text-sm text-gray-300">Quick answers to common outreach questions.</p>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            {faqs.map((item) => (
              <details
                key={item.q}
                className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 open:bg-white/10 transition-colors"
              >
                <summary className="cursor-pointer select-none text-sm font-semibold text-white">{item.q}</summary>
                <p className="mt-2 text-sm text-gray-300 leading-relaxed">{item.a}</p>
              </details>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

function Bullet({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-[#0f0f17] px-4 py-3">
      <p className="text-sm font-semibold text-white">{title}</p>
      <p className="mt-1 text-sm text-gray-300">{body}</p>
    </div>
  )
}

function TeamCard({ name, role }: { name: string; role: string }) {
  return (
    <div className="group rounded-2xl border border-white/10 bg-[#0f0f17] p-5 shadow-2xl shadow-black/40 transition-colors hover:bg-[#E4CAFF] hover:text-gray-950">
      <p className="text-[11px] uppercase tracking-[0.25em] text-gray-400 transition-colors group-hover:text-gray-800">
        {role}
      </p>
      <p className="mt-2 text-lg font-semibold text-white transition-colors group-hover:text-gray-950">{name}</p>
      {/* <p className="mt-2 text-sm text-gray-300 leading-relaxed">{focus}</p> */}
    </div>
  )
}
