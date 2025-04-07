#!/usr/bin/env python3
"""
Test runner for the Dating App AI Assistant.
Runs all unit and integration tests.
"""

import unittest
import sys
import os

def run_tests():
    """Run all tests and return the result."""
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return success if all tests passed
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    # Add the project root to the Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Run the tests
    sys.exit(run_tests())
