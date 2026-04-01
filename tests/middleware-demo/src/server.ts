import dotenv from 'dotenv';
import { createApp } from './app';

dotenv.config();

async function main() {
  console.log('\n' + '='.repeat(70));
  console.log('  pyStoOrm Middleware Demo - REST API');
  console.log('='.repeat(70) + '\n');

  try {
    const { app, pool } = await createApp();
    const port = parseInt(process.env.PORT || '3000', 10);

    await app.listen({ port, host: '0.0.0.0' });
    console.log(`\n✓ Server listening on http://localhost:${port}\n`);
    console.log('Available endpoints:');
    console.log('  GET    /health');
    console.log('  GET    /api/customers');
    console.log('  GET    /api/customers/:id');
    console.log('  POST   /api/customers');
    console.log('  PUT    /api/customers/:id');
    console.log('  DELETE /api/customers/:id');
    console.log('  (similar for /api/orders, /api/products)\n');

    // Graceful shutdown
    const signals = ['SIGTERM', 'SIGINT'];
    signals.forEach((sig) => {
      process.on(sig, async () => {
        console.log(`\n⚠ ${sig} received, shutting down gracefully...`);
        await app.close();
        await pool.end();
        console.log('✓ Goodbye!\n');
        process.exit(0);
      });
    });
  } catch (err) {
    console.error('✗ Failed to start server:', err);
    process.exit(1);
  }
}

main();
