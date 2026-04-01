#!/bin/bash

# Test API Script
# Tests the REST API endpoints

API="http://localhost:3000"
echo "======================================================================="
echo "  pyStoOrm REST API Tests"
echo "======================================================================="
echo ""

# Health check
echo "[1] Health Check"
curl -s "${API}/health" | python3 -m json.tool
echo ""

# Get all customers
echo "[2] GET /api/customers (all)"
curl -s "${API}/api/customers" | python3 -m json.tool || echo "Server not running"
echo ""

# Get customer by ID
echo "[3] GET /api/customers/103"
curl -s "${API}/api/customers/103" | python3 -m json.tool || echo "Server not running"
echo ""

# Create new customer
echo "[4] POST /api/customers"
curl -s -X POST "${API}/api/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "customername": "Tech Innovations Ltd",
    "contactlastname": "Johnson",
    "contactfirstname": "Alice",
    "phone": "555-0123",
    "addressline1": "123 Tech Park",
    "city": "San Francisco",
    "state": "CA",
    "country": "USA",
    "creditlimit": 50000
  }' | python3 -m json.tool || echo "Server not running"
echo ""

# Get all orders
echo "[5] GET /api/orders"
curl -s "${API}/api/orders" | python3 -m json.tool | head -30 || echo "Server not running"
echo ""

# Get all products
echo "[6] GET /api/products"
curl -s "${API}/api/products" | python3 -m json.tool | head -30 || echo "Server not running"
echo ""
