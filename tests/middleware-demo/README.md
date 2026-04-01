# pyStoOrm Middleware Demo

Complete working example of the pyStoOrm Middleware framework with REST API.

This demo shows:
- 🗄️ PostgreSQL database with Docker
- 🔧 Code generation from database schema
- 📝 Type-safe models, repositories, and services
- 🚀 REST API with Fastify
- ✅ Integration tests with Jest
- 📚 Full TypeScript setup

## Quick Start

### 1. Start PostgreSQL Database

```bash
docker-compose up -d
```

This starts:
- PostgreSQL 15 on `localhost:5432` (pystoorm_db)
- pgAdmin on `http://localhost:5050` (admin@example.com / admin)

Wait for database to be ready:
```bash
docker-compose logs postgres | grep "database system is ready"
```

### 2. Generate TypeScript Code

Generate models, repositories, services, DTOs, and controllers from the database schema:

```bash
npm run generate
```

This creates:
- `src/generated/models/` - Entity classes with dirty tracking
- `src/generated/repositories/` - Data access objects
- `src/generated/services/` - Business logic layer
- `src/generated/dto/` - Zod validation schemas
- `src/generated/controllers/` - Fastify route handlers

### 3. Install Dependencies

```bash
npm install
```

### 4. Start Development Server

```bash
npm run dev
```

Server runs on http://localhost:3000

### 5. Test the API

```bash
# Health check
curl http://localhost:3000/health

# API info
curl http://localhost:3000/api

# Database statistics
curl http://localhost:3000/api/stats
```

### 6. Run Tests

```bash
npm test
```

## Project Structure

```
.
├── docker-compose.yml          # PostgreSQL + pgAdmin
├── init.sql                    # Database schema (Classic Models)
├── project.yml                 # pyStoOrm configuration
├── .env                        # Environment variables
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
│
├── src/
│   ├── app.ts                  # Application setup
│   ├── server.ts               # Server entry point
│   ├── routes/
│   │   └── index.ts            # Route registration
│   │
│   ├── custom-logic/           # Custom business logic (extend generated code)
│   │   └── customers.service.example.ts
│   │
│   └── generated/              # AUTO-GENERATED (do not edit)
│       ├── models/
│       │   ├── customers.model.ts
│       │   ├── orders.model.ts
│       │   ├── products.model.ts
│       │   └── ...
│       ├── repositories/
│       ├── services/
│       ├── dto/
│       └── controllers/
│
└── tests/
    └── integration/
        └── api.test.ts         # API integration tests
```

## Database Schema

The demo uses the classic "Classicmodels" sample database with:

- **customers** - Customer records
- **orders** - Sales orders
- **orderdetails** - Order line items
- **products** - Product catalog
- **productlines** - Product categories
- **employees** - Sales staff
- **offices** - Office locations

Foreign keys and indexes are pre-configured.

## Generated Code Structure

After running `npm run generate`, you'll have:

### Models (entities with properties)
```typescript
export class Customers extends BaseModel {
  get customerName(): string { ... }
  set customerName(value: string) { ... }
  get isDirty(): boolean { ... }
  get modifiedColumns(): Record<string, any> { ... }
  // ... one property per column
}
```

### Repositories (data access)
```typescript
export class CustomersRepository extends BaseRepository<Customers> {
  async findById(id: number): Promise<Customers | null> { ... }
  async findAll(limit?, offset?): Promise<Customers[]> { ... }
  async create(data): Promise<Customers> { ... }
  async update(id, data): Promise<Customers | null> { ... }
  async delete(id): Promise<boolean> { ... }
}
```

### Services (business logic with hooks)
```typescript
export class CustomersService extends BaseService<Customers> {
  async getById(id: number): Promise<Customers> { ... }
  async getAll(limit?, offset?): Promise<Customers[]> { ... }
  async create(dto): Promise<Customers> { ... }

  // Lifecycle hooks to override
  protected async validateCreate(dto) { ... }
  protected async afterCreate(entity) { ... }
  protected async enrichEntity(entity) { ... }
}
```

### DTOs (validation schemas)
```typescript
export const CreateCustomersSchema = z.object({
  customerName: z.string(),
  phone: z.string(),
  country: z.string(),
  // ... all columns
});

export type CreateCustomers = z.infer<typeof CreateCustomersSchema>;
```

### Controllers (HTTP handlers)
```typescript
export class CustomersController {
  async getAll(request: FastifyRequest, reply: FastifyReply) { ... }
  async getById(request: FastifyRequest, reply: FastifyReply) { ... }
  async create(request: FastifyRequest, reply: FastifyReply) { ... }
  async update(request: FastifyRequest, reply: FastifyReply) { ... }
  async delete(request: FastifyRequest, reply: FastifyReply) { ... }
}
```

## Extending Generated Code

### 1. Custom Services

Create `src/custom-logic/customers.service.ts`:

```typescript
import { CustomersService as GeneratedService } from '../generated/services/customers.service';
import { CustomersRepository } from '../generated/repositories/customers.repository';
import { Customers } from '../generated/models/customers.model';
import { ValidationError } from '@pystoorm/middleware';

export class CustomersService extends GeneratedService {
  constructor(repository: CustomersRepository) {
    super(repository);
  }

  // Add custom methods
  async getVIPCustomers(): Promise<Customers[]> {
    return this.repository.execute(
      'SELECT * FROM customers WHERE creditLimit > $1',
      [50000]
    );
  }

  // Override validation
  protected async validateCreate(dto: Partial<Customers>): Promise<void> {
    if (!dto.customerName) {
      throw new ValidationError('Customer name is required');
    }
  }

  // Add side effects
  protected async afterCreate(entity: Customers): Promise<void> {
    console.log(`Created customer: ${entity.customerName}`);
  }
}
```

### 2. Register Routes

Update `src/routes/index.ts`:

```typescript
import { CustomersRepository } from '../generated/repositories/customers.repository';
import { CustomersService } from '../custom-logic/customers.service';
import { CustomersController } from '../generated/controllers/customers.controller';

export async function registerRoutes(server, database) {
  const pool = database.getPool();

  // Dependency injection
  const repo = new CustomersRepository(pool);
  const service = new CustomersService(repo);
  const controller = new CustomersController(service);

  // Routes
  server.get('/api/customers', (req, res) => controller.getAll(req, res));
  server.get('/api/customers/:id', (req, res) => controller.getById(req, res));
  server.post('/api/customers', (req, res) => controller.create(req, res));
  server.patch('/api/customers/:id', (req, res) => controller.update(req, res));
  server.delete('/api/customers/:id', (req, res) => controller.delete(req, res));
}
```

## Scripts

```bash
# Development
npm run dev              # Start dev server with hot reload
npm run build           # Compile TypeScript
npm run watch           # Watch and recompile

# Testing
npm test                # Run tests once
npm run test:watch      # Run tests in watch mode

# Code quality
npm run type-check      # Type check without compiling
npm run lint            # Run ESLint

# Generation
npm run generate        # Run pyStoOrm code generation
npm run clean           # Remove dist/ and generated files

# Production
npm start               # Run compiled server
```

## Environment Variables

See `.env` for all available options:

```
NODE_ENV=development
PORT=3000
HOST=0.0.0.0
LOG_LEVEL=debug

DB_HOST=localhost
DB_PORT=5432
DB_NAME=pystoorm_db
DB_USER=pystoorm_user
DB_PASSWORD=pystoorm_password
```

## API Endpoints (Auto-Generated)

After `npm run generate`, the following endpoints are available:

### Customers
```
GET    /api/customers          # List all
GET    /api/customers/:id      # Get one
POST   /api/customers          # Create
PATCH  /api/customers/:id      # Update
DELETE /api/customers/:id      # Delete
```

Similar endpoints are generated for all tables.

### Built-in Endpoints
```
GET    /                       # API info
GET    /health                 # Health check
GET    /api                    # API documentation
GET    /api/stats              # Database statistics
```

## Cleanup

To stop and remove all Docker containers/volumes:

```bash
docker-compose down -v
```

## Troubleshooting

### Database connection refused
- Check PostgreSQL is running: `docker-compose ps`
- Verify environment variables in `.env`
- Check logs: `docker-compose logs postgres`

### Generation errors
- Ensure pyStoOrm is installed: `pip install pyStoOrm`
- Check `project.yml` configuration
- Verify database connection string in config

### Tests fail
- Ensure database is running and initialized
- Check environment variables: `cat .env`
- Run single test: `npm test -- api.test.ts`

## Next Steps

1. **Generate code**: `npm run generate`
2. **Customize services**: Update `src/custom-logic/`
3. **Register routes**: Add to `src/routes/index.ts`
4. **Extend tests**: Add to `tests/integration/`
5. **Deploy**: Build and run with Docker or your platform

## Documentation

- [pyStoOrm Middleware Framework](../../pystoorm-middleware/README.md)
- [Architecture Overview](../../pystoorm-middleware/ARCHITECTURE.md)
- [pyStoOrm Main Project](../../README.md)

## License

MIT

---

Built with ❤️ using pyStoOrm Middleware
