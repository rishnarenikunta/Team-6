"use client"

import { useState } from "react"

type ToggleKey = "emailAlerts" | "pushAlerts" | "weeklyDigest"

const initialToggles: Record<ToggleKey, boolean> = {
  emailAlerts: false,
  pushAlerts: false,
  weeklyDigest: false,
}

export default function SettingsPage() {
  const [toggles, setToggles] = useState<Record<ToggleKey, boolean>>(initialToggles)

  const handleToggle = (key: ToggleKey) => {
    setToggles((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0c0c12] via-[#0f1018] to-[#0c0c12] text-white">
      <div className="mx-auto max-w-5xl px-6 pb-16 pt-10 space-y-10">
        <header className="space-y-3">
          <p className="text-xs uppercase tracking-[0.3em] text-gray-400">Settings</p>
          <h1 className="text-4xl font-semibold leading-tight">Tune your workspace</h1>
          <p className="text-sm text-gray-400 max-w-2xl">
            Control alerts, data refresh cadence, and personal details without leaving the dashboard.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-3">
          <section className="lg:col-span-2 space-y-6">
            <Card title="Notifications" subtitle="Choose how we keep you in the loop.">
              <div className="space-y-4">
                <ToggleRow
                  label="Email alerts"
                  description="Creator risk changes, trend spikes, and saved narrative updates."
                  checked={toggles.emailAlerts}
                  onClick={() => handleToggle("emailAlerts")}
                />
                <ToggleRow
                  label="Push alerts"
                  description="Lightweight pings for trending destinations you follow."
                  checked={toggles.pushAlerts}
                  onClick={() => handleToggle("pushAlerts")}
                />
                <ToggleRow
                  label="Weekly digest"
                  description="Sunday wrap-up with deltas, winners, and watchouts."
                  checked={toggles.weeklyDigest}
                  onClick={() => handleToggle("weeklyDigest")}
                />
              </div>
            </Card>

            <Card title="Data preferences" subtitle="Adjust refresh cadence and region focus.">
              <div className="grid gap-4 md:grid-cols-2">
                <Field label="Primary region">
                  <select className="w-full rounded-xl border border-white/10 bg-[#16161e] px-4 py-3 text-sm text-gray-100 shadow-inner shadow-black/30 focus:border-white/25 focus:outline-none">
                    <option>Global</option>
                    <option>Americas</option>
                    <option>EMEA</option>
                    <option>APAC</option>
                  </select>
                </Field>
                <Field label="Auto-refresh">
                  <select className="w-full rounded-xl border border-white/10 bg-[#16161e] px-4 py-3 text-sm text-gray-100 shadow-inner shadow-black/30 focus:border-white/25 focus:outline-none">
                    <option>Every hour</option>
                    <option>Every 6 hours</option>
                    <option>Every 24 hours</option>
                  </select>
                </Field>
                <Field label="Default view">
                  <select className="w-full rounded-xl border border-white/10 bg-[#16161e] px-4 py-3 text-sm text-gray-100 shadow-inner shadow-black/30 focus:border-white/25 focus:outline-none">
                    <option>Discover</option>
                    <option>Narratives</option>
                    <option>Claims</option>
                  </select>
                </Field>
                <Field label="Confidence threshold">
                  <select className="w-full rounded-xl border border-white/10 bg-[#16161e] px-4 py-3 text-sm text-gray-100 shadow-inner shadow-black/30 focus:border-white/25 focus:outline-none">
                    <option>Standard (85%)</option>
                    <option>Conservative (90%)</option>
                    <option>Exploratory (75%)</option>
                  </select>
                </Field>
              </div>
            </Card>
          </section>

          <section className="space-y-6">
            <Card title="Profile" subtitle="Visible to teammates who share reports.">
              <div className="space-y-4">
                <Field label="Name">
                  <input
                    defaultValue="Avery Patel"
                    className="w-full rounded-xl border border-white/10 bg-[#16161e] px-4 py-3 text-sm text-gray-100 shadow-inner shadow-black/30 focus:border-white/25 focus:outline-none"
                  />
                </Field>
                <Field label="Email">
                  <input
                    type="email"
                    defaultValue="avery@atlas.co"
                    className="w-full rounded-xl border border-white/10 bg-[#16161e] px-4 py-3 text-sm text-gray-100 shadow-inner shadow-black/30 focus:border-white/25 focus:outline-none"
                  />
                </Field>
                <Field label="Time zone">
                  <select className="w-full rounded-xl border border-white/10 bg-[#16161e] px-4 py-3 text-sm text-gray-100 shadow-inner shadow-black/30 focus:border-white/25 focus:outline-none">
                    <option>UTC−06:00 (Chicago)</option>
                    <option>UTC−05:00 (New York)</option>
                    <option>UTC+00:00 (London)</option>
                    <option>UTC+09:00 (Tokyo)</option>
                  </select>
                </Field>
              </div>
            </Card>

            <Card title="Export" subtitle="Control formats and retention for downloads.">
              <div className="space-y-4">
                <Field label="Default format">
                  <select className="w-full rounded-xl border border-white/10 bg-[#16161e] px-4 py-3 text-sm text-gray-100 shadow-inner shadow-black/30 focus:border-white/25 focus:outline-none">
                    <option>PDF summary</option>
                    <option>CSV rows</option>
                    <option>Slides (PPTX)</option>
                  </select>
                </Field>
                <div className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                  <input id="anonymize" type="checkbox" defaultChecked className="mt-1 accent-indigo-400" />
                  <label htmlFor="anonymize" className="text-sm text-gray-200">
                    Anonymize creator handles on exports
                    <span className="block text-xs text-gray-400">
                      Removes channel names and links from public share-outs.
                    </span>
                  </label>
                </div>
              </div>
            </Card>
          </section>
        </div>
      </div>
    </div>
  )
}

type CardProps = {
  title: string
  subtitle: string
  children: React.ReactNode
}

function Card({ title, subtitle, children }: CardProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#181824] via-[#11111b] to-[#0c0c12] p-5 shadow-xl shadow-black/40">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold text-white">{title}</h2>
        <p className="text-sm text-gray-400">{subtitle}</p>
      </div>
      <div className="mt-4">{children}</div>
    </div>
  )
}

type FieldProps = {
  label: string
  children: React.ReactNode
}

function Field({ label, children }: FieldProps) {
  return (
    <label className="space-y-2 text-sm font-medium text-gray-200">
      <span className="block text-xs uppercase tracking-[0.18em] text-gray-400">{label}</span>
      {children}
    </label>
  )
}

type ToggleRowProps = {
  label: string
  description: string
  checked: boolean
  onClick: () => void
}

function ToggleRow({ label, description, checked, onClick }: ToggleRowProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex w-full items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-left transition hover:-translate-y-0.5 hover:border-white/25"
    >
      <div className="space-y-1">
        <p className="text-sm font-semibold text-white">{label}</p>
        <p className="text-xs text-gray-400">{description}</p>
      </div>
      <span
        className={`relative inline-flex h-7 w-12 items-center rounded-full transition ${
          checked ? "bg-indigo-400/80" : "bg-white/10"
        }`}
      >
        <span
          className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-md transition ${
            checked ? "translate-x-5" : "translate-x-1"
          }`}
        />
      </span>
    </button>
  )
}
