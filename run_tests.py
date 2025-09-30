#!/usr/bin/env python3
"""
Test Runner Script

This script runs all tests for the Asthma Guardian v3 project.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def install_test_dependencies():
    """Install test dependencies."""
    print("Installing test dependencies...")
    return run_command(
        "pip install -r tests/requirements.txt",
        "Installing test dependencies"
    )


def run_unit_tests():
    """Run unit tests."""
    print("Running unit tests...")
    return run_command(
        "python -m pytest tests/infrastructure/ tests/backend/ -v --tb=short",
        "Unit tests"
    )


def run_frontend_tests():
    """Run frontend tests."""
    print("Running frontend tests...")
    os.chdir("frontend")
    success = run_command(
        "npm test -- --coverage --watchAll=false",
        "Frontend tests"
    )
    os.chdir("..")
    return success


def run_integration_tests():
    """Run integration tests."""
    print("Running integration tests...")
    return run_command(
        "python -m pytest tests/integration/ -v --tb=short -m integration",
        "Integration tests"
    )


def run_all_tests():
    """Run all tests."""
    print("Running all tests...")
    return run_command(
        "python -m pytest tests/ -v --tb=short --cov=. --cov-report=html --cov-report=term-missing",
        "All tests"
    )


def run_cdk_tests():
    """Run CDK-specific tests."""
    print("Running CDK tests...")
    return run_command(
        "cdk synth --quiet && echo 'CDK synthesis successful'",
        "CDK synthesis test"
    )


def generate_coverage_report():
    """Generate coverage report."""
    print("Generating coverage report...")
    return run_command(
        "python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=90",
        "Coverage report"
    )


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for Asthma Guardian v3")
    parser.add_argument(
        "--type",
        choices=["unit", "frontend", "integration", "all", "cdk", "coverage"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies before running tests"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Run tests in verbose mode"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(f"Running tests from: {os.getcwd()}")
    
    success = True
    
    # Install dependencies if requested
    if args.install_deps:
        success &= install_test_dependencies()
        if not success:
            print("Failed to install dependencies. Exiting.")
            sys.exit(1)
    
    # Run tests based on type
    if args.type == "unit":
        success &= run_unit_tests()
    elif args.type == "frontend":
        success &= run_frontend_tests()
    elif args.type == "integration":
        success &= run_integration_tests()
    elif args.type == "cdk":
        success &= run_cdk_tests()
    elif args.type == "coverage":
        success &= generate_coverage_report()
    elif args.type == "all":
        success &= run_unit_tests()
        success &= run_frontend_tests()
        success &= run_integration_tests()
        success &= run_cdk_tests()
    
    # Print final result
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    print(f"{'='*60}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
