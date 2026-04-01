# pyStoOrm Middleware Demo - Architekturbeschreibung

## 1. Executive Summary

Das **pyStoOrm Middleware Demo** ist ein vollständig generiertes, modernes REST API System, das zeigt, wie **Datenbankschema-First Development** moderne Web-APIs vereinfacht.

**Kernprinzipien:**
- 🗄️ **Schema-First**: API wird aus PostgreSQL-Schema generiert
- 🔄 **Type-Safe**: Vollständig TypeScript mit strikter Typ-Prüfung
- 🏗️ **Layered Architecture**: Klare Trennung von HTTP, Business Logic, und Database Access
- 🚀 **Production-Ready**: Fehlerbehandlung, Validierung, Logging inklusive
- 📦 **Zero-Boilerplate**: Entweder generiert oder minimal geschrieben

---

## 2. System-Übersicht

### 2.1 High-Level Architektur

```
┌────────────────────────────────────────────────────────────┐
│                     Client Layer                           │
│           (Browser, Postman, Mobile App, etc.)             │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP/JSON (REST)
                     ↓
┌────────────────────────────────────────────────────────────┐
│              Presentation Layer (Controllers)               │
│                  (FastifyController)                        │
│  ├─ HTTP Request Handling                                 │
│  ├─ Request Validation                                    │
│  ├─ Response Formatting                                   │
│  └─ Status Code Management                                │
└────────────────────┬─────────────────────────────────────┘
                     │ TypeScript Objects
                     ↓
┌────────────────────────────────────────────────────────────┐
│             Business Logic Layer (Services)                 │
│                   (CustomersService)                        │
│  ├─ Validation Rules                                      │
│  ├─ Business Rules                                        │
│  ├─ Entity Enrichment                                     │
│  └─ Cross-Cutting Concerns                                │
└────────────────────┬─────────────────────────────────────┘
                     │ CRUD Operations
                     ↓
┌────────────────────────────────────────────────────────────┐
│           Data Access Layer (Repositories)                  │
│              (CustomersRepository)                          │
│  ├─ Query Building                                        │
│  ├─ Parameter Binding                                     │
│  ├─ Result Mapping                                        │
│  └─ Transaction Management                                │
└────────────────────┬─────────────────────────────────────┘
                     │ SQL Queries
                     ↓
┌────────────────────────────────────────────────────────────┐
│              Entity Layer (Models)                          │
│               (Customers Model)                            │
│  ├─ Column Definitions                                    │
│  ├─ Type Hints                                            │
│  ├─ Metadata                                              │
│  └─ Helper Methods                                        │
└────────────────────┬─────────────────────────────────────┘
                     │ Database Rows
                     ↓
┌────────────────────────────────────────────────────────────┐
│              Database Layer (PostgreSQL)                    │
│          (classicmodels Database - Docker)                 │
│  ├─ 7 Tables with 49 Columns                              │
│  ├─ Foreign Key Relationships                             │
│  ├─ Sample Data (50+ rows)                                │
│  └─ Indexes for Performance                               │
└────────────────────────────────────────────────────────────┘
```

### 2.2 Komponentenübersicht

| Layer | Komponente | Beispiel | Aufgabe |
|-------|-----------|----------|---------|
| **Presentation** | Controller | `CustomersController` | HTTP-Anfragen verarbeiten |
| **Business** | Service | `CustomersService` | Geschäftslogik implementieren |
| **Data Access** | Repository | `CustomersRepository` | Datenbankzugriff kapseln |
| **Entity** | Model | `Customers` | Datentypen definieren |
| **Database** | PostgreSQL | `classicmodels` DB | Daten persistent speichern |

---

## 3. Datenschichten im Detail

### 3.1 Controller Layer (src/generated/controllers/)

**Verantwortungen:**
- HTTP-Anfragen empfangen und validieren
- Request-Daten in Business-Objekte umwandeln
- Service-Methoden aufrufen
- Responses formatieren und HTTP-Status setzen
- Error-Responses generieren

**Beispiel: `CustomersController`**
```typescript
export class CustomersController {
  constructor(private service: CustomersService) {}

  async getAll(request: FastifyRequest, reply: FastifyReply) {
    const data = await this.service.getAll();
    return reply.send(data);  // 200 OK
  }

  async getById(request: FastifyRequest, reply: FastifyReply) {
    const { id } = request.params as { id: string };
    const data = await this.service.getById(parseInt(id, 10));
    return reply.send(data);  // 200 OK oder 404 Not Found
  }

  async create(request: FastifyRequest, reply: FastifyReply) {
    const data = await this.service.create(request.body);
    return reply.status(201).send(data);  // 201 Created
  }

  async update(request: FastifyRequest, reply: FastifyReply) {
    const { id } = request.params as { id: string };
    const data = await this.service.update(parseInt(id, 10), request.body);
    return reply.send(data);  // 200 OK
  }

  async delete(request: FastifyRequest, reply: FastifyReply) {
    const { id } = request.params as { id: string };
    await this.service.delete(parseInt(id, 10));
    return reply.status(204).send();  // 204 No Content
  }
}
```

**HTTP Mapping:**
```
GET    /api/customers       → getAll()
GET    /api/customers/:id   → getById(id)
POST   /api/customers       → create(body)
PUT    /api/customers/:id   → update(id, body)
DELETE /api/customers/:id   → delete(id)
```

### 3.2 Service Layer (src/generated/services/)

**Verantwortungen:**
- Geschäftslogik implementieren
- Validierung durchführen
- Fehler handhaben
- Repository-Methoden orchestrieren
- Optionale: Entities anreichern, cachen, logging

**Beispiel: `CustomersService`**
```typescript
export class CustomersService extends BaseService<Customers> {
  constructor(repository: CustomersRepository) {
    super(repository);
  }

  // Geerbt von BaseService:
  // - getById(id)
  // - getAll()
  // - create(data)
  // - update(id, data)
  // - delete(id)

  // Optional: Custom Business Logic
  async getVIPCustomers(): Promise<Customers[]> {
    const all = await this.repository.getAll();
    return all.filter(c => (c as any).creditlimit > 100000);
  }
}
```

**BaseService Template:**
```typescript
export abstract class BaseService<T> {
  constructor(protected repository: any) {}

  async getById(id: string | number): Promise<T> {
    const entity = await this.repository.findById(id);
    if (!entity) throw new Error('Entity not found');
    return entity;
  }

  async getAll(): Promise<T[]> {
    return this.repository.findAll();
  }

  async create(data: any): Promise<T> {
    return this.repository.create(data);
  }

  async update(id: string | number, data: any): Promise<T | null> {
    return this.repository.update(id, data);
  }

  async delete(id: string | number): Promise<boolean> {
    return this.repository.delete(id);
  }
}
```

### 3.3 Repository Layer (src/generated/repositories/)

**Verantwortungen:**
- SQL-Queries zusammenstellen
- Parameter binding durchführen
- Datenbankabfragen ausführen
- Ergebnisse in TypeScript-Objekte mappen
- Transaktionen verwalten

**Beispiel: `CustomersRepository`**
```typescript
export class CustomersRepository extends BaseRepository<Customers> {
  protected tableName = 'customers';
  protected primaryKey = 'customernumber';

  static COLUMNS = {
    customernumber: 'customernumber',
    customername: 'customername',
    contactlastname: 'contactlastname',
    // ... alle 13 Spalten
  };

  // Geerbt von BaseRepository:
  // - async findById(id): Customers | null
  // - async findAll(limit?, offset?): Customers[]
  // - async create(data): Customers
  // - async update(id, data): Customers | null
  // - async delete(id): boolean
  // - async count(): number
  // - async execute(sql, params): Customers[]
  // - async executeRaw(sql, params): any[]
}
```

**BaseRepository CRUD-Operationen:**
```typescript
// SELECT * FROM customers WHERE customernumber = $1
async findById(id: string | number): Promise<T | null>

// SELECT * FROM customers LIMIT 10 OFFSET 0
async findAll(limit?: number, offset?: number): Promise<T[]>

// INSERT INTO customers (...) VALUES (...) RETURNING *
async create(data: Partial<T>): Promise<T>

// UPDATE customers SET ... WHERE customernumber = $N RETURNING *
async update(id: string | number, data: Partial<T>): Promise<T | null>

// DELETE FROM customers WHERE customernumber = $1
async delete(id: string | number): Promise<boolean>

// SELECT COUNT(*) FROM customers
async count(): Promise<number>
```

### 3.4 Model Layer (src/generated/models/)

**Verantwortungen:**
- Datentypdefini­tionen
- Spalten-Metadaten speichern
- Helper-Methoden für Models
- Schreibschutz-Flags für Persistierung

**Beispiel: `Customers Model`**
```typescript
export class BaseModel {
  static _COLUMNS: string[] = [];
  static _PRIMARY_KEY: string | null = null;
  protected _modifiedColumns: Record<string, any> = {};

  get isDirty(): boolean {
    return this._modifiedColumns.length > 0;
  }

  get modifiedColumns(): Record<string, any> {
    return { ...this._modifiedColumns };
  }
}

export class Customers extends BaseModel {
  static _COLUMNS = [
    'customernumber',
    'customername',
    'contactlastname',
    'contactfirstname',
    'phone',
    'addressline1',
    'addressline2',
    'city',
    'state',
    'postalcode',
    'country',
    'salesrepemployeenumber',
    'creditlimit',
  ];

  static _PRIMARY_KEY = 'customernumber';
}
```

**Verwendung:**
```typescript
const customer = {
  customernumber: 103,
  customername: 'Atelier graphique',
  contactlastname: 'Schmitt',
  // ... alle anderen Spalten als Properties
};
```

### 3.5 DTO Layer (src/generated/dto/)

**Verantwortungen:**
- Validierungs-Schemas definieren
- Input/Output-Struktur dokumentieren
- Type-Safe Request/Response Handling

**Beispiel: `CustomersDTO`**
```typescript
export interface CustomersDTO {
  customernumber: number;
  customername: string;
  contactlastname: string;
  contactfirstname: string;
  phone: string;
  addressline1: string;
  addressline2?: string;
  city: string;
  state?: string;
  postalcode?: string;
  country: string;
  salesrepemployeenumber?: number;
  creditlimit?: number;
}

export interface CreateCustomersDTO {
  customername: string;
  contactlastname: string;
  contactfirstname: string;
  phone: string;
  addressline1: string;
  city: string;
  country: string;
  creditlimit?: number;
  // ... optional fields
}

export interface UpdateCustomersDTO {
  customername?: string;
  contactlastname?: string;
  // ... alle Felder optional für PATCH
}
```

---

## 4. Datenfluss - Beispiel Request

### 4.1 GET /api/customers/103

```
1. HTTP Request kommt an
   ├─ Method: GET
   ├─ Path: /api/customers/103
   └─ Headers: Content-Type: application/json

2. Fastify Router leitet weiter
   └─ Findet Route → CustomersController.getById()

3. Controller.getById()
   ├─ Extrahiert ID aus URL-Param: { id: "103" }
   ├─ Konvertiert zu number: 103
   └─ Ruft Service auf

4. CustomersService.getById(103)
   ├─ Validiert ID (ist number, > 0)
   ├─ Ruft Repository auf

5. CustomersRepository.findById(103)
   ├─ Baut SQL Query: "SELECT * FROM customers WHERE customernumber = $1"
   ├─ Bindet Parameter: [103]
   ├─ Sendet an PostgreSQL
   └─ Wartet auf Ergebnis

6. PostgreSQL Query Execution
   ├─ Führt Query aus
   ├─ Findet Row mit customernumber=103
   └─ Sendet Datensatz zurück

7. Repository.findById() bekommt Ergebnis
   ├─ Konvertiert Row zu TypeScript-Objekt
   └─ Gibt Customers-Objekt zurück

8. Service.getById() bekommt Objekt
   ├─ Optional: Anreicherung, Caching, Logging
   └─ Gibt Objekt zurück

9. Controller.getById() bekommt Objekt
   ├─ Formatiert als JSON
   ├─ Setzt HTTP-Status 200 OK
   └─ Sendet Response

10. Client empfängt
    ├─ Status: 200
    ├─ Body:
    │  {
    │    "customernumber": 103,
    │    "customername": "Atelier graphique",
    │    "contactlastname": "Schmitt",
    │    ...
    │  }
    └─ Headers: Content-Type: application/json
```

### 4.2 POST /api/customers (Create)

```
1. HTTP Request kommt an
   ├─ Method: POST
   ├─ Path: /api/customers
   ├─ Headers: Content-Type: application/json
   └─ Body:
      {
        "customername": "TechCorp",
        "contactlastname": "Smith",
        "contactfirstname": "John",
        "phone": "555-0000",
        "addressline1": "123 Main St",
        "city": "NYC",
        "country": "USA",
        "creditlimit": 50000
      }

2. Fastify Router
   └─ CustomersController.create()

3. Controller.create()
   ├─ Extrahiert Body
   ├─ Validiert Struktur (via DTO)
   └─ Ruft Service auf

4. CustomersService.create(data)
   ├─ Führt Validierung durch
   ├─ Prüft Business-Regeln
   └─ Ruft Repository auf

5. CustomersRepository.create(data)
   ├─ Baut INSERT Query
   ├─ SQL: INSERT INTO customers (...) VALUES (...) RETURNING *
   ├─ Bindet Werte als Parameter
   ├─ Sendet an PostgreSQL
   └─ Wartet auf RETURNING Clause

6. PostgreSQL INSERT
   ├─ Führt INSERT aus
   ├─ Generiert neue ID (serial)
   ├─ Validiert Foreign Keys
   ├─ Speichert Row
   └─ Gibt gesamten Record zurück

7. Repository bekommt Created Row
   ├─ Konvertiert zu Customers-Objekt
   └─ Gibt zurück

8. Service gibt Objekt zurück

9. Controller formatiert Response
   ├─ Setzt HTTP-Status 201 Created
   ├─ Setzt Location-Header
   └─ Sendet Body mit Created Entity

10. Client empfängt
    ├─ Status: 201 Created
    ├─ Headers: Location: /api/customers/999
    └─ Body: vollständiger neue Customer-Record
```

---

## 5. Design Patterns

### 5.1 Repository Pattern

**Ziel:** Abstraktion der Datenbankabfragen

**Implementierung:**
```typescript
// BaseRepository: Generischer CRUD-Zugriff
// ↓
// CustomersRepository: Tabellenspezifisch
//   ├─ Erbt findById, findAll, create, update, delete
//   └─ Kann erweitert werden: async findByCity(city: string) { ... }

const repo = new CustomersRepository(pool);
const customer = await repo.findById(103);
const all = await repo.findAll(10, 0);  // limit 10, offset 0
```

**Vorteile:**
- Datenbank-Logik gekapselt
- Einfach austauschbar (z.B. auf MongoDB wechseln)
- Testbar (Mock-Repository)
- Wiederverwendbar

### 5.2 Service Layer Pattern

**Ziel:** Business-Logik von HTTP entkoppeln

**Implementierung:**
```typescript
// Controller → Service → Repository
// Service ist reusable, kann von CLI/GraphQL/WebSocket verwendet werden

export class CustomersService extends BaseService<Customers> {
  constructor(private repo: CustomersRepository) {
    super(repo);
  }

  // Geerbt: getById, getAll, create, update, delete

  // Custom Business Logic
  async getVIPCustomers() { ... }
  async validateCustomer(data) { ... }
  async enrichCustomer(customer) { ... }
}
```

**Vorteile:**
- Business-Logik testbar ohne HTTP
- Kann von mehreren Interfaces verwendet werden
- Klare Separation of Concerns

### 5.3 Dependency Injection

**Ziel:** Lose Kopplung und Testbarkeit

**Implementierung (Manual):**
```typescript
// src/routes/index.ts
const customersRepo = new CustomersRepository(pool);
const customersService = new CustomersService(customersRepo);
const customersController = new CustomersController(customersService);

app.get('/api/customers/:id', (req, res) =>
  customersController.getById(req, res)
);
```

**Vorteile:**
- Explizit und einfach zu verstehen
- Keine DI-Framework-Magie
- Gut für Unit-Tests (Mocks injizieren)

### 5.4 Data Transfer Object (DTO) Pattern

**Ziel:** Request/Response Validierung und Transformation

**Implementierung:**
```typescript
// CreateCustomersDTO definiert, welche Felder required sind
export interface CreateCustomersDTO {
  customername: string;      // required
  contactlastname: string;    // required
  creditlimit?: number;       // optional
}

// Controller validiert gegen DTO
async create(request: FastifyRequest) {
  const data: CreateCustomersDTO = request.body;
  // Type-safety garantiert
}
```

**Vorteile:**
- Type-Safety
- Dokumentation
- Validierung
- Unterscheidung Create vs Update vs Query

---

## 6. REST API Design

### 6.1 Standard REST Endpoints

**Pro Tabelle gibt es 5 Standard-Endpoints:**

```
GET    /api/{resource}           # List (mit Pagination)
GET    /api/{resource}/{id}      # Retrieve
POST   /api/{resource}           # Create
PUT    /api/{resource}/{id}      # Update (ganz)
DELETE /api/{resource}/{id}      # Delete
```

**Beispiel Customers:**
```bash
GET    /api/customers             # Alle Customers
GET    /api/customers/103         # Customer mit ID 103
GET    /api/customers?limit=10&offset=20  # Mit Pagination
POST   /api/customers             # Neuen Customer erstellen
PUT    /api/customers/103         # Customer 103 aktualisieren
DELETE /api/customers/103         # Customer 103 löschen
```

### 6.2 HTTP Status Codes

| Code | Situation | Beispiel |
|------|-----------|----------|
| 200 | Success (GET, PUT) | `GET /api/customers/103` → Customer gelesen |
| 201 | Created (POST) | `POST /api/customers` → Neuer Customer erstellt |
| 204 | No Content (DELETE) | `DELETE /api/customers/103` → Gelöscht, kein Body |
| 400 | Bad Request | POST mit ungültigen Feldern |
| 404 | Not Found | `GET /api/customers/99999` → Customer nicht vorhanden |
| 500 | Server Error | Unerwarteter Fehler in Service/Repository |

### 6.3 Request/Response Format

**Request (POST /api/customers):**
```json
{
  "customername": "TechCorp",
  "contactlastname": "Doe",
  "contactfirstname": "John",
  "phone": "555-1234",
  "addressline1": "123 Main St",
  "city": "NYC",
  "country": "USA",
  "creditlimit": 50000
}
```

**Response (201 Created):**
```json
{
  "customernumber": 999,
  "customername": "TechCorp",
  "contactlastname": "Doe",
  "contactfirstname": "John",
  "phone": "555-1234",
  "addressline1": "123 Main St",
  "addressline2": null,
  "city": "NYC",
  "state": null,
  "postalcode": null,
  "country": "USA",
  "salesrepemployeenumber": null,
  "creditlimit": 50000
}
```

---

## 7. Datenbankdesign

### 7.1 Schema Übersicht

**7 Tabellen mit komplexen Relationships:**

```
┌─────────────────┐
│   offices       │  9 Spalten
├─────────────────┤
│ officeCode (PK) │
│ city            │
│ phone           │
│ ...             │
└────────┬────────┘
         │ FK
         ├─────────────────────────────┐
         ↓                             ↓
┌─────────────────┐         ┌──────────────────┐
│   employees     │         │   customers      │  13 Spalten
├─────────────────┤         ├──────────────────┤
│ employeeNumber  │         │ customerNumber   │
│ lastName        │─────┐   │ customerName     │
│ firstName       │     │   │ phone            │
│ office (FK)     │     │   │ salesRep (FK)    │
│ reportsTo (FK)  │     │   │ creditLimit      │
│ ...             │     │   │ ...              │
└────────┬────────┘     │   └────────┬─────────┘
         │ self-ref     │            │
         └──────────────┼────────────┤
                        │            │
                        ↓            ↓
              ┌──────────────────────────┐
              │      orders             │  7 Spalten
              ├──────────────────────────┤
              │ orderNumber (PK)         │
              │ orderDate                │
              │ requiredDate             │
              │ shippedDate              │
              │ status                   │
              │ comments                 │
              │ customer (FK)            │
              └────────────┬─────────────┘
                           │
                           ↓
              ┌──────────────────────────┐
              │  orderdetails           │  5 Spalten
              ├──────────────────────────┤
              │ orderNumber (FK, PK)     │
              │ productCode (FK, PK)     │
              │ quantityOrdered          │
              │ priceEach                │
              │ orderLineNumber          │
              └──────────────────────────┘
                           ↑
                           │ FK
        ┌──────────────────┴──────────────────┐
        ↓                                      ↓
┌──────────────────┐              ┌──────────────────┐
│   productlines   │  4 Spalten  │   products       │  9 Spalten
├──────────────────┤              ├──────────────────┤
│ productLine (PK) │              │ productCode (PK) │
│ textDescription  │              │ productName      │
│ htmlDescription  │◄─────────────│ productLine (FK) │
│ image (BYTEA)    │              │ productScale     │
└──────────────────┘              │ productVendor    │
                                  │ productDescription
                                  │ quantityInStock  │
                                  │ buyPrice         │
                                  │ MSRP             │
                                  └──────────────────┘
```

### 7.2 Key Constraints

**Primary Keys (eindeutige Identifikatoren):**
- `offices.officeCode`
- `employees.employeeNumber`
- `customers.customerNumber`
- `orders.orderNumber`
- `products.productCode`
- `productlines.productLine`
- `orderdetails.(orderNumber, productCode)` - Composite Key

**Foreign Keys (Relationships):**
- `employees.officeCode` → `offices.officeCode`
- `employees.reportsTo` → `employees.employeeNumber` (self-ref)
- `customers.salesRepEmployeeNumber` → `employees.employeeNumber`
- `orders.customerNumber` → `customers.customerNumber`
- `orderdetails.orderNumber` → `orders.orderNumber`
- `orderdetails.productCode` → `products.productCode`
- `products.productLine` → `productlines.productLine`

### 7.3 Indexes

**Für Performance:**
```sql
CREATE INDEX idx_customers_country ON customers(country);
CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_customers_salesRep ON customers(salesRepEmployeeNumber);
CREATE INDEX idx_orders_customer ON orders(customerNumber);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orderdetails_product ON orderdetails(productCode);
CREATE INDEX idx_products_line ON products(productLine);
```

---

## 8. Code-Struktur und File Organization

### 8.1 Verzeichnisstruktur

```
tests/middleware-demo/
├── src/
│   ├── generated/               # Auto-generiert by pyStoOrm
│   │   ├── models/             # Entity definitions (7 files)
│   │   │   ├── customers.model.ts
│   │   │   ├── orders.model.ts
│   │   │   ├── products.model.ts
│   │   │   ├── employees.model.ts
│   │   │   ├── offices.model.ts
│   │   │   ├── orderdetails.model.ts
│   │   │   └── productlines.model.ts
│   │   ├── repositories/       # Database access (7 files)
│   │   │   ├── customers.repository.ts
│   │   │   ├── orders.repository.ts
│   │   │   ├── products.repository.ts
│   │   │   └── ...
│   │   ├── services/           # Business logic (7 files)
│   │   │   ├── customers.service.ts
│   │   │   ├── orders.service.ts
│   │   │   └── ...
│   │   ├── dto/                # Data transfer objects (7 files)
│   │   │   ├── customers.dto.ts
│   │   │   └── ...
│   │   └── controllers/        # HTTP handlers (7 files)
│   │       ├── customers.controller.ts
│   │       └── ...
│   │
│   ├── custom-logic/           # Optional: Extensions
│   │   └── customer-service.ts # Custom CustomerService
│   │
│   ├── app.ts                 # Fastify App Setup
│   ├── routes/
│   │   └── index.ts           # Route Registration & DI
│   └── server.ts              # Entry Point
│
├── dist/                       # Compiled JavaScript (npm run build)
├── node_modules/               # Dependencies
├── package.json               # npm Konfiguration
├── tsconfig.json              # TypeScript Konfiguration
├── .env                       # Environment Variables
├── docker-compose.yml         # PostgreSQL Setup
├── init.sql                   # Database Schema & Sample Data
├── project.yml                # pyStoOrm Configuration
├── API_QUICKSTART.md          # Getting Started Guide
└── ARCHITECTURE.md            # This file
```

### 8.2 Typ der Datei vs. Inhalt

| Datei | Generiert? | Ändern? | Erklärung |
|-------|-----------|--------|-----------|
| `models/*.model.ts` | ✅ Ja | ❌ Nein | Automatisch aus DB generiert |
| `repositories/*.repository.ts` | ✅ Ja | ⚠️ Erweitern | CRUD + custom finders |
| `services/*.service.ts` | ✅ Ja | ⚠️ Erweitern | Business-Logik hooks |
| `dto/*.dto.ts` | ✅ Ja | ❌ Nein | Validierungs-Interfaces |
| `controllers/*.controller.ts` | ✅ Ja | ⚠️ Erweitern | HTTP-Handler |
| `app.ts` | ❌ Nein | ✅ Ja | Fastify-Setup |
| `routes/index.ts` | ❌ Nein | ✅ Ja | Route-Registrierung |
| `server.ts` | ❌ Nein | ✅ Ja | Entry Point |

---

## 9. Deployment Architecture

### 9.1 Development Setup

```
┌────────────────────────────────┐
│  Developer Machine (localhost) │
├────────────────────────────────┤
│                                │
│  ┌──────────────────────────┐  │
│  │  Node.js + TypeScript    │  │
│  │  npm run start:dev       │  │
│  │  Läuft auf :3000         │  │
│  └──────────────────────────┘  │
│            ↓ (Port 3000)        │
│  ┌──────────────────────────┐  │
│  │  PostgreSQL (Docker)     │  │
│  │  docker-compose up       │  │
│  │  Läuft auf :5432         │  │
│  │  pgAdmin auf :5050       │  │
│  └──────────────────────────┘  │
│            ↓ (Port 5432)        │
│  ┌──────────────────────────┐  │
│  │  classicmodels DB        │  │
│  │  50+ sample rows         │  │
│  │  7 tables                │  │
│  └──────────────────────────┘  │
│                                │
└────────────────────────────────┘
```

### 9.2 Production Setup (Konzept)

```
┌─────────────────────────────────────────────────────────┐
│                   Internet / Load Balancer              │
└────────────────┬────────────────────────────────────────┘
                 │ HTTPS:443
                 ↓
┌─────────────────────────────────────────────────────────┐
│          Kubernetes / Docker Swarm / ECS / etc.         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │ API Pod 1        │  │ API Pod 2        │  (replicas)│
│  │ Node.js 18+      │  │ Node.js 18+      │             │
│  │ Port 3000        │  │ Port 3000        │             │
│  └────────┬─────────┘  └────────┬─────────┘             │
│           │                     │                       │
│           └──────────┬──────────┘                       │
│                      ↓ Database Pool                     │
│  ┌──────────────────────────────────────────┐           │
│  │ PostgreSQL Managed Service (RDS, etc.)   │           │
│  │ - Replication                            │           │
│  │ - Backups                                │           │
│  │ - Failover                               │           │
│  │ - Monitoring                             │           │
│  └──────────────────────────────────────────┘           │
│                                                         │
│  ┌──────────────────────────────────────────┐           │
│  │ Monitoring & Logging (CloudWatch, etc.)  │           │
│  │ - Request Logging                        │           │
│  │ - Error Tracking                         │           │
│  │ - Performance Metrics                    │           │
│  └──────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

### 9.3 Build Pipeline

```
Source Code
    ↓ (git push)
Continuous Integration
    ├─ npm install
    ├─ npm run type-check
    ├─ npm run build
    ├─ npm run lint
    ├─ npm run test
    └─ Generate Docker Image
         ↓
Container Registry
    ├─ ECR
    ├─ Docker Hub
    └─ GitHub Container Registry
         ↓
Deploy to Staging
    ├─ Run integration tests
    ├─ Performance tests
    └─ Manual approval
         ↓
Deploy to Production
    ├─ Blue-Green Deployment
    ├─ Health checks
    └─ Monitor
```

---

## 10. Erweiterbarkeit

### 10.1 Neue Tabelle hinzufügen

**Schritt-für-Schritt:**

```bash
# 1. Neue Tabelle in PostgreSQL erstellen
ALTER TABLE ... CREATE TABLE supplier (
  supplierID INT PRIMARY KEY,
  supplierName VARCHAR(100) NOT NULL,
  contactEmail VARCHAR(100),
  ...
);

# 2. Neu generieren
npm run generate

# 3. Kompilieren
npm run build

# 4. Routes registrieren (src/routes/index.ts)
const supplierRepo = new SupplierRepository(pool);
const supplierService = new SupplierService(supplierRepo);
const supplierController = new SupplierController(supplierService);

app.get('/api/suppliers', (req, res) => supplierController.getAll(req, res));
// ... weitere Routes

# 5. Server neustarten
npm run start
```

**Resultat:** Neue API mit 5 Endpoints automatisch verfügbar!

### 10.2 Custom Business Logic hinzufügen

**Beispiel: Eigener CustomerService**

```typescript
// src/custom-logic/customer-service.ts
import { CustomersService as GeneratedService } from '../generated/services/customers.service';
import { CustomersRepository } from '../generated/repositories/customers.repository';

export class CustomCustomerService extends GeneratedService {
  constructor(repo: CustomersRepository) {
    super(repo);
  }

  // Erbt: getById, getAll, create, update, delete

  // Neue Custom Methods
  async getVIPCustomers() {
    const all = await this.repository.getAll();
    return all.filter(c => (c as any).creditlimit > 100000);
  }

  async getSalesRepStats(repId: number) {
    const customers = await this.repository.getAll();
    return customers.filter(c =>
      (c as any).salesrepemployeenumber === repId
    );
  }

  async enrichCustomer(customer: any) {
    // Füge zusätzliche Daten hinzu
    return {
      ...customer,
      vip: customer.creditlimit > 100000,
      status: customer.creditlimit > 0 ? 'active' : 'inactive'
    };
  }
}
```

**In src/routes/index.ts verwenden:**
```typescript
import { CustomCustomerService } from '../custom-logic/customer-service';

const customersRepo = new CustomersRepository(pool);
const customersService = new CustomCustomerService(customersRepo);

// Alle neuen Methods sind verfügbar!
app.get('/api/customers/vip', async (req, res) => {
  const vipCustomers = await customersService.getVIPCustomers();
  return res.send(vipCustomers);
});
```

### 10.3 Caching hinzufügen

```typescript
// services/customers.service.ts mit Redis
export class CustomersService extends BaseService<Customers> {
  private cache = new Map<string, any>();

  async getById(id: string | number): Promise<Customers> {
    const cacheKey = `customer:${id}`;

    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const customer = await super.getById(id);
    this.cache.set(cacheKey, customer);
    return customer;
  }

  async update(id: string | number, data: any) {
    const result = await super.update(id, data);
    // Invalidate cache
    this.cache.delete(`customer:${id}`);
    return result;
  }
}
```

### 10.4 Authentifizierung hinzufügen

```typescript
// routes/index.ts mit JWT
import jwt from '@fastify/jwt';

app.register(jwt, { secret: process.env.JWT_SECRET });

app.addHook('onRequest', async (request, reply) => {
  try {
    await request.jwtVerify();
  } catch (err) {
    reply.status(401).send({ error: 'Unauthorized' });
  }
});

// Routes sind jetzt geschützt
app.get('/api/customers', async (req, res) => {
  // req.user ist vorhanden
  const userId = req.user.id;
  // ...
});
```

---

## 11. Testing Architecture

### 11.1 Unit Tests (Service Layer)

```typescript
// tests/services/customer-service.test.ts
describe('CustomersService', () => {
  let service: CustomersService;
  let mockRepo: CustomersRepository;

  beforeEach(() => {
    // Mock Repository
    mockRepo = {
      findById: jest.fn(),
      findAll: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
    } as any;

    service = new CustomersService(mockRepo);
  });

  test('getById should call repository.findById', async () => {
    await service.getById(103);
    expect(mockRepo.findById).toHaveBeenCalledWith(103);
  });

  test('create should validate data', async () => {
    const invalidData = { customername: '' };
    await expect(service.create(invalidData)).rejects.toThrow();
  });
});
```

### 11.2 Integration Tests (Full Stack)

```typescript
// tests/integration/customers.test.ts
describe('GET /api/customers', () => {
  let app: FastifyInstance;

  beforeAll(async () => {
    app = await createApp();
    await app.listen({ port: 3001 });
  });

  test('should return all customers', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/customers'
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThan(0);
  });

  test('should get customer by ID', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/customers/103'
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.customernumber).toBe(103);
  });

  afterAll(async () => {
    await app.close();
  });
});
```

---

## 12. Performance Considerations

### 12.1 Database Optimization

**Connections Pooling:**
```typescript
const pool = new Pool({
  max: 20,              // Max connections
  idleTimeoutMillis: 30000,  // Timeout inactive
  connectionTimeoutMillis: 2000,
});
```

**Query Optimization:**
- Indexes auf Foreign Keys und WHERE-Spalten
- LIMIT/OFFSET für Pagination
- SELECT nur benötigte Spalten (nicht *)
- Connection Pooling für Multiplex

### 12.2 API Response Caching

```typescript
// Controller mit Cache Headers
async getAll(request: FastifyRequest, reply: FastifyReply) {
  const customers = await this.service.getAll();

  // Browser Cache: 5 Minuten
  reply.header('Cache-Control', 'public, max-age=300');

  // ETag für Conditional Requests
  reply.header('ETag', `"${Hash(JSON.stringify(customers))}"`);

  return reply.send(customers);
}
```

### 12.3 Pagination

```typescript
// Client Request
GET /api/customers?limit=20&offset=40

// Service
async getAll(limit: number = 10, offset: number = 0) {
  return this.repository.findAll(limit, offset);
}

// Repository
async findAll(limit?: number, offset?: number): Promise<T[]> {
  let query = 'SELECT * FROM "' + this.tableName + '"';

  if (limit) query += ' LIMIT $1';
  if (offset) query += ' OFFSET $2';

  return this.pool.query(query, [limit, offset]);
}
```

---

## 13. Security Architecture

### 13.1 Input Validation

```typescript
// Controller
async create(request: FastifyRequest, reply: FastifyReply) {
  const data = request.body;

  // Validate structure
  if (!data.customername || typeof data.customername !== 'string') {
    return reply.status(400).send({ error: 'Invalid customername' });
  }

  // Validate length
  if (data.customername.length > 100) {
    return reply.status(400).send({ error: 'Name too long' });
  }

  // Pass to service
  return reply.status(201).send(await this.service.create(data));
}
```

### 13.2 SQL Injection Prevention

**Parameterized Queries (automatisch):**
```typescript
// WRONG - SQL Injection vulnerable
const query = `SELECT * FROM customers WHERE customername = '${name}'`;

// RIGHT - Parameterized (was wir machen)
const query = "SELECT * FROM customers WHERE customername = $1";
await pool.query(query, [name]);  // Parameter binding
```

### 13.3 Authentication/Authorization

```typescript
// Middleware für JWT
import fastifyJwt from '@fastify/jwt';

app.register(fastifyJwt, { secret: process.env.JWT_SECRET });

// Protect routes
app.addHook('onRequest', async (request, reply) => {
  try {
    await request.jwtVerify();
  } catch (err) {
    reply.status(401).send({ error: 'Unauthorized' });
  }
});
```

---

## 14. Monitoring & Observability

### 14.1 Logging

```typescript
// Automatisch in Fastify/Pino
{"level":30,"time":1775009590816,"reqId":"req-2",
 "res":{"statusCode":200},"responseTime":23.49,"msg":"request completed"}
```

### 14.2 Error Tracking

```typescript
// Controller mit Error Handling
async getById(request: FastifyRequest, reply: FastifyReply) {
  try {
    const data = await this.service.getById(parseInt(id));
    return reply.send(data);
  } catch (error) {
    logger.error({ error }, 'Failed to get customer');
    return reply.status(500).send({ error: 'Internal Server Error' });
  }
}
```

### 14.3 Health Checks

```typescript
// GET /health
app.get('/health', async () => ({
  status: 'ok',
  timestamp: new Date().toISOString(),
  uptime: process.uptime(),
  database: 'connected'
}));
```

---

## Summary: Architecture Highlights

| Aspekt | Lösung | Benefit |
|--------|--------|---------|
| **Code Generation** | pyStoOrm | Keine Boilerplate, Schema als Source of Truth |
| **Type Safety** | TypeScript strict | Fehler zur Compile-Zeit, nicht Runtime |
| **Layering** | Controllers → Services → Repositories | Testbar, wartbar, loose coupling |
| **Data Access** | Repository Pattern | Datenbank austauschbar |
| **API Design** | REST standard | Clients verstehen sofort |
| **Database** | PostgreSQL + Indexes | Performance, Zuverlässigkeit |
| **Async/Await** | Node.js native | Non-blocking, skalierbar |
| **Error Handling** | Try/catch + HTTP Status | User-friendly Errors |
| **Scalability** | Connection pooling, caching | Viele concurrent Requests |
| **Testing** | Unit + Integration | Vertrauen in Deployment |

---

## Weiterführende Ressourcen

- **REST API Design**: https://restfulapi.net/
- **TypeScript Handbook**: https://www.typescriptlang.org/docs/
- **Fastify Documentation**: https://www.fastify.io/docs/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Design Patterns**: https://refactoring.guru/design-patterns
- **Clean Code Principles**: https://en.wikipedia.org/wiki/SOLID
