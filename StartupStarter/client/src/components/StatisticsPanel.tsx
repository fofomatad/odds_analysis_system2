import { useStats } from '../hooks/useStats'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface StatisticsPanelProps {
  selectedTeam: string | null
}

export default function StatisticsPanel({ selectedTeam }: StatisticsPanelProps) {
  const { stats } = useStats(selectedTeam)

  return (
    <div className="rounded-lg bg-card p-6">
      <h2 className="text-2xl font-semibold mb-4">Performance Statistics</h2>
      
      {selectedTeam ? (
        <div className="space-y-6">
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats?.performanceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke="hsl(var(--primary))" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-accent rounded-lg">
              <h3 className="text-sm font-medium text-muted-foreground">Win Rate</h3>
              <p className="text-2xl font-bold">{stats?.winRate}%</p>
            </div>
            <div className="p-4 bg-accent rounded-lg">
              <h3 className="text-sm font-medium text-muted-foreground">Avg Points</h3>
              <p className="text-2xl font-bold">{stats?.avgPoints}</p>
            </div>
            <div className="p-4 bg-accent rounded-lg">
              <h3 className="text-sm font-medium text-muted-foreground">Form</h3>
              <p className="text-2xl font-bold">{stats?.currentForm}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-muted-foreground py-12">
          Select a team to view statistics
        </div>
      )}
    </div>
  )
}
