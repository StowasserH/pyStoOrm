#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: pyStoOrm Repository Pattern

This demonstrates the Repository Pattern with proper encapsulation:
- Models are accessed only via properties (getters/setters)
- Repositories return individual model objects (not arrays)
- Models track whether they have been modified (dirty flag)
- Models have a unique identifier even before persisting
"""
import os
import sys
from pathlib import Path

# Setup paths
CURRENT_DIR = Path(__file__).parent
GENERATED_DIR = CURRENT_DIR / "generated"
sys.path.insert(0, str(GENERATED_DIR))


def main():
    db_path = str(CURRENT_DIR / "classicmodels.db")

    # Check database exists
    if not os.path.exists(db_path):
        print("Error: Database not found!")
        print("Run batch.sh first:")
        print(f"  cd {CURRENT_DIR} && bash batch.sh")
        sys.exit(1)

    print("\n" + "="*70)
    print("  pyStoOrm - Repository Pattern Example")
    print("="*70)

    # ==========================================
    # [1] Customers Repository - find_by_id()
    # ==========================================
    print("\n[1] Find a Customer by ID")
    print("-" * 70)

    from repositories.customers_repository import CustomersRepository

    customers_repo = CustomersRepository(db_path)
    customer = customers_repo.find_by_id(103)

    if customer:
        print(f"Customer found: {customer}")
        print(f"  ID: {customer.get_id()}")
        print(f"  Name: {customer.contactfirstname} {customer.contactlastname}")
        print(f"  City: {customer.city}")
        print(f"  Country: {customer.country}")
        print(f"  Is modified: {customer.is_dirty}")
    else:
        print("Customer not found")


    # ==========================================
    # [2] Modify a Model - Dirty Flag
    # ==========================================
    print("\n[2] Modify a Model (Dirty Flag)")
    print("-" * 70)

    if customer:
        print(f"Before: {customer}")
        print(f"Modified: {customer.is_dirty}")

        # Modify via property setter
        customer.city = "São Paulo"
        customer.country = "Brazil"

        print(f"After:  {customer}")
        print(f"Modified: {customer.is_dirty}")
        print(f"Changed columns: {customer.modified_columns}")


    # ==========================================
    # [3] Customers Repository - find_all() as Generator
    # ==========================================
    print("\n[3] Find All Customers (Generator)")
    print("-" * 70)

    total = customers_repo.count()
    print(f"Total customers: {total}")
    print(f"\nFirst 3 customers (lazy loaded):")

    for i, cust in enumerate(customers_repo.find_all()):
        if i >= 3:
            break
        print(f"  {i+1}. {cust}")
        print(f"     Country: {cust.country}")


    # ==========================================
    # [4] Find with Criteria
    # ==========================================
    print("\n[4] Find Customers by Criteria")
    print("-" * 70)

    us_count = 0
    print("Customers from USA:")
    for cust in customers_repo.find(country='USA'):
        print(f"  • {cust}")
        us_count += 1
        if us_count >= 3:
            break

    print(f"\nTotal USA customers: {customers_repo.count(country='USA')}")


    # ==========================================
    # [5] Orders Repository - Individual Objects
    # ==========================================
    print("\n[5] Orders Repository")
    print("-" * 70)

    from repositories.orders_repository import OrdersRepository

    orders_repo = OrdersRepository(db_path)

    # Find specific order
    order = orders_repo.find_by_id(10100)
    if order:
        print(f"Order found: {order}")
        print(f"  ID: {order.get_id()}")
        print(f"  Customer: {order.customernumber}")
        print(f"  Order Date: {order.orderdate}")
        print(f"  Required Date: {order.requireddate}")
        print(f"  Is modified: {order.is_dirty}")


    # ==========================================
    # [6] Model without Database ID - Hidden ID
    # ==========================================
    print("\n[6] New Model - Hidden ID (not yet persisted)")
    print("-" * 70)

    from models.orders import Orders

    # Create new order (not in database yet)
    new_order = Orders()
    new_order.customernumber = 999
    new_order.orderdate = "2024-03-27"
    new_order.requireddate = "2024-04-10"
    new_order.shippeddate = None
    new_order.status = "In Process"
    new_order.comments = "Test order"

    print(f"New order: {new_order}")
    print(f"  ID (hidden): {new_order.get_id()}")
    print(f"  Modified: {new_order.is_dirty}")
    print(f"  Modified columns: {new_order.modified_columns}")

    # Convert to dict
    order_dict = new_order.to_dict()
    print(f"\nAs dictionary:")
    for key, value in order_dict.items():
        print(f"  {key}: {value}")


    # ==========================================
    # [7] Products Repository
    # ==========================================
    print("\n[7] Products Repository")
    print("-" * 70)

    from repositories.products_repository import ProductsRepository

    products_repo = ProductsRepository(db_path)

    print(f"Total products: {products_repo.count()}")
    print("\nFirst 5 products:")

    for i, product in enumerate(products_repo.find_all()):
        if i >= 5:
            break
        print(f"  {product}")


    # ==========================================
    # Summary - Repository Pattern
    # ==========================================
    print("\n[8] Repository Pattern Features")
    print("-" * 70)

    print("✓ Models are accessed only via properties (getters/setters)")
    print("✓ Repositories return individual objects (not arrays)")
    print("✓ find_all() returns a generator (lazy loading)")
    print("✓ Models track changes with _dirty flag")
    print("✓ Models have get_id() - database ID or hidden UUID")
    print("✓ New models get a hidden ID until persisted")
    print("✓ Modified columns tracked via modified_columns dict")
    print("✓ to_dict() converts model to dictionary")
    print("✓ __str__() shows 'attitude' (key descriptor)")
    print("✓ __repr__() shows attitude + ID + modification status")


    # Cleanup
    customers_repo.close()
    orders_repo.close()
    products_repo.close()

    print("\n" + "="*70)
    print("✓ Example completed")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
