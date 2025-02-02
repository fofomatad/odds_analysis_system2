import { useScores } from '../hooks/useScores'

interface ScoreBoardProps {
  onTeamSelect: (team: string) => void
}

export default function ScoreBoard({ onTeamSelect }: ScoreBoardProps) {
  const { scores, isLoading } = useScores()

  if (isLoading) {
    return (
      <div className="rounded-lg bg-card p-6">
        <h2 className="text-2xl font-semibold mb-4">Live Scores</h2>
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-muted rounded" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-lg bg-card p-6">
      <h2 className="text-2xl font-semibold mb-4">Live Scores</h2>
      <div className="space-y-4">
        {scores?.map((game) => (
          <div 
            key={game.id}
            className="flex items-center justify-between p-4 bg-accent rounded-lg cursor-pointer hover:bg-accent/90"
            onClick={() => onTeamSelect(game.homeTeam)}
          >
            <div className="flex items-center space-x-4">
              <span className="font-medium">{game.homeTeam}</span>
              <span className="text-2xl font-bold">{game.homeScore}</span>
            </div>
            <div className="text-muted-foreground">vs</div>
            <div className="flex items-center space-x-4">
              <span className="text-2xl font-bold">{game.awayScore}</span>
              <span className="font-medium">{game.awayTeam}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
