interface LegendItem {
  name: string
  color: string
}

export function GraphLegend({ items }: { items: LegendItem[] }) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      {items.map((item) => (
        <div key={item.name} className="flex items-center gap-1">
          <span
            className="inline-block h-2 w-2"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-[9px]" style={{ color: 'var(--text-muted)' }}>
          {item.name}
        </span>
        </div>
      ))}
    </div>
  )
}
