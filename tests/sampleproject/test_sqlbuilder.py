#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test SQLBuilder - Demonstrating custom SQL queries with generated SQL metadata.

This script shows how to use the SQLBuilder for advanced queries:
1. Access SQL metadata constants
2. Build custom SQL with fragments
3. Create models from JOIN results
"""
import sys
from pathlib import Path

# Add the project root and generated modules to the path
CURRENT_DIR = Path(__file__).parent
GENERATED_DIR = CURRENT_DIR / "generated"
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(GENERATED_DIR))

# Import repositories and builders
from repositories.customers_repository import CustomersRepository
from repositories.orders_repository import OrdersRepository
from repositories.payments_repository import PaymentsRepository

from builders.customers_builder import CustomersBuilder
from builders.orders_builder import OrdersBuilder
from builders.payments_builder import PaymentsBuilder


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def main():
    """Demonstrate SQLBuilder usage."""

    db_path = str(CURRENT_DIR / "classicmodels.db")

    print("\n" + "="*70)
    print("  pyStoOrm SQLBuilder - Custom Query Examples")
    print("="*70)

    # ==========================================
    # 1. Access SQL Metadata
    # ==========================================
    print_section("1. SQL Metadata Constants")

    print(f"Customers table metadata:")
    print(f"  TABLE: {CustomersRepository.SQL_TABLE}")
    print(f"  ALIAS: {CustomersRepository.SQL_ALIAS}")
    print(f"  PK: {CustomersRepository.SQL_PK}")
    print(f"  COLS: {CustomersRepository.SQL_COLS}")
    print(f"  TYPES: {CustomersRepository.SQL_TYPES}")
    print(f"  IDX: {CustomersRepository.SQL_IDX}")

    # ==========================================
    # 2. Use SQL Fragment Builders
    # ==========================================
    print_section("2. SQL Fragment Builders")

    select_clause = CustomersBuilder.select('c')
    print(f"SELECT fragment: {select_clause}")

    where_pk = CustomersBuilder.where_pk('c')
    print(f"WHERE PK fragment: {where_pk}")

    table = CustomersBuilder.table()
    print(f"Table name: {table}")

    col_count = CustomersBuilder.column_count()
    print(f"Column count: {col_count}")

    # ==========================================
    # 3. Build Custom JOIN Query
    # ==========================================
    print_section("3. Custom JOIN Query using SQL Fragments")

    # Build the query using generated fragments
    query = f"""
    SELECT {CustomersBuilder.select('c')}, {OrdersBuilder.select('o')}
    FROM {CustomersRepository.SQL_TABLE} c
    LEFT JOIN {OrdersRepository.SQL_TABLE} o
        ON o.customerNumber = c.customerNumber
    WHERE c.country = ?
    ORDER BY c.customerNumber
    """

    print(f"Generated Query:")
    print(f"  {query}")

    # Execute custom query
    repo = CustomersRepository(db_path)
    cursor = repo.connection.cursor()
    cursor.execute(query, ['USA'])
    rows = cursor.fetchall()

    print(f"\n✓ Found {len(rows)} result rows for customers in USA with orders")

    if rows:
        # Extract data using SQLBuilder
        customers = {}
        for row in rows:
            # Customers table ends at column count
            cust_col_count = CustomersBuilder.column_count()
            order_col_count = OrdersBuilder.column_count()

            # Build objects from row slices
            if row[:cust_col_count][0] is not None:  # Customer exists
                customer = CustomersBuilder.from_row(row, 0, cust_col_count)
                cust_id = customer.customernumber

                if cust_id not in customers:
                    customers[cust_id] = customer
                    customers[cust_id].orders = []

                # Add order if it exists
                if row[cust_col_count] is not None:  # Order number exists
                    order = OrdersBuilder.from_row(row, cust_col_count, cust_col_count + order_col_count)
                    customers[cust_id].orders.append(order)

        print(f"\nParsed into objects:")
        for cust_id, customer in list(customers.items())[:3]:
            print(f"\n  Customer: {customer.customername} (ID: {cust_id})")
            print(f"  Contact: {customer.contactfirstname} {customer.contactlastname}")
            print(f"  Orders: {len(customer.orders)}")
            for order in customer.orders[:2]:
                print(f"    - Order #{order.ordernumber} ({order.orderdate})")

    # ==========================================
    # 4. Batch Row Conversion
    # ==========================================
    print_section("4. Batch Row Conversion")

    # Simple query to get multiple payments
    query = f"SELECT * FROM {PaymentsRepository.SQL_TABLE} LIMIT 5"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Convert all rows at once
    payments = PaymentsBuilder.from_rows(rows)
    print(f"✓ Converted {len(payments)} rows to Payment objects")

    for i, payment in enumerate(payments, 1):
        print(f"  {i}. Payment {payment.checknumber}: ${payment.amount:.2f} (Customer: {payment.customernumber})")

    # ==========================================
    # 5. Batch by Key
    # ==========================================
    print_section("5. Batch Rows by Primary Key")

    query = f"SELECT * FROM {PaymentsRepository.SQL_TABLE} LIMIT 20"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Group by customer number
    payments_by_customer = PaymentsBuilder.batch_from_rows(
        rows,
        key_func=lambda row: row[PaymentsRepository.SQL_IDX['customerNumber']]
    )

    print(f"✓ Grouped {len(rows)} payments by {len(payments_by_customer)} customers")

    for cust_id in list(payments_by_customer.keys())[:5]:
        payment = payments_by_customer[cust_id]
        print(f"  Customer {cust_id}: {payment.checknumber} (${payment.amount:.2f})")

    # ==========================================
    # 6. Type Information
    # ==========================================
    print_section("6. Type Information for Prepared Statements")

    types = PaymentsBuilder.types()
    col_types = PaymentsBuilder.column_types()

    print(f"Type string: {types}")
    print(f"Column types:")
    for col, type_char in col_types.items():
        type_name = {
            'i': 'INTEGER',
            's': 'STRING',
            'd': 'DECIMAL',
            'b': 'BOOLEAN'
        }.get(type_char, 'UNKNOWN')
        print(f"  {col}: {type_char} ({type_name})")

    # ==========================================
    # 7. SQL Fragment Methods
    # ==========================================
    print_section("7. SQL Fragment Helper Methods")

    print(f"sql_select(): {PaymentsRepository.sql_select('p')}")
    print(f"\nsql_insert_cols(): {PaymentsRepository.sql_insert_cols()}")
    print(f"\nsql_insert_placeholders(): {PaymentsRepository.sql_insert_placeholders()}")
    print(f"\nsql_update_set(): {PaymentsRepository.sql_update_set()}")
    print(f"\nsql_where_pk(): {PaymentsRepository.sql_where_pk()}")

    # Cleanup
    repo.close()

    print("\n" + "="*70)
    print("✓ SQLBuilder test completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
