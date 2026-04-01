import Fastify, { FastifyInstance } from 'fastify';
import cors from '@fastify/cors';
import helmet from '@fastify/helmet';
import { Pool } from 'pg';
import { registerRoutes } from './routes';

export async function createApp(): Promise<{ app: FastifyInstance; pool: Pool }> {
  // Create Fastify instance
  const app = Fastify({
    logger: true,
  });

  // Register security middleware
  await app.register(helmet);
  await app.register(cors, { origin: '*' });

  // Create PostgreSQL connection pool
  const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432', 10),
    database: process.env.DB_NAME || 'pystoorm_db',
    user: process.env.DB_USER || 'pystoorm_user',
    password: process.env.DB_PASSWORD || 'pystoorm_password',
  });

  // Test database connection
  try {
    const result = await pool.query('SELECT NOW()');
    console.log('✓ Database connected:', result.rows[0]);
  } catch (err) {
    console.error('✗ Database connection failed:', err);
    throw err;
  }

  // Health check endpoint
  app.get('/health', async () => ({
    status: 'ok',
    timestamp: new Date().toISOString(),
  }));

  // Register routes
  await registerRoutes(app, pool);

  return { app, pool };
}
