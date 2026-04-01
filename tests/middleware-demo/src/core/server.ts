/**
 * Fastify Server Setup
 *
 * Creates and configures Fastify HTTP server with common middleware.
 * Provides hooks for additional plugin registration.
 */

import Fastify, { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import fastifyCors from '@fastify/cors';
import fastifyHelmet from '@fastify/helmet';
import { Logger } from './logger';

export interface ServerConfig {
  port?: number;
  host?: string;
  prefix?: string;
  trustProxy?: boolean | number | string | (string | number)[];
}

/**
 * Create Fastify server with default middleware.
 *
 * Includes:
 * - CORS support
 * - Helmet security headers
 * - Structured logging via pino
 * - Health check endpoint
 *
 * @param logger Logger instance
 * @param config Server configuration
 * @returns Configured Fastify instance
 */
export async function createServer(
  logger: Logger,
  config?: ServerConfig
): Promise<FastifyInstance> {
  const pinoLogger = logger.getPino();

  const server: FastifyInstance = Fastify({
    logger: pinoLogger,
  });

  // Register CORS
  await server.register(fastifyCors, {
    origin: true,
    credentials: true,
  });

  // Register Helmet for security headers
  await server.register(fastifyHelmet, {
    contentSecurityPolicy: false, // Disabled for flexibility
  });

  // Health check endpoint
  server.get('/health', async (_request: FastifyRequest, reply: FastifyReply) => {
    return reply.send({
      status: 'ok',
      timestamp: new Date().toISOString(),
    });
  });

  // Root endpoint
  server.get('/', async (_request: FastifyRequest, reply: FastifyReply) => {
    return reply.send({
      message: 'pyStoOrm Middleware API',
      version: '0.1.0',
    });
  });

  // Global error handler (catches unhandled errors)
  server.setErrorHandler(async (error, request, reply) => {
    logger.error(`Unhandled error: ${error.message}`, {
      statusCode: error.statusCode || 500,
      url: request.url,
      method: request.method,
      stack: error.stack,
    });

    const statusCode = error.statusCode || 500;
    return reply.status(statusCode).send({
      error: error.message || 'Internal Server Error',
      statusCode,
      timestamp: new Date().toISOString(),
    });
  });

  return server;
}

/**
 * Start server and listen on configured port.
 *
 * @param server Fastify instance
 * @param logger Logger instance
 * @param config Server configuration
 */
export async function startServer(
  server: FastifyInstance,
  logger: Logger,
  config?: ServerConfig
): Promise<void> {
  const port = config?.port || Number(process.env.PORT) || 3000;
  const host = config?.host || process.env.HOST || '0.0.0.0';

  try {
    await server.listen({ port, host });
    logger.info(`Server listening`, {
      host,
      port,
      url: `http://${host}:${port}`,
    });
  } catch (error) {
    logger.fatal(
      `Failed to start server: ${error instanceof Error ? error.message : String(error)}`
    );
    throw error;
  }
}

/**
 * Gracefully shutdown server.
 *
 * @param server Fastify instance
 * @param logger Logger instance
 */
export async function shutdownServer(
  server: FastifyInstance,
  logger: Logger
): Promise<void> {
  try {
    logger.info('Shutting down server...');
    await server.close();
    logger.info('Server shutdown complete');
  } catch (error) {
    logger.error(
      `Error during shutdown: ${error instanceof Error ? error.message : String(error)}`
    );
    throw error;
  }
}
