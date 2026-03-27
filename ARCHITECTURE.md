# pyStoOrm - Architektur & Funktionsweise

pyStoOrm ist ein **ORM-Code-Generator**, der ein bestehendes Datenbankschema (MySQL/PostgreSQL) analysiert und automatisch Python-ORM-Klassen generiert.

## 📊 Workflow - Von der Datenbank zum Code

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Konfiguration einlesen                                   │
│    (bootstrap.yml + project.yml)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 2. Datenbank-Analyzer (Controller)                          │
│    • Verbindung aufbauen                                    │
│    • Datenbank-Schema auslesen                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 3. Schema Parsing (Parser)                                  │
│    • Tabellen auflisten                                     │
│    • Spalten pro Tabelle auslesen                           │
│    • Column-Metadaten extrahieren                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 4. Code-Generator (Coordinator)                             │
│    • Templates laden (Mako)                                 │
│    • Python-Klassen rendern                                 │
│    • Output speichern                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Systemarchitektur

### Module & Komponenten

```
pystoorm/
├── pystoorm.py              # Einstiegspunkt / Main
├── analyzer/
│   ├── controller.py        # Orchestriert DB-Analyse
│   └── parser.py            # Parst Schema-Daten
├── database/
│   ├── connector.py         # Abstract Base Class
│   ├── mysqlconnector.py    # MySQL-Implementierung
│   ├── postgresqlconnector.py # PostgreSQL-Implementierung
│   ├── schema.py            # Schema-Datenmodell
│   ├── table.py             # Table-Datenmodell
│   ├── column.py            # Column-Datenmodell
│   ├── reference.py         # Foreign Key-Referenz
│   └── nullconnector.py     # Dummy (Testing)
├── generator/
│   └── coordinator.py       # Generiert Code aus Templates
└── templates/
    ├── python/
    │   ├── model.py.template
    │   └── repository.py.template
    └── erd/
        └── graphviz.template
```

---

## 🔄 Detaillierter Prozessfluss

### 1️⃣ **Einstiegspunkt: `pystoorm.py`**

```python
# Hauptablauf:
1. Kommandozeilenargumente parsen
2. bootstrap.yml laden (globale Konfiguration)
3. project.yml laden (projektspezifische Einstellungen)
4. Konfigurationen zusammenführen
5. Controller + Coordinator starten
```

**Konfiguration Beispiel:**
```yaml
# bootstrap.yml
connections:
  - # wird durch project.yml gefüllt
name: Harald Stowasser
logLevel: WARN
output:
  - from: ./templates/python/model.py.template
    to: ${project}/orm/model/[table].py

# project.yml
connections:
  - connection: classicmodels
    host: 127.0.0.1
    username: pystoorm
    password: pystoormpw
    database: classicmodels
    connector: database.mysqlconnector.MysqlConnector
```

---

### 2️⃣ **Analyse: `analyzer/controller.py`**

**Rolle:** Orchestriert die Datenbankverbindung und Schema-Analyse

**Hauptmethoden:**

| Methode | Zweck |
|---------|-------|
| `conector_fabrik()` | Factory-Pattern: lädt dynamisch den richtigen Connector |
| `build_import()` | Konvertiert Connector-Namen zu Python Import-Path |
| `walk()` | Iteriert über alle Connections, analysiert jede DB |

**Ablauf in `walk()`:**
```python
for connection in config['connections']:
    1. Connector-Klasse dynamisch laden (MysqlConnector/PostgresqlConnector)
    2. Connection-Config dem Connector übergeben
    3. Verbindung zur DB aufbauen → connector.connect()
    4. Parser starten → parser.parse() → liefert Schema-Objekt
    5. Schema speichern in connection["parsedSchema"]
```

---

### 3️⃣ **Datenbank-Connector: `database/connector.py` + Implementierungen**

**Abstrakte Base Class:**
```python
class Connector:
    def connect()           # Verbindung aufbauen
    def get_schema()        # Alle Tabellen auflisten
    def get_table(table)    # Spalten einer Tabelle
    def get_column(table, column)  # Spalten-Details
```

#### **MySQLConnector Implementation**

```python
class MysqlConnector(Connector):

    def get_schema():
        # SQL: SHOW TABLES
        # Gibt zurück: Schema(database_name, [table1, table2, ...])

    def get_table(table):
        # SQL: SHOW COLUMNS FROM `table`
        # Gibt zurück: Table(name, type="flat", [col1, col2, ...])

    def get_column(table, column):
        # SQL: SELECT ... FROM INFORMATION_SCHEMA.COLUMNS
        # Gibt zurück: Column(name, type, nullable, key, default, length)
        # Mit Error-Handling wenn Column nicht existiert
```

**Parameterisierte Queries (SQL Injection Protection):**
```python
# SICHER: Parameter werden escaped
query = "SELECT ... WHERE table_name = %s AND table_schema = %s"
cursor.execute(query, (table, database))

# Identifiers mit Backticks:
"SHOW COLUMNS FROM `%s`" % table
```

---

### 4️⃣ **Datenmodelle: `database/schema.py`, `table.py`, `column.py`**

**Schema** → Repräsentation einer kompletten Datenbank
```python
Schema:
  - name: "classicmodels"
  - table_names: ["customers", "orders", "products", ...]
  - tables: {  # Dict mit Table-Objekten
      "customers": Table(...),
      "orders": Table(...),
      ...
    }
```

**Table** → Repräsentation einer Tabelle
```python
Table:
  - name: "customers"
  - type: "flat"
  - column_names: ["customerNumber", "customerName", ...]
  - columns: {  # Dict mit Column-Objekten
      "customerNumber": Column(...),
      "customerName": Column(...),
      ...
    }
```

**Column** → Repräsentation einer Spalte
```python
Column:
  - name: "customerNumber"
  - type: "INT"
  - nullable: False
  - key: "PRI"  # PRI=Primary Key, MUL=Multiple, UNI=Unique
  - default: None
  - length: 11
  - ref_to: []      # Foreign Keys die HIERHER verweisen
  - ref_from: []    # Foreign Keys die VON HIER wegverweisen
```

**Reference** → Foreign Key Beziehung
```python
Reference(ref_schema, ref_table, ref_column)
# Beispiel: customers.customerNumber → orders.customerNumber
```

---

### 5️⃣ **Parsing: `analyzer/parser.py`**

**Rolle:** Traversiert das Datenbankschema und füllt die Datenmodelle

```python
class Parser:
    def parse(connector):
        1. connector.get_schema() aufrufen
        2. Für jede Tabelle:
           a. connector.get_table(table_name) aufrufen
           b. Für jede Spalte:
              - connector.get_column(table, column) aufrufen
              - Column-Objekt in table.columns speichern
           c. Table-Objekt in schema.tables speichern
        3. Vollständiges Schema zurückgeben

        Ausgabe: vollständig gefülltes Schema-Objekt
```

---

### 6️⃣ **Code-Generation: `generator/coordinator.py`**

**Rolle:** Rendert Mako-Templates mit Schema-Daten

**Template Modi:**

| Modus | Zweck |
|-------|-------|
| `schema` | Template wird 1x pro Schema/Datenbankverbindung ausgeführt |
| `table` | Template wird 1x pro Tabelle ausgeführt |

**Beispiel aus `model.py.template`:**
```
## modus: table
## modus: schema
#!/usr/bin/env python
class ${underscored(table_name+" Model")}(Model):
    row=[]
```

**Koordinator Ablauf:**
```python
def generate():
    for template in config['output']:
        1. Template-Datei laden
        2. "modus: schema" oder "modus: table" auslesen

        if modus == "schema":
            # Einmal pro Datenbankverbindung
            for connection in config['connections']:
                schema = connection["parsedSchema"]
                result = template.render(schema=schema)
                print(result)  # oder in Datei schreiben

        elif modus == "table":
            # Einmal pro Tabelle
            for connection in config['connections']:
                schema = connection["parsedSchema"]
                for table_name in schema.table_names:
                    ctx = Context(
                        table=schema.tables[table_name],
                        table_name=table_name,
                        underscored=underscored,  # Utility-Funktionen
                        camel_case=camel_case
                    )
                    result = template.render_context(ctx)
                    print(result)  # oder in Datei schreiben
```

**Template-Utilities:**
```python
def underscored(text):     # "User Name" → "user_name"
def camel_case(text):       # "user name" → "UserName"
```

---

## 📝 Fehlerbehandlung & Logging

### Logging-Levels
```python
import logging
logger = logging.getLogger(__name__)

logger.info()    # Normale Meldungen
logger.debug()   # Debug-Infos
logger.error()   # Fehler mit Stacktrace
logger.warning() # Warnungen
```

### Error-Handling Punkte

| Stelle | Fehlertyp | Handling |
|--------|-----------|----------|
| YAML-Parsing | `FileNotFoundError`, `YAMLError` | Exit mit Fehlercode 1 |
| DB-Connection | `mysql.connector.Error` | Logged und re-raised |
| Connector-Loading | `ImportError`, `AttributeError` | Caught und gemeldet |
| Column nicht found | `ValueError` | Raised mit Meldung |

---

## 🔌 Connector-Pattern (Factory)

**Dynamisches Laden von Connector-Klassen:**

```python
# config: "database.mysqlconnector.MysqlConnector"
# Split in: ["database", "mysqlconnector", "MysqlConnector"]

package = "pystoorm.database.mysqlconnector"  # oder "database.mysqlconnector"
module_name = "MysqlConnector"

lib = importlib.import_module(package)        # Import durchführen
connector_class = getattr(lib, module_name)   # Klasse holen
connector = connector_class()                 # Instanz erzeugen
```

**Vorteile:**
- Neue DB-Systeme ohne Code-Änderung hinzufügbar
- Konfigurationsbasiert
- Pluggable Architecture

---

## 🧪 Testing

**Unit Tests in `tests/test_basic.py`:**

```python
TestSchema:
  - test_schema_initialization()       # Konstruktor funktioniert
  - test_schema_mutable_defaults()     # Keine shared dicts

TestTable:
  - test_table_initialization()        # Konstruktor funktioniert
  - test_table_mutable_defaults()      # Keine shared dicts

TestColumn:
  - test_column_initialization()       # Konstruktor funktioniert
  - test_column_references()           # Referenzen funktionieren
```

**Tests ausführen:**
```bash
python3 -m pytest tests/test_basic.py -v
```

---

## ⚙️ Konfiguration

### `bootstrap.yml` (global)
```yaml
connections:
  - # wird durch project.yml ergänzt

name: Harald Stowasser
logLevel: WARN

output:
  - from: ./templates/python/model.py.template
    to: ${project}/orm/model/[table].py
  - from: ./templates/python/repository.py.template
  - from: ./templates/erd/graphviz.template
    to: ${project}/graphviz.dot
```

### `project.yml` (projektspezifisch)
```yaml
connections:
  - connection: classicmodels
    host: 127.0.0.1
    username: pystoorm
    password: pystoormpw
    database: classicmodels
    connector: database.mysqlconnector.MysqlConnector
    # Optional:
    port: 3306
    passfile: ~/.mysql/pass

project: ../tests/sampleproject
```

---

## 🚀 Verwendungsbeispiel

```bash
# Szenario: ORM-Code für MySQL-Datenbank generieren

cd pystoorm
python3 pystoorm.py ../tests/sampleproject/project.yml

# Prozess:
# 1. bootstrap.yml + project.yml laden → config
# 2. MysqlConnector instanziieren
# 3. Mit classicmodels DB verbinden
# 4. Schema auslesen: [customers, orders, products, ...]
# 5. Jede Tabelle analysieren: Spalten, Types, Keys
# 6. Templates rendern:
#    - Für jede Tabelle: model.py generieren
#    - Für jede Tabelle: repository.py generieren
#    - Für Schema: erd/graphviz.dot generieren
# 7. Output: Python-ORM-Klassen
```

---

## 🛡️ Security Features

1. **SQL Injection Protection**
   - Parameterisierte Queries: `cursor.execute(query, params)`
   - Identifier mit Backticks

2. **Connection Pooling**
   - Lazy connection (nur bei Bedarf)
   - Cursor wird mit `close()` freigegeben

3. **Error Propagation**
   - Keine sensitive Daten in Logs
   - Exceptions werden weitergeleitet

---

## 📦 Dependencies

| Paket | Version | Zweck |
|-------|---------|-------|
| clint | >=0.5.1 | CLI-Ausgabe (colored text) |
| mysql-connector-python | >=8.0.33 | MySQL-Verbindung |
| PyYAML | >=6.0 | YAML-Parsing |
| Mako | >=1.2.4 | Template-Engine |

---

## 🎯 Zusammenfassung

**pyStoOrm ist ein 4-Schichten-System:**

1. **Config-Layer**: YAML Dateien laden
2. **Analysis-Layer**: Controller + Parser untersuchen DB
3. **Data-Layer**: Schema/Table/Column Modelle speichern Metadaten
4. **Generation-Layer**: Coordinator rendert Templates

**Der Kerngedanke**: Externe Datenbank → Interne Datenstruktur → Code-Templates → Python-ORM-Code
