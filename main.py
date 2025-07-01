#!/usr/bin/env python3
"""
RecruitIQ - Job Market Intelligence Platform
Main entry point for the application
"""

def main():
    """Main entry point for console script"""
    try:
        from recruitiq.cli.main import app
        app()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you've installed RecruitIQ properly:")
        print("   python scripts/install.py")
        print("   or")
        print("   pip install -e .")
        exit(1)
    except Exception as e:
        print(f"❌ Error running RecruitIQ: {e}")
        exit(1)

if __name__ == "__main__":
    main() 