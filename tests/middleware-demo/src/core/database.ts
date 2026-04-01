/**
 * PostgreSQL Database Connection Pool Manager
 *
 * Manages connection pooling to PostgreSQL database.
 * Provides health checks and graceful shutdown.
 */

import { Pool, PoolClient, QueryResult } from 'pg';
import { Logger } from './logger';

export interface DatabaseConfig {
  connectionString?: string;
  host?: string;
  port?: number;
  database?: string;
  user?: string;
  password?: string;
  max?: number;
  idleTimeoutMillis?: number;
  connectionTimeoutMillis?: number;
}

/**
 * Database Connection Pool Manager
 *
 * Wraps pg Pool and provides utility methods.
 */
export class Database {
  private pool: Pool;
  private logger: Logger;
  private isConnected: boolean = false;

  constructor(config: DatabaseConfig, logger?: Logger) {
    this.logger = logger || new Logger();

    // Build pool config from connection string or individual params
    let poolConfig: any = {};

    if (config.connectionString) {
      poolConfig.connectionString = config.connectionString;
    } else {
      poolConfig = {
        host: config.host || process.env.DB_HOST || 'localhost',
        port: config.port || Number(process.env.DB_PORT) || 5432,
        database: config.database || process.env.DB_NAME || 'postgres',
        user: config.user || process.env.DB_USER || 'postgres',
        password: config.password || process.env.DB_PASSWORD || '',
      };
    }

    // Set pool options
    poolConfig.max = config.max || 20;
    poolConfig.idleTimeoutMillis = config.idleTimeoutMillis || 30000;
    poolConfig.connectionTimeoutMillis = config.connectionTimeoutMillis || 2000;

    this.pool = new Pool(poolConfig);

    // Handle pool errors
    this.pool.on('error', (error) => {
      this.logger.error('Unexpected error on idle client', { error: error.message });
    });
  }

  /**
   * Connect to database and verify connection.
   *
   * @throws Error if connection fails
   */
  async connect(): Promise<void> {
    try {
      const result = await this.pool.query('SELECT NOW()');
      this.isConnected = true;
      this.logger.info('Database connected successfully', {
        timestamp: result.rows[0].now,
      });
    } catch (error) {
      this.logger.error('Failed to connect to database', {
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  }

  /**
   * Check if database is connected and healthy.
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.pool.query('SELECT 1');
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get the connection pool.
   *
   * @returns pg Pool instance
   */
  getPool(): Pool {
    return this.pool;
  }

  /**
   * Get a client from the pool.
   *
   * @returns Client that must be released
   */
  async getClient(): Promise<PoolClient> {
    return this.pool.connect();
  }

  /**
   * Execute a query.
   *
   * @param query SQL query string
   * @param values Query parameters
   * @returns Query result
   */
  async query(query: string, values?: any[]): Promise<QueryResult> {
    return this.pool.query(query, values);
  }

  /**
   * Execute a query and return first row.
   *
   * @param query SQL query string
   * @param values Query parameters
   * @returns First row or null
   */
  async queryOne(query: string, values?: any[]): Promise<any | null> {
    const result = await this.pool.query(query, values);
    return result.rows[0] || null;
  }

  /**
   * Execute a query and return all rows.
   *
   * @param query SQL query string
   * @param values Query parameters
   * @returns Array of rows
   */
  async queryAll(query: string, values?: any[]): Promise<any[]> {
    const result = await this.pool.query(query, values);
    return result.rows;
  }

  /**
   * Execute transaction.
   *
   * @param callback Transaction callback that receives client
   * @returns Transaction result
   */
  async transaction<T>(
    callback: (client: PoolClient) => Promise<T>
  ): Promise<T> {
    const client = await this.getClient();

    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Get connection pool statistics.
   *
   * @returns Pool stats
   */
  getStats(): {
    totalCount: number;
    idleCount: number;
    waitingCount: number;
  } {
    return {
      totalCount: this.pool.totalCount,
      idleCount: this.pool.idleCount,
      waitingCount: this.pool.waitingCount,
    };
  }

  /**
   * Gracefully disconnect from database.
   */
  async disconnect(): Promise<void> {
    try {
      await this.pool.end();
      this.isConnected = false;
      this.logger.info('Database disconnected');
    } catch (error) {
      this.logger.error('Error disconnecting database', {
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  }

  /**
   * Check if connected.
   */
  isConnectedStatus(): boolean {
    return this.isConnected;
  }
}

/**
 * Create database instance from environment variables.
 *
 * Reads from:
 * - DATABASE_URL (full connection string)
 * - DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
 *
 * @param logger Logger instance
 * @returns Database instance
 */
export function createDatabaseFromEnv(logger?: Logger): Database {
  const connectionString =
    process.env.DATABASE_URL ||
    (process.env.DB_HOST && process.env.DB_USER && process.env.DB_NAME
      ? `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`
      : undefined);

  const config: DatabaseConfig = {
    connectionString,
    host: process.env.DB_HOST,
    port: process.env.DB_PORT ? parseInt(process.env.DB_PORT, 10) : undefined,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
  };

  return new Database(config, logger);
}
