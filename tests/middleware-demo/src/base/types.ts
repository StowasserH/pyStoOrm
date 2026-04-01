/**
 * Shared TypeScript Type Definitions
 *
 * Common types used throughout the middleware.
 */

/**
 * Base entity type - all models should extend this.
 */
export interface IEntity {
  getId(): string | number | null;
  isDirty: boolean;
  modifiedColumns: Record<string, any>;
  resetDirty(): void;
  toObject(): Record<string, any>;
  equals(other: any): boolean;
}

/**
 * Repository interface - all repositories should implement this.
 */
export interface IRepository<T extends IEntity> {
  findById(id: string | number): Promise<T | null>;
  findAll(limit?: number, offset?: number): Promise<T[]>;
  create(data: Partial<T>): Promise<T>;
  update(id: string | number, data: Partial<T>): Promise<T | null>;
  delete(id: string | number): Promise<boolean>;
  count(where?: string): Promise<number>;
}

/**
 * Service interface - all services should implement this.
 */
export interface IService<T extends IEntity> {
  getById(id: string | number): Promise<T>;
  getAll(limit?: number, offset?: number): Promise<T[]>;
  create(dto: Partial<T>): Promise<T>;
  update(id: string | number, dto: Partial<T>): Promise<T | null>;
  delete(id: string | number): Promise<boolean>;
  count(where?: string): Promise<number>;
}

/**
 * Error types
 */
export class NotFoundError extends Error {
  name = 'NotFoundError';
  statusCode = 404;

  constructor(message: string) {
    super(message);
  }
}

export class ValidationError extends Error {
  name = 'ValidationError';
  statusCode = 422;

  constructor(message: string) {
    super(message);
  }
}

export class ConflictError extends Error {
  name = 'ConflictError';
  statusCode = 409;

  constructor(message: string) {
    super(message);
  }
}

export class UnauthorizedError extends Error {
  name = 'UnauthorizedError';
  statusCode = 401;

  constructor(message: string = 'Unauthorized') {
    super(message);
  }
}

export class ForbiddenError extends Error {
  name = 'ForbiddenError';
  statusCode = 403;

  constructor(message: string = 'Forbidden') {
    super(message);
  }
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  limit?: number;
  offset?: number;
  page?: number;
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit?: number;
  offset?: number;
  page?: number;
}

/**
 * API response wrapper
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}
