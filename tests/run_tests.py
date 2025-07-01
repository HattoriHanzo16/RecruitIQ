#!/usr/bin/env python3
"""
RecruitIQ Test Runner

Comprehensive test runner with coverage reporting and test organization.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description="Running command"):
    """Run a shell command and return success status"""
    print(f"\n{description}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def run_tests(test_type="all", coverage=True, verbose=True, parallel=False):
    """Run tests with specified options"""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path
    cmd.append("tests/")
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=recruitiq",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
    
    # Add parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Filter by test type
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "scraper":
        cmd.extend(["-m", "scraper"])
    elif test_type == "analyzer":
        cmd.extend(["-m", "analyzer"])
    elif test_type == "cv":
        cmd.extend(["-m", "cv"])
    elif test_type == "cli":
        cmd.extend(["-m", "cli"])
    elif test_type == "database":
        cmd.extend(["-m", "database"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    
    # Run the tests
    return run_command(cmd, f"Running {test_type} tests")


def run_lint():
    """Run code linting"""
    commands = [
        (["python", "-m", "flake8", "recruitiq/", "tests/"], "Running flake8 linting"),
        (["python", "-m", "black", "--check", "recruitiq/", "tests/"], "Running black format check"),
        (["python", "-m", "isort", "--check-only", "recruitiq/", "tests/"], "Running isort import check")
    ]
    
    success = True
    for cmd, description in commands:
        if not run_command(cmd, description):
            success = False
    
    return success


def run_type_check():
    """Run type checking with mypy"""
    return run_command(
        ["python", "-m", "mypy", "recruitiq/"],
        "Running mypy type checking"
    )


def run_security_check():
    """Run security checks"""
    commands = [
        (["python", "-m", "bandit", "-r", "recruitiq/"], "Running bandit security check"),
        (["python", "-m", "safety", "check"], "Running safety vulnerability check")
    ]
    
    success = True
    for cmd, description in commands:
        if not run_command(cmd, description):
            success = False
    
    return success


def clean_test_artifacts():
    """Clean test artifacts and cache files"""
    import shutil
    
    artifacts = [
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "__pycache__",
        "*.pyc",
        ".mypy_cache"
    ]
    
    print("\n🧹 Cleaning test artifacts...")
    
    for artifact in artifacts:
        # Handle glob patterns
        if "*" in artifact:
            import glob
            for file in glob.glob(f"**/{artifact}", recursive=True):
                try:
                    Path(file).unlink()
                    print(f"Removed file: {file}")
                except:
                    pass
        else:
            # Handle directories and files
            for path in Path(".").rglob(artifact):
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"Removed directory: {path}")
                    else:
                        path.unlink()
                        print(f"Removed file: {path}")
                except:
                    pass
    
    print("✅ Cleanup completed")


def generate_test_report():
    """Generate comprehensive test report"""
    print("\n📊 Generating comprehensive test report...")
    
    # Run tests with detailed coverage
    success = run_command([
        "python", "-m", "pytest",
        "tests/",
        "--cov=recruitiq",
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-report=term-missing",
        "--junitxml=test-results.xml",
        "--html=test-report.html",
        "--self-contained-html"
    ], "Generating detailed test report")
    
    if success:
        print("\n📋 Test Report Generated:")
        print("- HTML Coverage Report: htmlcov/index.html")
        print("- XML Coverage Report: coverage.xml")
        print("- Test Results XML: test-results.xml")
        print("- Test Report HTML: test-report.html")
    
    return success


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="RecruitIQ Test Runner")
    
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "scraper", "analyzer", "cv", "cli", "database", "fast"],
        default="all",
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage reporting"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run tests in quiet mode"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linting checks"
    )
    
    parser.add_argument(
        "--type-check",
        action="store_true",
        help="Run type checking"
    )
    
    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security checks"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate comprehensive test report"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean test artifacts before running"
    )
    
    parser.add_argument(
        "--all-checks",
        action="store_true",
        help="Run all tests and checks (tests, lint, type-check, security)"
    )
    
    args = parser.parse_args()
    
    print("🧪 RecruitIQ Test Runner")
    print("=" * 50)
    
    # Clean artifacts if requested
    if args.clean:
        clean_test_artifacts()
    
    success = True
    
    # Run comprehensive checks if requested
    if args.all_checks:
        print("\n🔍 Running comprehensive test suite...")
        
        checks = [
            (lambda: run_tests("all", not args.no_coverage, not args.quiet, args.parallel), "Unit Tests"),
            (run_lint, "Code Linting"),
            (run_type_check, "Type Checking"),
            (run_security_check, "Security Checks")
        ]
        
        for check_func, check_name in checks:
            print(f"\n--- {check_name} ---")
            if not check_func():
                success = False
                print(f"❌ {check_name} failed")
            else:
                print(f"✅ {check_name} passed")
    
    else:
        # Run individual checks
        if args.lint:
            success &= run_lint()
        
        if args.type_check:
            success &= run_type_check()
        
        if args.security:
            success &= run_security_check()
        
        # Run tests (default action)
        if not any([args.lint, args.type_check, args.security, args.report]):
            success &= run_tests(
                args.type, 
                not args.no_coverage, 
                not args.quiet, 
                args.parallel
            )
    
    # Generate report if requested
    if args.report:
        success &= generate_test_report()
    
    # Final status
    print("\n" + "=" * 50)
    if success:
        print("🎉 All checks passed successfully!")
        sys.exit(0)
    else:
        print("💥 Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 