"""
Pytest configuration - Makes pystoorm module importable for tests.
"""
import sys
import os

# Add parent directory to sys.path so pystoorm can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
