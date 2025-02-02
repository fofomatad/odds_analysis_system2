import express from 'express'
import cors from 'cors'
import { scoresRouter } from './routes/scores'
import { statsRouter } from './routes/stats'
import { drizzle } from 'drizzle-orm/neon-serverless'
import { Pool } from '@neondatabase/serverless'

const app = express()
const port = 8000

// Database connection
const pool = new Pool({ connectionString: process.env.DATABASE_URL })
export const db = drizzle(pool)

app.use(cors())
app.use(express.json())

// Routes
app.use('/api/scores', scoresRouter)
app.use('/api/stats', statsRouter)

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy' })
})

app.listen(port, '0.0.0.0', () => {
  console.log(`Server running on port ${port}`)
})
