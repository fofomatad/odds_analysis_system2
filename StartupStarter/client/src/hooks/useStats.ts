import { useState, useEffect } from 'react'

interface Stats {
  winRate: number
  avgPoints: number
  currentForm: string
  performanceHistory: {
    date: string
    score: number
  }[]
}

export function useStats(team: string | null) {
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    if (!team) {
      setStats(null)
      return
    }

    const fetchStats = async () => {
      try {
        const response = await fetch(`/api/stats/${team}`)
        const data = await response.json()
        setStats(data)
      } catch (error) {
        console.error('Error fetching stats:', error)
      }
    }

    fetchStats()
  }, [team])

  return { stats }
}
