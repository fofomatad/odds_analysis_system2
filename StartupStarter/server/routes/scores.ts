import express from 'express'
import { db } from '../index'
import { games } from '../../db/schema'
import { eq } from 'drizzle-orm'

export const scoresRouter = express.Router()

scoresRouter.get('/', async (req, res) => {
  try {
    const liveGames = await db.select().from(games)
      .where(eq(games.status, 'live'))
    res.json(liveGames)
  } catch (error) {
    console.error('Error fetching scores:', error)
    res.status(500).json({ error: 'Internal server error' })
  }
})
