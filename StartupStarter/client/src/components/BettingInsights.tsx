interface BettingInsightsProps {
  selectedTeam: string | null
}

export default function BettingInsights({ selectedTeam }: BettingInsightsProps) {
  return (
    <div className="rounded-lg bg-card p-6">
      <h2 className="text-2xl font-semibold mb-4">Betting Insights</h2>
      
      {selectedTeam ? (
        <div className="space-y-4">
          <div className="p-4 bg-accent rounded-lg">
            <h3 className="text-sm font-medium text-muted-foreground">Win Probability</h3>
            <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary"
                style={{ width: '65%' }}
              />
            </div>
            <p className="mt-2 text-2xl font-bold">65%</p>
          </div>
          
          <div className="p-4 bg-accent rounded-lg">
            <h3 className="text-sm font-medium text-muted-foreground">Suggested Bet</h3>
            <p className="text-lg font-medium mt-2">Money Line: -150</p>
            <p className="text-sm text-muted-foreground">Based on recent performance</p>
          </div>
          
          <div className="p-4 bg-accent rounded-lg">
            <h3 className="text-sm font-medium text-muted-foreground">Key Factors</h3>
            <ul className="mt-2 space-y-2 text-sm">
              <li>• Strong home record</li>
              <li>• Key player returning</li>
              <li>• Historical matchup advantage</li>
            </ul>
          </div>
        </div>
      ) : (
        <div className="text-center text-muted-foreground py-12">
          Select a team to view insights
        </div>
      )}
    </div>
  )
}
