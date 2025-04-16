#!/usr/bin/env python3
"""
Script to run the HypnoBot tests.
"""
import os
import sys
import argparse
import pytest

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the HypnoBot tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = []
    
    # Add verbosity
    if args.verbose:
        pytest_args.append('-v')
    
    # Add test type filter
    if args.unit:
        pytest_args.append('tests/unit')
    elif args.integration:
        pytest_args.append('tests/integration')
    else:
        pytest_args.append('tests')
    
    # Add coverage if requested
    if args.coverage:
        pytest_args = ['--cov=src', '--cov-report=term', '--cov-report=html'] + pytest_args
    
    print(f"Running tests with arguments: {' '.join(pytest_args)}")
    
    # Run pytest
    exit_code = pytest.main(pytest_args)
    
    # Exit with pytest exit code
    sys.exit(exit_code) 