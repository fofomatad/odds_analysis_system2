import { useState } from 'react'
import ScoreBoard from './ScoreBoard'
import StatisticsPanel from './StatisticsPanel'
import BettingInsights from './BettingInsights'
import TeamComparison from './TeamComparison'

export default function Dashboard() {
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null)
  
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold">Sports Analytics Dashboard</h1>
      </header>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ScoreBoard onTeamSelect={setSelectedTeam} />
        </div>
        
        <div className="space-y-6">
          <BettingInsights selectedTeam={selectedTeam} />
        </div>
        
        <div className="lg:col-span-2">
          <StatisticsPanel selectedTeam={selectedTeam} />
        </div>
        
        <div className="lg:col-span-3">
          <TeamComparison />
        </div>
      </div>
    </div>
  )
}
