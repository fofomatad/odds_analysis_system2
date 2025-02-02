import { pgTable, text, serial, integer, timestamp, jsonb, decimal, boolean } from "drizzle-orm/pg-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";
import { relations } from "drizzle-orm";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").unique().notNull(),
  password: text("password").notNull(),
});

export const players = pgTable("players", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  team: text("team").notNull(),
  stats: jsonb("stats").$type<{
    points: number;
    assists: number;
    rebounds: number;
    gamesPlayed: number;
    fg_percentage: number;
    three_point_percentage: number;
    ft_percentage: number;
    clutch_performance: number;
    lastPerformance: number[];
  }>().notNull(),
  psychologicalProfile: jsonb("psychological_profile").$type<{
    pressureHandling: number;
    consistency: number;
    rivalryPerformance: number;
    mediaImpact: number;
    recoveryTrend: number;
  }>(),
  healthStatus: jsonb("health_status").$type<{
    injuryHistory: string[];
    fatigueLevel: number;
    lastInjuryDate?: string;
    minutesLoad: number;
  }>(),
  lastUpdated: timestamp("last_updated").notNull(),
});

export const playerStats = pgTable("player_stats", {
  id: serial("id").primaryKey(),
  playerId: integer("player_id").notNull(),
  gameDate: timestamp("game_date").notNull(),
  isHome: boolean("is_home").notNull(),
  points: integer("points").notNull(),
  rebounds: integer("rebounds").notNull(),
  assists: integer("assists").notNull(),
  minutes: integer("minutes").notNull(),
  fieldGoalsMade: integer("fg_made").notNull(),
  fieldGoalsAttempted: integer("fg_attempted").notNull(),
  threePointsMade: integer("three_made").notNull(),
  threePointsAttempted: integer("three_attempted").notNull(),
  freeThrowsMade: integer("ft_made").notNull(),
  freeThrowsAttempted: integer("ft_attempted").notNull(),
  clutchTime: boolean("clutch_time").default(false).notNull(),
  quarterPoints: jsonb("quarter_points").$type<number[]>().notNull(),
  result: text("result").notNull(),
});

export const playerProps = pgTable("player_props", {
  id: serial("id").primaryKey(),
  playerId: integer("player_id").notNull(),
  gameId: integer("game_id").notNull(),
  statType: text("stat_type").notNull(),
  line: decimal("line").notNull(),
  odds: decimal("odds").notNull(),
  prediction: decimal("prediction").notNull(),
  confidence: decimal("confidence").notNull(),
  valueRating: decimal("value_rating").notNull(),
   contextualFactors: jsonb("contextual_factors").$type<{
    restDays: number;
    backToBack: boolean;
    rivalryGame: boolean;
    homeAdvantage: number;
  }>(),
  timestamp: timestamp("timestamp").notNull(),
});

export const playerTrends = pgTable("player_trends", {
  id: serial("id").primaryKey(),
  playerId: integer("player_id").notNull(),
  date: timestamp("date").notNull(),
  trendType: text("trend_type").notNull(),
  value: decimal("value").notNull(),
  direction: text("direction").notNull(),
  strength: decimal("strength").notNull(),
  confidence: decimal("confidence").notNull(),
});

export const systemStats = pgTable("system_stats", {
  id: serial("id").primaryKey(),
  timestamp: timestamp("timestamp").notNull(),
  cpuPercent: decimal("cpu_percent").notNull(),
  memoryPercent: decimal("memory_percent").notNull(),
  diskPercent: decimal("disk_percent").notNull(),
  networkBytesSent: decimal("network_bytes_sent").notNull(),
  networkBytesRecv: decimal("network_bytes_recv").notNull(),
  threadCount: integer("thread_count").notNull(),
});

export const games = pgTable("games", {
  id: serial("id").primaryKey(),
  homeTeam: text("home_team").notNull(),
  awayTeam: text("away_team").notNull(),
  status: text("status").notNull(),
  score: jsonb("score").$type<{
    home: number;
    away: number;
    quarter: number;
  }>().notNull(),
  timestamp: timestamp("timestamp").notNull(),
});

export const odds = pgTable("odds", {
  id: serial("id").primaryKey(),
  gameId: integer("game_id").notNull(),
  homeOdds: integer("home_odds").notNull(),
  awayOdds: integer("away_odds").notNull(),
  confidence: integer("confidence").notNull(),
  timestamp: timestamp("timestamp").notNull(),
});

export const alerts = pgTable("alerts", {
  id: serial("id").primaryKey(),
  type: text("type").notNull(),
  message: text("message").notNull(),
  matchId: text("match_id"),
  timestamp: timestamp("timestamp").notNull(),
  status: text("status").default("pending").notNull(),
  metadata: jsonb("metadata").$type<{
    odds?: {
      home: number;
      away: number;
    };
    confidence?: number;
    profit?: number;
  }>(),
});

// Relations
export const gameRelations = relations(games, ({ many }) => ({
  odds: many(odds),
  playerProps: many(playerProps),
  alerts: many(alerts, {
    fields: [games.id],
    references: [alerts.matchId],
  }),
}));

export const playerRelations = relations(players, ({ many }) => ({
  stats: many(playerStats),
  props: many(playerProps),
  trends: many(playerTrends),
}));

export const oddsRelations = relations(odds, ({ one }) => ({
  game: one(games, {
    fields: [odds.gameId],
    references: [games.id],
  }),
}));

export const alertRelations = relations(alerts, ({ one }) => ({
  game: one(games, {
    fields: [alerts.matchId],
    references: [games.id],
  }),
}));

// Schemas for validation
export const insertUserSchema = createInsertSchema(users);
export const selectUserSchema = createSelectSchema(users);

// Types
export type InsertUser = typeof users.$inferInsert;
export type SelectUser = typeof users.$inferSelect;
export type Player = typeof players.$inferSelect;
export type Game = typeof games.$inferSelect;
export type Odds = typeof odds.$inferSelect;
export type Alert = typeof alerts.$inferSelect;
export type PlayerStats = typeof playerStats.$inferSelect;
export type PlayerProps = typeof playerProps.$inferSelect;
export type PlayerTrends = typeof playerTrends.$inferSelect;
export type SystemStats = typeof systemStats.$inferSelect;