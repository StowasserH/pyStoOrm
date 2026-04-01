/**
 * Configuration Management
 *
 * Loads configuration from environment variables.
 * Supports local .env files via dotenv.
 */

import * as fs from 'fs';
import * as path from 'path';

export interface AppConfig {
  env: 'development' | 'production' | 'test';
  port: number;
  host: string;
  logLevel: string;
  database: {
    host: string;
    port: number;
    user: string;
    password: string;
    database: string;
  };
}

/**
 * Load environment variables from .env file if it exists.
 *
 * @param envPath Path to .env file
 */
export function loadDotenv(envPath: string = '.env'): void {
  if (fs.existsSync(envPath)) {
    const env = fs.readFileSync(envPath, 'utf-8');
    env.split('\n').forEach((line) => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const [key, value] = trimmed.split('=');
        if (key && value) {
          // Only set if not already set
          if (!process.env[key]) {
            process.env[key] = value.trim();
          }
        }
      }
    });
  }
}

/**
 * Get application configuration from environment.
 *
 * @returns AppConfig object
 */
export function getConfig(): AppConfig {
  return {
    env: (process.env.NODE_ENV as 'development' | 'production' | 'test') || 'development',
    port: parseInt(process.env.PORT || '3000', 10),
    host: process.env.HOST || '0.0.0.0',
    logLevel: process.env.LOG_LEVEL || 'info',
    database: {
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT || '5432', 10),
      user: process.env.DB_USER || 'postgres',
      password: process.env.DB_PASSWORD || '',
      database: process.env.DB_NAME || 'postgres',
    },
  };
}

/**
 * Validate required configuration values.
 *
 * @param requiredVars Array of required environment variable names
 * @throws Error if any required variable is missing
 */
export function validateConfig(requiredVars: string[]): void {
  const missing = requiredVars.filter((key) => !process.env[key]);
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }
}
