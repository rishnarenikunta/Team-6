export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
      <div className="max-w-5xl mx-auto px-6 pb-16 pt-12 space-y-10">
        <header className="space-y-3">
          <p className="text-xs uppercase tracking-[0.3em] text-gray-400">About</p>
          <h1 className="text-4xl font-semibold leading-tight">Travel narrative intelligence for brand-safe decisions</h1>
          <p className="text-sm text-gray-300 max-w-3xl">
            This app helps you monitor emerging travel narratives and creator signals, so you can move faster on
            sponsorship and destination marketing decisions.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          <Card
            title="Creators"
            body="Browse channels with recent video context, audience engagement, and clustering-based signals."
          />
          <Card
            title="Narratives"
            body="Track storyline clusters by destination and review related claims and supporting content."
          />
          <Card
            title="Claims"
            body="Surface high-signal statements with risk labels to support brand safety reviews."
          />
        </section>

        <section className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-inner shadow-black/30 space-y-4">
          <div className="space-y-1">
            <h2 className="text-lg font-semibold">What you can do</h2>
            <p className="text-sm text-gray-300">A quick overview of the main workflows.</p>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <Bullet title="Explore creators" body="Open a creator to review recent videos, trending narratives, and claims." />
            <Bullet title="Audit a narrative" body="Open a narrative to see clustered claims and the destination context." />
            <Bullet title="Filter fast" body="Use subscribers and views filters to narrow to the right partners." />
            <Bullet title="Share context" body="Use links to send teammates directly to creator and narrative detail pages." />
          </div>
        </section>

        <section className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-6 shadow-2xl shadow-black/40 space-y-3">
          <h2 className="text-lg font-semibold">Data notes</h2>
          <p className="text-sm text-gray-300">
            Metrics and clusters are derived from stored video metadata, narrative extraction, and downstream clustering
            outputs.
          </p>
        </section>
      </div>
    </div>
  )
}

function Card({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#0f0f17] p-5 shadow-2xl shadow-black/40">
      <p className="text-[11px] uppercase tracking-[0.25em] text-gray-400">{title}</p>
      <p className="mt-2 text-sm text-gray-200 leading-relaxed">{body}</p>
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
