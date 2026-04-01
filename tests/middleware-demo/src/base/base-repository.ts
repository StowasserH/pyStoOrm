/**
 * Base Repository Class
 *
 * Abstract repository providing common CRUD operations.
 * All generated repositories should extend this class.
 */

import { Pool, QueryResult, PoolClient } from 'pg';
import { IEntity, IRepository, NotFoundError } from './types';

/**
 * Abstract base repository for all generated repositories.
 *
 * Provides:
 * - CRUD operations (Create, Read, Update, Delete)
 * - Transaction support
 * - Custom query execution
 *
 * Subclasses should:
 * - Set tableName and primaryKey
 * - Implement _fromRow() to convert DB rows to entities
 * - Add domain-specific finder methods
 */
export abstract class BaseRepository<T extends IEntity> implements IRepository<T> {
  /**
   * Table name in database (set by subclass)
   */
  protected tableName: string = '';

  /**
   * Primary key column name (set by subclass)
   */
  protected primaryKey: string = 'id';

  /**
   * PostgreSQL connection pool
   */
  protected pool: Pool;

  constructor(pool: Pool) {
    this.pool = pool;
  }

  /**
   * Convert database row to entity instance.
   *
   * Must be implemented by subclass.
   *
   * @param row Database row
   * @returns Entity instance
   */
  protected abstract _fromRow(row: Record<string, any>): T;

  /**
   * Find entity by primary key.
   *
   * @param id Primary key value
   * @returns Entity or null if not found
   */
  async findById(id: string | number): Promise<T | null> {
    const query = `SELECT * FROM "${this.tableName}" WHERE "${this.primaryKey}" = $1`;
    const result: QueryResult = await this.pool.query(query, [id]);
    return result.rows.length > 0 ? this._fromRow(result.rows[0]) : null;
  }

  /**
   * Find all entities.
   *
   * @param limit Optional limit
   * @param offset Optional offset
   * @returns Array of entities
   */
  async findAll(limit?: number, offset?: number): Promise<T[]> {
    let query = `SELECT * FROM "${this.tableName}"`;
    const params: any[] = [];

    if (limit !== undefined) {
      params.push(limit);
      query += ` LIMIT $${params.length}`;
    }

    if (offset !== undefined) {
      params.push(offset);
      query += ` OFFSET $${params.length}`;
    }

    const result: QueryResult = await this.pool.query(query, params);
    return result.rows.map((row) => this._fromRow(row));
  }

  /**
   * Create a new entity.
   *
   * @param data Object with column values
   * @returns Created entity with ID
   */
  async create(data: Partial<T>): Promise<T> {
    const columns = Object.keys(data);
    const values = Object.values(data);

    if (columns.length === 0) {
      throw new Error('Cannot create with empty data');
    }

    const placeholders = values.map((_, i) => `$${i + 1}`).join(', ');
    const columnNames = columns.map((col) => `"${col}"`).join(', ');

    const query = `
      INSERT INTO "${this.tableName}" (${columnNames})
      VALUES (${placeholders})
      RETURNING *
    `;

    const result: QueryResult = await this.pool.query(query, values);
    return this._fromRow(result.rows[0]);
  }

  /**
   * Update an entity.
   *
   * @param id Primary key value
   * @param data Object with updated values
   * @returns Updated entity or null if not found
   */
  async update(id: string | number, data: Partial<T>): Promise<T | null> {
    const columns = Object.keys(data);

    if (columns.length === 0) {
      // No updates, just return the entity
      return this.findById(id);
    }

    const values = Object.values(data);
    const setClauses = columns
      .map((col, i) => `"${col}" = $${i + 1}`)
      .join(', ');
    values.push(id);

    const query = `
      UPDATE "${this.tableName}"
      SET ${setClauses}
      WHERE "${this.primaryKey}" = $${values.length}
      RETURNING *
    `;

    const result: QueryResult = await this.pool.query(query, values);
    return result.rows.length > 0 ? this._fromRow(result.rows[0]) : null;
  }

  /**
   * Delete an entity.
   *
   * @param id Primary key value
   * @returns true if deleted, false if not found
   */
  async delete(id: string | number): Promise<boolean> {
    const query = `DELETE FROM "${this.tableName}" WHERE "${this.primaryKey}" = $1`;
    const result: QueryResult = await this.pool.query(query, [id]);
    return result.rowCount !== null && result.rowCount > 0;
  }

  /**
   * Count entities matching criteria.
   *
   * @param where Optional WHERE clause (without WHERE keyword)
   * @returns Count
   */
  async count(where?: string): Promise<number> {
    let query = `SELECT COUNT(*) as count FROM "${this.tableName}"`;
    const params: any[] = [];

    if (where) {
      query += ` WHERE ${where}`;
    }

    const result: QueryResult = await this.pool.query(query, params);
    return parseInt(result.rows[0]?.count || 0, 10);
  }

  /**
   * Check if entity exists.
   *
   * @param id Primary key value
   * @returns true if exists
   */
  async exists(id: string | number): Promise<boolean> {
    const entity = await this.findById(id);
    return entity !== null;
  }

  /**
   * Execute custom query and map results to entities.
   *
   * Override in subclass for type safety.
   *
   * @param query SQL query
   * @param params Query parameters
   * @returns Array of entities
   */
  protected async execute(query: string, params: any[] = []): Promise<T[]> {
    const result: QueryResult = await this.pool.query(query, params);
    return result.rows.map((row) => this._fromRow(row));
  }

  /**
   * Execute raw query (returns plain objects).
   *
   * @param query SQL query
   * @param params Query parameters
   * @returns Array of plain objects
   */
  protected async executeRaw(query: string, params: any[] = []): Promise<any[]> {
    const result: QueryResult = await this.pool.query(query, params);
    return result.rows;
  }

  /**
   * Execute query returning single value.
   *
   * @param query SQL query
   * @param params Query parameters
   * @returns Single value or null
   */
  protected async executeScalar(query: string, params: any[] = []): Promise<any> {
    const result: QueryResult = await this.pool.query(query, params);
    if (result.rows.length === 0) {
      return null;
    }
    const row = result.rows[0];
    // Return first column value
    return Object.values(row)[0] || null;
  }

  /**
   * Begin transaction.
   *
   * @returns Client for transaction
   */
  protected async beginTransaction(): Promise<PoolClient> {
    const client = await this.pool.connect();
    await client.query('BEGIN');
    return client;
  }

  /**
   * Commit transaction.
   *
   * @param client Transaction client
   */
  protected async commit(client: PoolClient): Promise<void> {
    try {
      await client.query('COMMIT');
    } finally {
      client.release();
    }
  }

  /**
   * Rollback transaction.
   *
   * @param client Transaction client
   */
  protected async rollback(client: PoolClient): Promise<void> {
    try {
      await client.query('ROLLBACK');
    } finally {
      client.release();
    }
  }

  /**
   * Execute transaction callback.
   *
   * @param callback Callback function that receives client
   * @returns Result from callback
   */
  protected async transaction<R>(
    callback: (client: PoolClient) => Promise<R>
  ): Promise<R> {
    const client = await this.beginTransaction();
    try {
      const result = await callback(client);
      await this.commit(client);
      return result;
    } catch (error) {
      await this.rollback(client);
      throw error;
    }
  }
}
