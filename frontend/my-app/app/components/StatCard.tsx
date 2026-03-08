// app/components/StatCard.tsx
import Link from "next/link"

type StatCardProps = {
  title: string
  value: string | number
  subtitle?: string
  growth?: string
  href?: string        // new
}

export default function StatCard(props: StatCardProps) {
  const CardBody = (
    <div className="bg-[#E4CAFF] border border-black rounded-2xl p-6 shadow-lg hover:border-white transition-all duration-200 h-full">
      <p className="text-sm text-[#000000] mb-2">{props.title}</p>
      <div className="flex items-end justify-between">
        <h2 className="text-3xl font-semibold text-black">{props.value}</h2>
        {props.growth && <span className="text-sm text-neutral-300">{props.growth}</span>}
      </div>
      {props.subtitle && <p className="text-xs text-neutral-500 mt-2">{props.subtitle}</p>}
    </div>
  )

  return props.href ? (
    <Link href={props.href} className="block focus:outline-none focus:ring-2 focus:ring-white/60">
      {CardBody}
    </Link>
  ) : (
    CardBody
  )
}
