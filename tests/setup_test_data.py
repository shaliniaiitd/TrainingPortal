#!/usr/bin/env python
"""
Setup script for generating test data.
Run this once to create all test data in supported formats.

Usage:
    python setup_test_data.py
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from generate_test_data import generate_all_formats


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("TRAININGPORTAL TEST DATA SETUP")
    print("=" * 70 + "\n")

    try:
        generate_all_formats()
        print("\n" + "=" * 70)
        print("SETUP COMPLETE!")
        print("=" * 70)
        print("\n📝 Next steps:")
        print("   1. Start Django server: python manage.py runserver")
        print("   2. Run tests: pytest tests/ui/ -v")
        print("   3. View test data: cat tests/test_data/test_data.json\n")
        return 0
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
