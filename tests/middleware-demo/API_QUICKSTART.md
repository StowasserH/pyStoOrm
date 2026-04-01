# pyStoOrm Middleware Demo - API Quick Start

## Status

✅ **Fully Generated & Compilable**
- 35 TypeScript files successfully generated
- All code compiles without errors (npm run build ✓)
- PostgreSQL database running with sample data
- REST API fully scaffolded and ready to extend

## Setup Steps

### 1. Verify PostgreSQL is Running
```bash
sudo docker-compose up -d
# Verify:
docker ps | grep postgres
```

✓ PostgreSQL on `localhost:5432`
✓ Database: `pystoorm_db`
✓ User: `pystoorm_user`
✓ Password: `pystoorm_password`

### 2. Generate TypeScript Code (Already Done)
```bash
npm run generate
# Generates src/generated/ with Models, Repositories, Services, DTOs, Controllers
```

### 3. Compile TypeScript
```bash
npm run build
# Output: dist/
```

### 4. Start the API Server
```bash
npm run start
# Listens on http://localhost:3000
```

Expected output:
```
======================================================================
  pyStoOrm Middleware Demo - REST API
======================================================================

✓ Database connected
✓ Server listening on http://localhost:3000

Available endpoints:
  GET    /health
  GET    /api/customers
  GET    /api/customers/:id
  POST   /api/customers
  PUT    /api/customers/:id
  DELETE /api/customers/:id
  (similar for /api/orders, /api/products)
```

## Test the API

### 1. Health Check
```bash
curl http://localhost:3000/health
```

### 2. Get All Customers
```bash
curl http://localhost:3000/api/customers | jq .
```

Sample response:
```json
[
  {
    "customernumber": 103,
    "customername": "Atelier graphique",
    "contactlastname": "Schmitt",
    "contactfirstname": "Carine",
    "phone": "40.32.2555",
    "addressline1": "54 rue Royale",
    ...
  }
]
```

### 3. Get Customer by ID
```bash
curl http://localhost:3000/api/customers/103 | jq .
```

### 4. Create New Customer
```bash
curl -X POST http://localhost:3000/api/customers \
  -H "Content-Type: application/json" \
  -d '{
    "customername": "Tech Corp",
    "contactlastname": "Doe",
    "contactfirstname": "John",
    "phone": "555-1234",
    "addressline1": "123 Tech St",
    "city": "San Francisco",
    "state": "CA",
    "country": "USA",
    "creditlimit": 25000
  }' | jq .
```

### 5. Update Customer
```bash
curl -X PUT http://localhost:3000/api/customers/103 \
  -H "Content-Type: application/json" \
  -d '{"creditlimit": 150000}' | jq .
```

### 6. Delete Customer
```bash
curl -X DELETE http://localhost:3000/api/customers/999
```

### 7. Get Orders
```bash
curl http://localhost:3000/api/orders | jq . | head -50
```

### 8. Get Products
```bash
curl http://localhost:3000/api/products | jq . | head -50
```

## Run All Tests
```bash
bash test-api.sh
```

## Project Structure

### Generated Code (`src/generated/`)
```
├── models/              (7 models)
│   ├── customers.model.ts
│   ├── orders.model.ts
│   └── products.model.ts
├── repositories/        (7 repositories)
│   ├── customers.repository.ts
│   ├── orders.repository.ts
│   └── products.repository.ts
├── services/           (7 services)
│   ├── customers.service.ts
│   ├── orders.service.ts
│   └── products.service.ts
├── dto/                (7 DTOs)
│   ├── customers.dto.ts
│   ├── orders.dto.ts
│   └── products.dto.ts
└── controllers/        (7 controllers)
    ├── customers.controller.ts
    ├── orders.controller.ts
    └── products.controller.ts
```

### Custom Logic (`src/`)
```
├── app.ts              # Fastify app setup
├── server.ts           # Entry point
└── routes/
    └── index.ts        # Route registration
```

## 7 Tables with Full API

| Table | Columns | Primary Key | REST Endpoints |
|-------|---------|-------------|---|
| customers | 13 | customerNumber | GET, POST, PUT, DELETE |
| employees | 8 | employeeNumber | GET, POST, PUT, DELETE |
| offices | 9 | officeCode | GET, POST, PUT, DELETE |
| orders | 7 | orderNumber | GET, POST, PUT, DELETE |
| orderdetails | 5 | (orderNumber, productCode) | GET, POST, PUT, DELETE |
| products | 9 | productCode | GET, POST, PUT, DELETE |
| productlines | 4 | productLine | GET, POST, PUT, DELETE |

## Sample Data

Database includes pre-populated data:
- 6 offices (San Francisco, Boston, NYC, Paris, Tokyo, Sydney)
- 8 employees
- 6 product lines
- 7 sample products
- 6 customers
- 5 orders
- 7 order details

## Next Steps

### Extend with Custom Business Logic
Edit `src/routes/index.ts` to add:
- Custom validation
- Authorization checks
- Business logic hooks
- Custom finders/queries

### Example: Add Custom Customer Service
```typescript
// src/custom-logic/customer-service.ts
export class CustomCustomerService extends CustomersService {
  async getVIPCustomers(): Promise<Customers[]> {
    // Custom logic: find high-value customers
    const customers = await this.repository.findAll();
    return customers.filter(c => c.creditlimit > 100000);
  }
}
```

### Error Handling
The API includes:
- 400 Bad Request (validation)
- 404 Not Found (missing entity)
- 500 Internal Server Error (unexpected)

### Database Queries
All repositories support:
- `findById(id)` - Get by primary key
- `findAll(limit?, offset?)` - Get all with pagination
- `create(data)` - Create new record
- `update(id, data)` - Update record
- `delete(id)` - Delete record
- Custom methods - Add in repository classes

## Architecture

```
Client (curl/Postman/browser)
    ↓
Controllers (HTTP handlers)
    ↓
Services (Business Logic)
    ↓
Repositories (Database Access)
    ↓
PostgreSQL
```

Each layer is **type-safe** and **generated from schema**.

## Troubleshooting

### "Cannot find module" errors
- Run `npm install` first
- Ensure PostgreSQL is running: `sudo docker-compose up -d`

### Database connection failed
- Check PostgreSQL: `sudo docker-compose logs postgres`
- Verify credentials in `.env`
- Database: `pystoorm_db`

### Port 3000 already in use
```bash
lsof -i :3000  # Find process
kill -9 <PID>  # Kill it
```

### Port 5432 already in use (PostgreSQL)
```bash
sudo docker-compose down  # Stop containers
sudo docker-compose up -d # Restart
```
