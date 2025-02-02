import { pgTable, serial, text, integer, timestamp, decimal } from 'drizzle-orm/pg-core'

export const games = pgTable('games', {
  id: serial('id').primaryKey(),
  homeTeam: text('home_team').notNull(),
  awayTeam: text('away_team').notNull(),
  homeScore: integer('home_score').notNull(),
  awayScore: integer('away_score').notNull(),
  status: text('status').notNull(),
  date: timestamp('date').notNull(),
})

export const teams = pgTable('teams', {
  id: serial('id').primaryKey(),
  name: text('name').notNull().unique(),
  winRate: decimal('win_rate').notNull(),
  avgPoints: decimal('avg_points').notNull(),
  currentForm: text('current_form').notNull(),
})
