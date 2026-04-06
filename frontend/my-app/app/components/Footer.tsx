import Link from "next/link"

type LinkGroup = {
  title: string
  links: { label: string; href: string; badge?: string }[]
}

const linkGroups: LinkGroup[] = [
  {
    title: "Product",
    links: [
      { label: "Dashboard", href: "/" },
      { label: "Narratives", href: "/narratives" },
      { label: "Creators", href: "/creators", badge: "New" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", href: "/about" },
      { label: "Contact", href: "/contact" },
      { label: "Changelog", href: "/changelog" },
    ],
  },
  {
    title: "Support",
    links: [
      { label: "Docs", href: "/docs" },
      { label: "Status", href: "/status" },
      { label: "Security", href: "/security" },
    ],
  },
]

export default function Footer() {
  return (
    <footer className="mt-12 border-t border-white/10 bg-gradient-to-b from-[#0b0b12] via-[#0a0a14] to-[#06060c] text-gray-200">
      <div className="mx-auto max-w-6xl px-6 py-10 space-y-10">
        <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-md space-y-3">
            <p className="text-xs uppercase tracking-[0.3em] text-[#E4CAFF]">YouTravel platform</p>
            <h2 className="text-2xl font-semibold text-[#E4CAFF]">Narratives, creators, and risk in one place.</h2>
            <p className="text-sm text-gray-400">
              Hourly signals from video uploads, comments, and sentiment to keep sponsorships brand-safe and on-message.
            </p>
            <div className="flex flex-wrap gap-3 text-[11px] uppercase tracking-wide text-gray-100">
              <span className="rounded-full bg-[#E4CAFF]/50 px-3 py-1 text-[#E4CAFF]-200">Realtime signals</span>
              <span className="rounded-full bg-white/10 px-3 py-1">Sentiment scoring</span>
              <span className="rounded-full bg-white/10 px-3 py-1">Creator risk</span>
            </div>
          </div>

          <div className="grid flex-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {linkGroups.map((group) => (
              <div key={group.title} className="space-y-3">
                <p className="text-xs uppercase tracking-[0.2em] text-gray-400">{group.title}</p>
                <ul className="space-y-2 text-sm">
                  {group.links.map((item) => (
                    <li key={item.label} className="flex items-center gap-2">
                      <Link
                        href={item.href}
                        className="text-gray-200 hover:text-white transition-colors underline-offset-4 hover:underline"
                      >
                        {item.label}
                      </Link>
                      {item.badge && (
                        <span className="rounded-full bg-[#E4CAFF]/15 px-2 py-0.5 text-[11px] uppercase tracking-wide text-[#E4CAFF]">
                          {item.badge}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-4 border-t border-white/10 pt-6 text-xs text-gray-400 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-gray-300">© {new Date().getFullYear()} YouTravel</span>
            <span className="hidden sm:inline text-gray-600">·</span>
            <span>Signals refreshed hourly • Data coverage: YouTube</span>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Link href="/privacy" className="hover:text-white transition-colors">
              Privacy
            </Link>
            <span className="text-gray-600">/</span>
            <Link href="/terms" className="hover:text-white transition-colors">
              Terms
            </Link>
            <span className="text-gray-600">/</span>
            <Link href="mailto:hello@youtravel.ai" className="hover:text-white transition-colors">
              hello@youtravel.ai
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
