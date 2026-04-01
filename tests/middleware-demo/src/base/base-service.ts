/**
 * Base Service Class
 *
 * Abstract service providing common business logic patterns.
 * All generated services should extend this class.
 */

import {
  IEntity,
  IService,
  IRepository,
  NotFoundError,
  ValidationError,
  PaginationParams,
  PaginatedResponse,
} from './types';

/**
 * Abstract base service for all generated services.
 *
 * Provides:
 * - CRUD operations with validation hooks
 * - Lifecycle hooks for custom logic
 * - Error handling
 *
 * Subclasses should:
 * - Inject concrete repository in constructor
 * - Override hook methods for custom logic
 * - Add domain-specific methods
 *
 * Lifecycle hooks (override in subclass):
 * - validateCreate() - validate before create
 * - validateUpdate() - validate before update
 * - prepareCreate() - transform data before create
 * - prepareUpdate() - transform data before update
 * - afterCreate() - side effects after create
 * - afterUpdate() - side effects after update
 * - beforeDelete() - check before delete
 * - afterDelete() - side effects after delete
 * - enrichEntity() - load related data
 */
export abstract class BaseService<T extends IEntity> implements IService<T> {
  /**
   * Repository instance (injected by subclass).
   */
  protected repository!: IRepository<T>;

  constructor(repository: IRepository<T>) {
    this.repository = repository;
  }

  /**
   * Get entity by ID with enrichment.
   *
   * @param id Entity identifier
   * @returns Enriched entity
   * @throws NotFoundError if not found
   */
  async getById(id: string | number): Promise<T> {
    const entity = await this.repository.findById(id);
    if (!entity) {
      throw new NotFoundError(`Entity with id ${id} not found`);
    }
    return this.enrichEntity(entity);
  }

  /**
   * Get all entities with enrichment.
   *
   * @param limit Optional limit
   * @param offset Optional offset
   * @returns Array of enriched entities
   */
  async getAll(limit?: number, offset?: number): Promise<T[]> {
    const entities = await this.repository.findAll(limit, offset);
    return Promise.all(entities.map((e) => this.enrichEntity(e)));
  }

  /**
   * Get paginated entities.
   *
   * @param params Pagination parameters
   * @returns Paginated response
   */
  async getPaginated(
    params: PaginationParams = {}
  ): Promise<PaginatedResponse<T>> {
    const limit = params.limit || 10;
    const offset = params.offset || (params.page ? (params.page - 1) * limit : 0);

    const [entities, total] = await Promise.all([
      this.repository.findAll(limit, offset),
      this.repository.count(),
    ]);

    const enriched = await Promise.all(
      entities.map((e) => this.enrichEntity(e))
    );

    return {
      data: enriched,
      total,
      limit,
      offset,
      page: params.page,
    };
  }

  /**
   * Create new entity with validation.
   *
   * @param dto Data transfer object
   * @returns Created entity
   * @throws ValidationError if validation fails
   */
  async create(dto: Partial<T>): Promise<T> {
    // Validation hook
    await this.validateCreate(dto);

    // Preparation hook
    const prepared = await this.prepareCreate(dto);

    // Create
    const entity = await this.repository.create(prepared);

    // Post-create hook
    await this.afterCreate(entity);

    return this.enrichEntity(entity);
  }

  /**
   * Update entity with validation.
   *
   * @param id Entity identifier
   * @param dto Partial update data
   * @returns Updated entity or null
   * @throws ValidationError if validation fails
   * @throws NotFoundError if entity not found
   */
  async update(id: string | number, dto: Partial<T>): Promise<T | null> {
    // Check existence
    const existing = await this.repository.findById(id);
    if (!existing) {
      return null;
    }

    // Validation hook
    await this.validateUpdate(id, dto);

    // Preparation hook
    const prepared = await this.prepareUpdate(id, dto);

    // Update
    const entity = await this.repository.update(id, prepared);

    if (!entity) {
      return null;
    }

    // Post-update hook
    await this.afterUpdate(entity);

    return this.enrichEntity(entity);
  }

  /**
   * Delete entity with pre-check.
   *
   * @param id Entity identifier
   * @returns true if deleted, false if not found
   * @throws Error if deletion is prevented in beforeDelete hook
   */
  async delete(id: string | number): Promise<boolean> {
    // Check existence
    const entity = await this.repository.findById(id);
    if (!entity) {
      return false;
    }

    // Pre-delete hook
    await this.beforeDelete(entity);

    // Delete
    const deleted = await this.repository.delete(id);

    if (deleted) {
      // Post-delete hook
      await this.afterDelete(entity);
    }

    return deleted;
  }

  /**
   * Count entities.
   *
   * @param where Optional WHERE clause
   * @returns Count
   */
  async count(where?: string): Promise<number> {
    return this.repository.count(where);
  }

  // ============================================================
  // Lifecycle Hooks - Override in subclass for custom logic
  // ============================================================

  /**
   * Lifecycle Hook: Validate data before create.
   *
   * Override in subclass for validation logic.
   * Throw ValidationError to prevent creation.
   *
   * @param dto Data to validate
   * @throws ValidationError
   */
  protected async validateCreate(dto: Partial<T>): Promise<void> {
    // Override in subclass
  }

  /**
   * Lifecycle Hook: Validate data before update.
   *
   * Override in subclass for validation logic.
   * Throw ValidationError to prevent update.
   *
   * @param id Entity identifier
   * @param dto Data to validate
   * @throws ValidationError
   */
  protected async validateUpdate(id: string | number, dto: Partial<T>): Promise<void> {
    // Override in subclass
  }

  /**
   * Lifecycle Hook: Prepare/transform data before create.
   *
   * Override in subclass to normalize or enrich data.
   * Example: add timestamps, generate IDs, etc.
   *
   * @param dto Raw input data
   * @returns Prepared data
   */
  protected async prepareCreate(dto: Partial<T>): Promise<Partial<T>> {
    return dto;
  }

  /**
   * Lifecycle Hook: Prepare/transform data before update.
   *
   * Override in subclass to normalize or enrich data.
   * Example: update updated_at timestamp, etc.
   *
   * @param id Entity identifier
   * @param dto Raw input data
   * @returns Prepared data
   */
  protected async prepareUpdate(id: string | number, dto: Partial<T>): Promise<Partial<T>> {
    return dto;
  }

  /**
   * Lifecycle Hook: Execute after entity creation.
   *
   * Override in subclass for side effects.
   * Examples: emit events, update cache, send notifications, etc.
   *
   * @param entity Created entity
   */
  protected async afterCreate(entity: T): Promise<void> {
    // Override in subclass
  }

  /**
   * Lifecycle Hook: Execute after entity update.
   *
   * Override in subclass for side effects.
   * Examples: emit events, invalidate cache, send notifications, etc.
   *
   * @param entity Updated entity
   */
  protected async afterUpdate(entity: T): Promise<void> {
    // Override in subclass
  }

  /**
   * Lifecycle Hook: Execute before entity deletion.
   *
   * Override in subclass to prevent deletion or clean up related data.
   * Throw Error to prevent deletion.
   *
   * @param entity Entity to be deleted
   * @throws Error to prevent deletion
   */
  protected async beforeDelete(entity: T): Promise<void> {
    // Override in subclass
  }

  /**
   * Lifecycle Hook: Execute after entity deletion.
   *
   * Override in subclass for side effects.
   * Examples: emit events, cascade delete, send notifications, etc.
   *
   * @param entity Deleted entity
   */
  protected async afterDelete(entity: T): Promise<void> {
    // Override in subclass
  }

  /**
   * Lifecycle Hook: Enrich entity with related data.
   *
   * Override in subclass to load related entities, compute derived fields, etc.
   * Called automatically after loading entities from DB.
   *
   * @param entity Entity to enrich
   * @returns Enriched entity
   */
  protected async enrichEntity(entity: T): Promise<T> {
    // Override in subclass
    return entity;
  }
}
