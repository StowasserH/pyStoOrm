#!/usr/bin/env python3
"""
Create SQLite database with Classic Models schema and sample data.
Run: python create_db.py
"""

import sqlite3
import os

DB_FILE = 'classicmodels.db'

# SQL schema (adapted for SQLite)
SCHEMA = """
CREATE TABLE IF NOT EXISTS productlines (
    productLine VARCHAR(50) PRIMARY KEY,
    textDescription VARCHAR(4000),
    htmlDescription TEXT,
    image BLOB
);

CREATE TABLE IF NOT EXISTS products (
    productCode VARCHAR(15) PRIMARY KEY,
    productName VARCHAR(70) NOT NULL,
    productLine VARCHAR(50) NOT NULL,
    productScale VARCHAR(10) NOT NULL,
    productVendor VARCHAR(50) NOT NULL,
    productDescription TEXT NOT NULL,
    quantityInStock INTEGER NOT NULL,
    buyPrice REAL NOT NULL,
    MSRP REAL,
    FOREIGN KEY (productLine) REFERENCES productlines(productLine)
);

CREATE TABLE IF NOT EXISTS customers (
    customerNumber INTEGER PRIMARY KEY,
    customerName VARCHAR(50) NOT NULL,
    contactLastName VARCHAR(50) NOT NULL,
    contactFirstName VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    addressLine1 VARCHAR(50) NOT NULL,
    addressLine2 VARCHAR(50),
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50),
    postalCode VARCHAR(15),
    country VARCHAR(50) NOT NULL,
    salesRepEmployeeNumber INTEGER,
    creditLimit REAL
);

CREATE TABLE IF NOT EXISTS orders (
    orderNumber INTEGER PRIMARY KEY,
    orderDate DATE NOT NULL,
    requiredDate DATE NOT NULL,
    shippedDate DATE,
    status VARCHAR(15) NOT NULL,
    comments TEXT,
    customerNumber INTEGER NOT NULL,
    FOREIGN KEY (customerNumber) REFERENCES customers(customerNumber)
);

CREATE TABLE IF NOT EXISTS orderdetails (
    orderNumber INTEGER NOT NULL,
    productCode VARCHAR(15) NOT NULL,
    quantityOrdered INTEGER NOT NULL,
    priceEach REAL NOT NULL,
    orderLineNumber INTEGER NOT NULL,
    PRIMARY KEY (orderNumber, productCode),
    FOREIGN KEY (orderNumber) REFERENCES orders(orderNumber),
    FOREIGN KEY (productCode) REFERENCES products(productCode)
);

CREATE TABLE IF NOT EXISTS employees (
    employeeNumber INTEGER PRIMARY KEY,
    lastName VARCHAR(50) NOT NULL,
    firstName VARCHAR(50) NOT NULL,
    extension VARCHAR(10),
    email VARCHAR(100),
    officeCode VARCHAR(10),
    reportsTo INTEGER,
    jobTitle VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS offices (
    officeCode VARCHAR(10) PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    addressLine1 VARCHAR(50) NOT NULL,
    addressLine2 VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) NOT NULL,
    postalCode VARCHAR(15),
    territory VARCHAR(10)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country);
CREATE INDEX IF NOT EXISTS idx_customers_city ON customers(city);
CREATE INDEX IF NOT EXISTS idx_customers_salesRep ON customers(salesRepEmployeeNumber);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customerNumber);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orderdetails_product ON orderdetails(productCode);
CREATE INDEX IF NOT EXISTS idx_products_line ON products(productLine);
"""

# Sample data
DATA = """
INSERT OR IGNORE INTO offices VALUES
('1', 'San Francisco', '+1 650 219 4782', '100 Market Street', NULL, 'CA', 'USA', '94105', 'NA'),
('2', 'Boston', '+1 617 723 4200', '51 Atlantic Avenue', NULL, 'MA', 'USA', '02110', 'NA'),
('3', 'NYC', '+1 212 555 3000', 'Madison Avenue 1', NULL, 'NY', 'USA', '10001', 'NA'),
('4', 'Paris', '+33 1 46 62 47 40', '29 Rue Lalou', NULL, NULL, 'France', '75002', 'EMEA'),
('5', 'Tokyo', '+81 33 224 5000', '4-1 Kioicho', NULL, NULL, 'Japan', '100-8488', 'Japan'),
('6', 'Sydney', '+61 2 9264 2451', '5 Dale Street', NULL, NULL, 'Australia', '2010', 'APAC');

INSERT OR IGNORE INTO employees VALUES
(1002, 'Murphy', 'Diane', 'x5800', 'diane@company.com', '1', NULL, 'President'),
(1056, 'Patterson', 'Mary', 'x4611', 'mary@company.com', '1', 1002, 'VP Sales'),
(1076, 'Firrelli', 'Jeff', 'x9273', 'jeff@company.com', '1', 1002, 'VP Marketing'),
(1088, 'Patterson', 'William', 'x4871', 'william@company.com', '6', 1076, 'Sales Rep'),
(1102, 'Bondur', 'Gerhard', 'x3087', 'gerhard@company.com', '4', 1056, 'Sales Rep'),
(1143, 'Bow', 'Anthony', 'x5428', 'anthony@company.com', '1', 1056, 'Sales Rep'),
(1165, 'Jennings', 'Leslie', 'x3291', 'leslie@company.com', '1', 1143, 'Sales Rep'),
(1166, 'Thompson', 'Leslie', 'x4065', 'thompson@company.com', '1', 1143, 'Sales Rep');

INSERT OR IGNORE INTO productlines VALUES
('Classic Cars', 'Attention car enthusiasts: Make your wildest car ownership dreams come true.', NULL, NULL),
('Motorcycles', 'Our motorcycles are state of the art machines.', NULL, NULL),
('Planes', 'Unique, diecast airplane and helicopter replicas suitable for collections.', NULL, NULL),
('Ships', 'The perfect holiday or anniversary gift for model ship enthusiasts.', NULL, NULL),
('Trains', 'Model trains with amazing detail.', NULL, NULL),
('Trucks and Buses', 'The latest model trucks and buses as well as farm vehicles.', NULL, NULL);

INSERT OR IGNORE INTO products VALUES
('S10_1678', '1969 Harley Davidson Ultimate Chopper', 'Motorcycles', '1:10', 'Min Lin Diecast', 'This replica features working kickstand.', 7933, 48.81, 95.70),
('S10_1949', '1952 Alpine Renault 1300', 'Classic Cars', '1:10', 'Classic Metal Creations', 'Turnable front wheels; steering function.', 7305, 98.30, 214.30),
('S10_2016', '1996 Moto Guzzi 1100i', 'Motorcycles', '1:10', 'Highway 66 Mini Classics', 'Official Moto Guzzi logos and details.', 6625, 68.99, 118.94),
('S10_4757', '1972 Alfa Romeo GTA', 'Classic Cars', '1:10', 'Motor City Art Classics', 'Features include: Turnable front wheels.', 3252, 85.68, 176.56),
('S10_4962', '1962 Lancia Delta 16V', 'Classic Cars', '1:10', 'Classic Metal Creations', 'Features include: Turnable front wheels.', 8875, 103.42, 207.80),
('S12_1099', '1968 Ford Mustang', 'Classic Cars', '1:12', 'Autoart Studio Design', 'Hood, doors and trunk all open.', 68, 68.99, 101.51),
('S12_1108', '2001 Ferrari Enzo', 'Classic Cars', '1:12', 'Hot Wheels', 'Turnable front wheels; steering function.', 3828, 95.59, 207.80);

INSERT OR IGNORE INTO customers VALUES
(103, 'Atelier graphique', 'Schmitt', 'Carine', '40.32.2555', '54 rue Royale', NULL, 'Nantes', NULL, '44000', 'France', 1370, 21000.00),
(112, 'Signal Gift Stores', 'King', 'Jean', '7025551838', '2560 Boulevard of Broken Dreams', NULL, 'New York', 'NY', '10103', 'USA', 1166, 71800.00),
(114, 'Australian Collectors, Co.', 'Ferguson', 'Peter', '03 9520 4555', '636 St Kilda Road', 'Level 3', 'Melbourne', 'Victoria', '3004', 'Australia', 1611, 117300.00),
(119, 'La Rochelle Gifts', 'Labrune', 'Janine', '40.67.8555', '67 rue des Cinquante Otages', NULL, 'Nantes', NULL, '44000', 'France', 1370, 118400.00),
(121, 'Baane Mini Imports', 'Bergulfsen', 'Jonas', '07-98 9555', 'Erling Skakkes gate 78', NULL, 'Stavern', NULL, '4110', 'Norway', 1504, 81700.00),
(124, 'Mini Gifts Distributors Ltd.', 'Nelson', 'Susan', '4155551450', '4575 Hillside Drive', NULL, 'Santa Cruz', 'CA', '97815', 'USA', 1165, 210500.00);

INSERT OR IGNORE INTO orders VALUES
(10100, '2023-01-06', '2023-01-13', '2023-01-10', 'Shipped', NULL, 103),
(10101, '2023-01-09', '2023-01-18', '2023-01-11', 'Shipped', NULL, 112),
(10102, '2023-01-10', '2023-01-18', '2023-01-14', 'Shipped', 'This order was cancelled', 121),
(10103, '2023-01-29', '2023-02-07', '2023-02-12', 'Shipped', NULL, 114),
(10104, '2023-01-31', '2023-02-09', '2023-03-30', 'Shipped', 'Autoart and Metal Classics shipment', 124);

INSERT OR IGNORE INTO orderdetails VALUES
(10100, 'S10_1678', 30, 95.70, 1),
(10100, 'S12_1108', 50, 100.00, 2),
(10101, 'S10_1949', 22, 214.30, 1),
(10102, 'S10_4962', 45, 207.80, 1),
(10103, 'S10_2016', 36, 118.94, 1),
(10104, 'S10_1678', 28, 95.70, 1),
(10104, 'S10_4757', 16, 176.56, 2);
"""

def main():
    # Remove old database if exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"✓ Removed old {DB_FILE}")

    # Create new database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Execute schema
    for statement in SCHEMA.split(';'):
        if statement.strip():
            cursor.execute(statement)

    # Execute data inserts
    for statement in DATA.split(';'):
        if statement.strip():
            try:
                cursor.execute(statement)
            except sqlite3.IntegrityError:
                pass  # Ignore duplicate inserts

    conn.commit()
    conn.close()

    print(f"✓ Created {DB_FILE} with sample data")
    print(f"✓ Tables: customers, orders, products, productlines, employees, offices, orderdetails")
    print(f"\nYou can now run: npm run generate")

if __name__ == '__main__':
    main()
