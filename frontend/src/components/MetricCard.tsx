export function MetricCard({ label, value, note, tone }: { label: string; value: number | string; note: string; tone?: string }) {
  return <article className={`metric-card ${tone ?? ""}`}><p>{label}</p><strong>{value}</strong><span>{note}</span></article>;
}
