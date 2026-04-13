type StatCardProps = {
  title: string
  value: string | number
  subtitle?: string
  growth?: string
}

export default function StatCard({
  title,
  value,
  subtitle,
  growth,
}: StatCardProps) {
  return (
    <div className="
      bg-[#E4CAFF]
      border border-[#ffffff]
      rounded-2xl
      p-6
      shadow-lg
      hover:border-neutral-700
      transition-all duration-200
    ">
      <p className="text-sm text-[#000000] mb-2">
        {title}
      </p>

      <div className="flex items-end justify-between">
        <h2 className="text-3xl font-semibold text-black">
          {value}
        </h2>

        {growth && (
          <span className="text-sm text-neutral-300">
            {growth}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="text-xs text-neutral-500 mt-2">
          {subtitle}
        </p>
      )}
    </div>
  )
}
