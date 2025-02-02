import express from 'express'
import { db } from '../index'
import { games, teams } from '../../db/schema'
import { eq, and } from 'drizzle-orm'

export const statsRouter = express.Router()

statsRouter.get('/:team', async (req, res) => {
  const { team } = req.params

  try {
    const teamStats = await db.select()
      .from(teams)
      .where(eq(teams.name, team))
      .limit(1)

    if (!teamStats.length) {
      return res.status(404).json({ error: 'Team not found' })
    }

    const recentGames = await db.select()
      .from(games)
      .where(
        and(
          eq(games.status, 'finished'),
          eq(games.homeTeam, team)
        )
      )
      .limit(10)

    res.json({
      winRate: teamStats[0].winRate,
      avgPoints: teamStats[0].avgPoints,
      currentForm: teamStats[0].currentForm,
      performanceHistory: recentGames.map(game => ({
        date: game.date,
        score: game.homeScore
      }))
    })
  } catch (error) {
    console.error('Error fetching stats:', error)
    res.status(500).json({ error: 'Internal server error' })
  }
})
