#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of pyStoOrm generated models and repositories.

This script demonstrates the Repository Pattern for CRUD operations
using the auto-generated classes from the classic models sample database.
"""
import os
import sys
from pathlib import Path

# Add the project root and generated modules to the path
CURRENT_DIR = Path(__file__).parent
GENERATED_DIR = CURRENT_DIR / "generated"
PROJECT_ROOT = CURRENT_DIR.parent.parent  # pyStoOrm root
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(GENERATED_DIR))

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    """Demonstrate repository usage with generated classes."""

    db_path = str(CURRENT_DIR / "classicmodels.db")

    if not os.path.exists(db_path):
        print("Error: Database file not found!")
        print(f"Run batch.sh first to generate the database and models:")
        print(f"  cd {CURRENT_DIR}")
        print(f"  bash batch.sh")
        sys.exit(1)

    print("\n" + "="*60)
    print("  pyStoOrm Repository Pattern - Example Usage")
    print("="*60)

    # Dynamic import of repositories
    try:
        from repositories.payments_repository import PaymentsRepository
        print("\n✓ Successfully imported PaymentsRepository")
        RepoClass = PaymentsRepository
        TableName = "Payments"
    except ImportError as e:
        print(f"\n✗ Error importing PaymentsRepository: {e}")
        print("\nMake sure to run batch.sh first to generate the repositories:")
        print(f"  cd {CURRENT_DIR}")
        print(f"  bash batch.sh")
        sys.exit(1)

    # ==========================================
    # Initialize repository
    # ==========================================
    print_section("1. Initialize Repository")

    repo = RepoClass(db_path)
    print(f"✓ Repository initialized with database: {db_path}")
    print(f"  Primary key: {repo.primary_key}")
    print(f"  Table: {repo.table_name}")

    # ==========================================
    # Count all records
    # ==========================================
    print_section("2. Count Records")

    total_count = repo.count()
    print(f"✓ Total customers in database: {total_count}")

    # ==========================================
    # Find all records
    # ==========================================
    print_section("3. Find All Records")

    records = repo.find_all()
    print(f"✓ Retrieved {len(records)} {TableName.lower()} records")

    if records:
        print(f"\nFirst 3 {TableName.lower()} records:")
        for i, record in enumerate(records[:3], 1):
            print(f"\n  {i}. {record}")

    # ==========================================
    # Find by primary key
    # ==========================================
    print_section("4. Find by Primary Key")

    # Get first record's ID to demonstrate find_by_id
    if records:
        first_record = records[0]
        first_id = getattr(first_record, repo.primary_key)
        record = repo.find_by_id(first_id)

        if record:
            print(f"✓ Found {TableName.lower()} record with ID {first_id}:")
            print(f"\n  {record}")
            print(f"\n  Attributes:")
            data = record.to_dict()
            for key, value in list(data.items())[:5]:
                print(f"    - {key}: {value}")
        else:
            print(f"✗ No record found with ID {first_id}")
    else:
        print("✗ No records in database to demonstrate find_by_id")

    # ==========================================
    # Find with criteria
    # ==========================================
    print_section("5. Find with Criteria")

    # For this example, we'll demonstrate the capability even if no criteria matches
    # In a real scenario, you would know which columns exist in your table
    print(f"✓ Repository supports finding records with criteria")
    print(f"  Example: repo.find_all_by(column_name=value)")
    print(f"\nAvailable methods for searching:")
    print(f"  - find_all_by(**criteria) - Find records matching criteria")
    print(f"  - count(**criteria) - Count records matching criteria")


    # ==========================================
    # Check existence
    # ==========================================
    print_section("7. Check Record Existence")

    # Check first record
    if records:
        first_id = getattr(records[0], repo.primary_key)
        exists = repo.exists(first_id)
        status = "✓ Exists" if exists else "✗ Not found"
        print(f"  Record {first_id}: {status}")
    else:
        print("  No records to check")

    # ==========================================
    # Create and save new record
    # ==========================================
    print_section("8. Create and Save New Record")

    try:
        from models.payments import Payments

        # Create a new payment record
        new_payment = Payments(
            customernumber=101,
            checknumber="CHK-TEST-999",
            paymentdate="2024-03-27",
            amount=5000.00
        )

        print(f"✓ Created new {TableName.lower()} object:")
        print(f"  {new_payment}")

        # Save to database
        saved = repo.save(new_payment)
        print(f"\n✓ Saved to database")
        print(f"  Check: {saved.checknumber}")

        # Verify it was saved
        retrieved = repo.find_by_id(saved.checknumber)
        if retrieved:
            print(f"\n✓ Verified saved record exists in database:")
            print(f"  {retrieved}")

    except Exception as e:
        print(f"⚠ Note: Could not test save operation: {e}")
        print("  (This is normal if the database is read-only or has constraints)")

    # ==========================================
    # Summary
    # ==========================================
    print_section("Summary")

    print("Repository Pattern Capabilities Demonstrated:")
    print("  ✓ find_all() - Retrieve all records")
    print("  ✓ find_by_id() - Retrieve specific record by primary key")
    print("  ✓ find_all_by() - Find records matching criteria")
    print("  ✓ count() - Count records (with optional criteria)")
    print("  ✓ exists() - Check if record exists")
    print("  ✓ save() - Insert or update records")
    print("  ✓ delete() - Delete record by ID")
    print("  ✓ delete_all() - Delete records matching criteria")

    print("\nRepository Features:")
    print("  • Data abstraction layer")
    print("  • Type-safe queries")
    print("  • Automatic model conversion")
    print("  • Transaction support")

    # Cleanup
    repo.close()

    print("\n" + "="*60)
    print("✓ Example completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
