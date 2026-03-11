#!/usr/bin/env python3
"""Run tests with print output. Use if pytest is not installed."""

import sys

sys.path.insert(0, ".")
import tests.test_order_book as t

for name in dir(t):
    if name.startswith("test_"):
        getattr(t, name)()
        print(f"  ✓ {name}")

print("\nAll tests passed!")
