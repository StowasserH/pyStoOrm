/**
 * Integration Tests - API Endpoints
 *
 * These tests verify the complete request/response cycle.
 * They connect to a real test database.
 *
 * Run with: npm test
 */

import request from 'supertest';
import { Database, Logger } from '@pystoorm/middleware';
import { createApp } from '../../src/app';

describe('API Endpoints', () => {
  let app: any;
  let database: Database;
  let logger: Logger;

  beforeAll(async () => {
    // Override env vars for test environment
    process.env.NODE_ENV = 'test';
    process.env.DB_NAME = process.env.DB_NAME || 'pystoorm_db';

    // Create application
    ({ server: app.server, database, logger } = await createApp());

    // Start listening on ephemeral port
    await new Promise<void>((resolve, reject) => {
      app.server.listen({ port: 0, host: '127.0.0.1' }, (err: any) => {
        if (err) reject(err);
        else resolve();
      });
    });

    logger.info('Test server started');
  });

  afterAll(async () => {
    try {
      await app.server.close();
      await database.disconnect();
      logger.info('Test server closed');
    } catch (error) {
      logger.error('Error closing test server', error as Error);
    }
  });

  describe('Health & Info Endpoints', () => {
    test('GET /health - should return healthy status', async () => {
      const response = await request(app.server).get('/health').expect(200);

      expect(response.body).toHaveProperty('status', 'ok');
      expect(response.body).toHaveProperty('timestamp');
    });

    test('GET / - should return API info', async () => {
      const response = await request(app.server).get('/').expect(200);

      expect(response.body).toHaveProperty('message');
      expect(response.body.message).toContain('pyStoOrm');
    });

    test('GET /api - should return API information', async () => {
      const response = await request(app.server).get('/api').expect(200);

      expect(response.body).toHaveProperty('api');
      expect(response.body).toHaveProperty('version');
      expect(response.body).toHaveProperty('endpoints');
    });
  });

  describe('Database Stats', () => {
    test('GET /api/stats - should return database statistics', async () => {
      const response = await request(app.server)
        .get('/api/stats')
        .expect(200);

      expect(response.body).toHaveProperty('status', 'connected');
      expect(response.body).toHaveProperty('tables');
      expect(Array.isArray(response.body.tables)).toBe(true);
      expect(response.body).toHaveProperty('poolStats');
    });

    test('/api/stats - database should have expected tables', async () => {
      const response = await request(app.server).get('/api/stats').expect(200);

      const tables = response.body.tables as string[];
      const expectedTables = ['customers', 'orders', 'products'];

      for (const table of expectedTables) {
        expect(tables).toContain(table);
      }
    });
  });

  describe('Error Handling', () => {
    test('404 - should return not found for unknown route', async () => {
      const response = await request(app.server)
        .get('/api/nonexistent')
        .expect(404);

      expect(response.body).toHaveProperty('error');
    });

    test('405 - should return method not allowed for POST on GET-only endpoint', async () => {
      const response = await request(app.server)
        .post('/health')
        .expect(405);

      expect(response.status).toBe(405);
    });
  });

  /**
   * Example tests for generated endpoints (uncomment after generation)
   *
   * describe('Customers API', () => {
   *   test('GET /api/customers - should return all customers', async () => {
   *     const response = await request(app.server)
   *       .get('/api/customers')
   *       .expect(200);
   *
   *     expect(Array.isArray(response.body)).toBe(true);
   *     if (response.body.length > 0) {
   *       expect(response.body[0]).toHaveProperty('customerName');
   *     }
   *   });
   *
   *   test('GET /api/customers/:id - should return customer by id', async () => {
   *     const response = await request(app.server)
   *       .get('/api/customers/103')
   *       .expect(200);
   *
   *     expect(response.body).toHaveProperty('customerName');
   *   });
   *
   *   test('GET /api/customers/:id - should return 404 for non-existent id', async () => {
   *     const response = await request(app.server)
   *       .get('/api/customers/99999')
   *       .expect(404);
   *
   *     expect(response.body).toHaveProperty('error');
   *   });
   *
   *   test('POST /api/customers - should create new customer', async () => {
   *     const newCustomer = {
   *       customerName: 'Test Company',
   *       contactLastName: 'Doe',
   *       contactFirstName: 'John',
   *       phone: '555-1234',
   *       addressLine1: '123 Main St',
   *       city: 'Test City',
   *       country: 'USA',
   *       creditLimit: 50000,
   *     };
   *
   *     const response = await request(app.server)
   *       .post('/api/customers')
   *       .send(newCustomer)
   *       .expect(201);
   *
   *     expect(response.body).toHaveProperty('customerNumber');
   *     expect(response.body.customerName).toBe(newCustomer.customerName);
   *   });
   * });
   */
});
