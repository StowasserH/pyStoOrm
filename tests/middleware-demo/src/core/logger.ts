/**
 * Logger Service using pino
 *
 * Provides structured logging with levels and pretty-printing.
 * Configured via environment variables.
 */

import pino, { Logger as PinoLogger } from 'pino';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'fatal';

export interface LoggerConfig {
  level?: LogLevel;
  pretty?: boolean;
  prettyOptions?: Record<string, any>;
}

/**
 * Logger Service
 *
 * Wrapper around pino logger.
 */
export class Logger {
  private pinoLogger: PinoLogger;

  constructor(config?: LoggerConfig) {
    const level = config?.level || (process.env.LOG_LEVEL as LogLevel) || 'info';
    const pretty = config?.pretty ?? process.env.NODE_ENV !== 'production';

    const transport = pretty
      ? {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: 'SYS:standard',
            ignore: 'pid,hostname',
            ...config?.prettyOptions,
          },
        }
      : undefined;

    this.pinoLogger = pino(
      {
        level,
        timestamp: pino.stdTimeFunctions.isoTime,
      },
      transport ? pino.transport(transport) : undefined
    );
  }

  /**
   * Get underlying pino logger for Fastify integration.
   */
  getPino(): PinoLogger {
    return this.pinoLogger;
  }

  /**
   * Log debug message.
   */
  debug(message: string, data?: Record<string, any>): void {
    this.pinoLogger.debug(data, message);
  }

  /**
   * Log info message.
   */
  info(message: string, data?: Record<string, any>): void {
    this.pinoLogger.info(data, message);
  }

  /**
   * Log warning message.
   */
  warn(message: string, data?: Record<string, any>): void {
    this.pinoLogger.warn(data, message);
  }

  /**
   * Log error message.
   */
  error(message: string, data?: Record<string, any> | Error): void {
    if (data instanceof Error) {
      this.pinoLogger.error({ err: data }, message);
    } else {
      this.pinoLogger.error(data, message);
    }
  }

  /**
   * Log fatal message (application will exit).
   */
  fatal(message: string, data?: Record<string, any> | Error): void {
    if (data instanceof Error) {
      this.pinoLogger.fatal({ err: data }, message);
    } else {
      this.pinoLogger.fatal(data, message);
    }
  }

  /**
   * Create child logger with merged context.
   *
   * @param context Context data to merge with all messages
   * @returns Child logger
   */
  child(context: Record<string, any>): Logger {
    const logger = new Logger();
    logger.pinoLogger = this.pinoLogger.child(context);
    return logger;
  }
}
