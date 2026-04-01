# pyStoOrm Middleware Demo - Zusammenfassung der Entwicklung

## Überblick

Dieses Projekt demonstriert eine vollständige **REST-API-Middleware** auf Basis von pyStoOrm mit:
- **PostgreSQL** als Datenbank
- **TypeScript** für Typ-Sicherheit
- **Fastify** als HTTP-Framework
- **Automatische Code-Generierung** für Models, Repositories, Services, DTOs und Controller

## Was wurde heute entwickelt?

### 1. PostgreSQL-Unterstützung in pyStoOrm

**Problem:** pyStoOrm unterstützte nur MySQL.

**Lösung:**
- Neuer `PostgreSQL Connector` basierend auf `psycopg2`
- Korrekte SQL-Syntaxen für PostgreSQL
- Foreign Key Introspection für relationalen Datenmodelle

**Dateien:**
- `pystoorm/database/postgresqlconnector.py` - Komplett neu geschrieben
- `pystoorm/__main__.py` - Pfad-Auflösung korrigiert (nur für SQLite)
- `requirements.txt` - `psycopg2-binary` hinzugefügt

### 2. TypeScript Code-Generierung

**5 neue Mako-Templates erstellt:**

1. **model.ts.template** - Datenmodelle
   - BaseModel Klasse mit Dirty-Tracking
   - Per-Tabelle Model-Klassen
   - TypeScript Interfaces

2. **repository.ts.template** - Datenzugriff
   - BaseRepository mit CRUD-Operationen
   - Vorbereitete PostgreSQL-Statements ($1, $2, ...)
   - Per-Tabelle Repository-Klassen

3. **service.ts.template** - Business Logic Layer
   - BaseService mit Service-Methoden
   - Platz für Custom-Logic
   - Per-Tabelle Service-Klassen

4. **dto.ts.template** - Data Transfer Objects
   - TypeScript Interfaces für Request/Response
   - Type-safe Request Validation

5. **controller.ts.template** - HTTP Handler
   - Fastify-Controller mit getAll, getById, create, update, delete
   - FastifyRequest/FastifyReply Integration
   - Korrekte HTTP Status-Codes (200, 201, 204, 400, 404, 500)

**Location:** `pystoorm/templates/typescript/`

### 3. Middleware Demo-Projekt (`tests/middleware-demo/`)

Ein **production-ready** Beispiel-Projekt, das zeigt, wie man pyStoOrm mit TypeScript nutzt.

#### Verzeichnisstruktur:
```
tests/middleware-demo/
├── docker-compose.yml           # PostgreSQL + pgAdmin Setup
├── init.sql                     # 7 Tabellen + Sample-Daten
├── project.yml                  # pyStoOrm TypeScript-Konfiguration
├── package.json                 # npm Dependencies
├── tsconfig.json                # TypeScript Config (strict mode)
│
├── src/
│   ├── base/                    # Abstrakte Basis-Klassen
│   │   ├── base-repository.ts   # Generischer CRUD-Zugriff
│   │   ├── base-service.ts      # Service-Basis mit Hooks
│   │   └── types.ts             # Shared TypeScript Types
│   │
│   ├── core/                    # Kerninfrastruktur
│   │   ├── database.ts          # PostgreSQL Pool
│   │   ├── server.ts            # Fastify Setup
│   │   ├── logger.ts            # pino Logging
│   │   └── config.ts            # Umgebungs-Konfiguration
│   │
│   ├── generated/               # Auto-generiert von pyStoOrm
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── dto/
│   │   └── controllers/
│   │
│   ├── routes/
│   │   └── index.ts             # Route-Registrierung mit DI
│   │
│   ├── app.ts                   # Fastify App Initialisierung
│   └── server.ts                # Entry Point
│
├── tests/
│   └── integration/
│       └── api.test.ts          # Integration Tests
│
├── ARCHITECTURE.md              # Detaillierte Architektur (14 Sections)
├── API_QUICKSTART.md            # Quick Start Guide
├── test-api.sh                  # API Test-Script
└── README.md                    # Projekt-Übersicht
```

## Architektur: 5-Layer REST API

```
HTTP Request
    ↓
[Controller]       # HTTP-Handling (FastifyRequest/Reply)
    ↓
[Service]         # Business Logic (Validierung, Regeln)
    ↓
[Repository]      # Data Access (SQL-Queries)
    ↓
[Model]           # TypeScript Entities
    ↓
[PostgreSQL]      # Persistent Storage
```

**Beispiel: GET /api/customers/103**
1. CustomersController.getById(req, res)
2. CustomersService.getById(103)
3. CustomersRepository.findById(103) → SELECT * FROM customers WHERE id = $1
4. Rückgabe: Customer-Objekt als JSON

## Datenbank: 7 Tabellen

| Tabelle | Spalten | Primärschlüssel | Relationships |
|---------|---------|-----------------|---------------|
| **offices** | 9 | officeCode | Parent: employees, employees |
| **employees** | 8 | employeeNumber | Parent: offices; Child: customers |
| **customers** | 13 | customerNumber | Parent: employees; Child: orders |
| **products** | 9 | productCode | Parent: productlines; Child: orderdetails |
| **productlines** | 4 | productLine | Parent: products |
| **orders** | 7 | orderNumber | Parent: customers; Child: orderdetails |
| **orderdetails** | 5 | (orderNumber, productCode) | Parent: orders, products |

**Sample-Daten:**
- 6 Büros (San Francisco, Boston, NYC, Paris, Tokyo, Sydney)
- 8 Mitarbeiter
- 6 Produktlinien
- 7 Produkte
- 6 Kunden
- 5 Bestellungen mit 7 Details

## Technologie-Stack

| Component | Technologie | Version |
|-----------|-------------|---------|
| **Runtime** | Node.js | 18+ |
| **Language** | TypeScript | 5.0+ |
| **HTTP** | Fastify | 4.0+ |
| **Database** | PostgreSQL | 15 (Alpine) |
| **ORM** | pg (node-postgres) | 8.0+ |
| **Validation** | Zod | 3.0+ |
| **Testing** | Jest | 29.0+ |
| **Logging** | pino | 8.0+ |

## Getting Started

### 1. Datenbank starten
```bash
docker-compose up -d
```

### 2. TypeScript Code generieren
```bash
cd ../..  # Zur pyStoOrm Root
python -m pystoorm --config tests/middleware-demo/project.yml
cd tests/middleware-demo
```

### 3. Dependencies installieren
```bash
npm install
```

### 4. TypeScript kompilieren
```bash
npm run build
```

### 5. Server starten
```bash
npm run dev
```
Server läuft auf http://localhost:3000

### 6. API testen
```bash
# Health Check
curl http://localhost:3000/health

# Alle Kunden abrufen
curl http://localhost:3000/api/customers

# Kunde mit ID 103
curl http://localhost:3000/api/customers/103

# Neuen Kunden erstellen
curl -X POST http://localhost:3000/api/customers \
  -H "Content-Type: application/json" \
  -d '{"customername":"Tech Corp","country":"USA"}'
```

## REST API Endpoints

Für jede der 7 Tabellen verfügbar:

```
GET    /api/{table}              # Alle Datensätze
GET    /api/{table}/:id          # Einzelner Datensatz
POST   /api/{table}              # Neuen erstellen (201 Created)
PUT    /api/{table}/:id          # Aktualisieren
DELETE /api/{table}/:id          # Löschen
```

**Beispiele:**
- `GET /api/customers` → Array von Customers
- `POST /api/orders` → Neue Bestellung erstellen
- `PUT /api/products/SKU123` → Produkt aktualisieren
- `DELETE /api/orderdetails/123-ABC` → Order-Detail löschen

## Code-Generierung Workflow

```
1. project.yml konfigurieren
   ↓
2. pyStoOrm ausführen
   python -m pystoorm --config project.yml
   ↓
3. Generierte Dateien in src/generated/
   ├── models/
   ├── repositories/
   ├── services/
   ├── dto/
   └── controllers/
   ↓
4. Manuell erweitern in src/routes/index.ts
   (Route-Registrierung, Custom-Logic)
   ↓
5. npm run build && npm run dev
```

## Architektur-Dokumentation

Ausführliche Dokumentation verfügbar:

- **ARCHITECTURE.md** - 14 Sections
  - System Overview
  - Layer Descriptions
  - Request/Response Examples
  - Design Patterns
  - Database Schema
  - Deployment
  - Testing Strategy
  - Security Architecture

- **API_QUICKSTART.md** - Praktische Beispiele
  - Setup-Schritte
  - cURL-Befehle
  - Troubleshooting

## Besonderheiten

### Type Safety
- End-to-end TypeScript Kompilierung mit `strict: true`
- Auto-generierte Models, Repositories, Services
- Keine `any` Types

### Dependency Injection
- Manuelles Constructor Injection (einfach, explizit)
- Keine Container-Magic
- Testbar und debuggbar

### Error Handling
- Global Error Handler in Fastify
- HTTP Status-Codes: 200, 201, 204, 400, 404, 500
- Strukturierte Error-Response

### Extensibility
- Basis-Klassen (`BaseRepository`, `BaseService`) erweitern
- Hooks in Service-Schicht (beforeCreate, afterCreate, etc.)
- Custom Repositories mit zusätzlichen Finders

## Nächste Schritte

### Für Benutzer dieses Projekts:
1. Projekt klonen
2. `docker-compose up -d` starten
3. `npm install` ausführen
4. `npm run dev` starten
5. API unter http://localhost:3000 nutzen

### Zur Erweiterung:
- Neue Tabellen in der Datenbank hinzufügen
- `project.yml` aktualisieren
- `pyStoOrm` erneut ausführen → neue generierte Dateien
- Custom-Logic in `src/routes/index.ts` hinzufügen

### Authentication/Authorization:
- JWT Middleware in `src/routes/index.ts` hinzufügbar
- Fastify Plugins für Authentifizierung

### Testing:
- Integration Tests in `tests/integration/`
- Unit Tests für Custom-Services
- `npm run test` ausführen

## Fazit

Dieses Projekt zeigt, wie pyStoOrm eine **vollständige REST-API** mit:
- ✅ Automatischer Code-Generierung
- ✅ Type-Safe TypeScript
- ✅ PostgreSQL Datenbank
- ✅ Production-Ready Framework (Fastify)
- ✅ Klare Architektur (5 Layer)
- ✅ Erweiterbar und wartbar

**Ergebnis:** Entwickler können sich auf **Business-Logic** konzentrieren, nicht auf Infrastruktur.
