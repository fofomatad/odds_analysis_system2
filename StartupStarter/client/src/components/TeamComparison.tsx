import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar } from 'recharts'

const data = [
  { subject: 'Offense', A: 120, B: 110, fullMark: 150 },
  { subject: 'Defense', A: 98, B: 130, fullMark: 150 },
  { subject: 'Speed', A: 86, B: 130, fullMark: 150 },
  { subject: 'Power', A: 99, B: 100, fullMark: 150 },
  { subject: 'Stamina', A: 85, B: 90, fullMark: 150 },
  { subject: 'Technique', A: 65, B: 85, fullMark: 150 },
]

export default function TeamComparison() {
  return (
    <div className="rounded-lg bg-card p-6">
      <h2 className="text-2xl font-semibold mb-4">Team Comparison</h2>
      
      <div className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
            <PolarGrid />
            <PolarAngleAxis dataKey="subject" />
            <Radar
              name="Team A"
              dataKey="A"
              stroke="hsl(var(--primary))"
              fill="hsl(var(--primary))"
              fillOpacity={0.6}
            />
            <Radar
              name="Team B"
              dataKey="B"
              stroke="hsl(var(--secondary))"
              fill="hsl(var(--secondary))"
              fillOpacity={0.6}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
