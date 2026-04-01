import { FastifyInstance } from 'fastify';
import { Pool } from 'pg';

// Import generated repositories, services, and controllers
import { CustomersRepository } from '../generated/repositories/customers.repository';
import { CustomersService } from '../generated/services/customers.service';
import { CustomersController } from '../generated/controllers/customers.controller';

import { OrdersRepository } from '../generated/repositories/orders.repository';
import { OrdersService } from '../generated/services/orders.service';
import { OrdersController } from '../generated/controllers/orders.controller';

import { ProductsRepository } from '../generated/repositories/products.repository';
import { ProductsService } from '../generated/services/products.service';
import { ProductsController } from '../generated/controllers/products.controller';

export async function registerRoutes(app: FastifyInstance, pool: Pool) {
  // ============================================================
  // CUSTOMERS ROUTES
  // ============================================================
  const customersRepo = new CustomersRepository(pool);
  const customersService = new CustomersService(customersRepo);
  const customersController = new CustomersController(customersService);

  app.get('/api/customers', (req, res) => customersController.getAll(req, res));
  app.get('/api/customers/:id', (req, res) => customersController.getById(req, res));
  app.post('/api/customers', (req, res) => customersController.create(req, res));
  app.put('/api/customers/:id', (req, res) => customersController.update(req, res));
  app.delete('/api/customers/:id', (req, res) => customersController.delete(req, res));

  // ============================================================
  // ORDERS ROUTES
  // ============================================================
  const ordersRepo = new OrdersRepository(pool);
  const ordersService = new OrdersService(ordersRepo);
  const ordersController = new OrdersController(ordersService);

  app.get('/api/orders', (req, res) => ordersController.getAll(req, res));
  app.get('/api/orders/:id', (req, res) => ordersController.getById(req, res));
  app.post('/api/orders', (req, res) => ordersController.create(req, res));
  app.put('/api/orders/:id', (req, res) => ordersController.update(req, res));
  app.delete('/api/orders/:id', (req, res) => ordersController.delete(req, res));

  // ============================================================
  // PRODUCTS ROUTES
  // ============================================================
  const productsRepo = new ProductsRepository(pool);
  const productsService = new ProductsService(productsRepo);
  const productsController = new ProductsController(productsService);

  app.get('/api/products', (req, res) => productsController.getAll(req, res));
  app.get('/api/products/:id', (req, res) => productsController.getById(req, res));
  app.post('/api/products', (req, res) => productsController.create(req, res));
  app.put('/api/products/:id', (req, res) => productsController.update(req, res));
  app.delete('/api/products/:id', (req, res) => productsController.delete(req, res));

  console.log('✓ Routes registered');
}
