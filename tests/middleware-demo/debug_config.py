#!/usr/bin/env python3
"""Debug script to show what config pyStoOrm reads"""

import sys
import yaml
sys.path.insert(0, '/home/stowasserh/Nextcloud/share/work/pyStoOrm')

print("=" * 70)
print("DEBUG: Loading project.yml")
print("=" * 70)

# Load YAML
with open('project.yml') as f:
    raw_config = yaml.safe_load(f)

print("\nRaw YAML content:")
print(yaml.dump(raw_config, default_flow_style=False))

print("\n" + "=" * 70)
print("Connection config that will be used:")
print("=" * 70)

if 'connections' in raw_config:
    for conn in raw_config['connections']:
        print(f"\nConnection: {conn.get('connection')}")
        print(f"  Connector: {conn.get('connector')}")
        print(f"  Host: {conn.get('host')}")
        print(f"  Port: {conn.get('port')}")
        print(f"  Database: {conn.get('database')}")
        print(f"  User: {conn.get('user')}")

print("\n" + "=" * 70)
print("Now trying to instantiate PostgresqlConnector...")
print("=" * 70)

from pystoorm.database.postgresqlconnector import PostgresqlConnector

config = raw_config['connections'][0]
conn = PostgresqlConnector(config)

print(f"\nPostgresqlConnector args that will be used:")
for k, v in conn.args.items():
    print(f"  {k}: {v}")

print("\nDone!")
