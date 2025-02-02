import { useState, useEffect } from 'react'

interface Game {
  id: string
  homeTeam: string
  awayTeam: string
  homeScore: number
  awayScore: number
  status: 'live' | 'finished' | 'scheduled'
}

export function useScores() {
  const [scores, setScores] = useState<Game[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchScores = async () => {
      try {
        const response = await fetch('/api/scores')
        const data = await response.json()
        setScores(data)
      } catch (error) {
        console.error('Error fetching scores:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchScores()
    
    // Poll for updates every 30 seconds
    const interval = setInterval(fetchScores, 30000)
    return () => clearInterval(interval)
  }, [])

  return { scores, isLoading }
}
