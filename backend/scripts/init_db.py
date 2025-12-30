"""
Initialize the database with migrations and seed data
Run this script to set up a fresh database
"""
import subprocess
import sys


def run_command(command: list[str], description: str):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description} failed")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Initialize the database"""
    print("\n" + "="*60)
    print("DATABASE INITIALIZATION")
    print("="*60)
    
    # Run migrations
    if not run_command(
        ["alembic", "upgrade", "head"],
        "Running database migrations"
    ):
        print("\n✗ Database initialization failed!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ DATABASE INITIALIZED SUCCESSFULLY!")
    print("="*60)
    print("\nYour database is ready to use.")
    print("Default categories have been created.")
    print("\nNext steps:")
    print("  1. Start the backend: uvicorn app.main:app --reload")
    print("  2. Configure your Telegram bot token in .env")
    print("  3. Access API docs at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
