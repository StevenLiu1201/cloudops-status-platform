"""Command-line entry point for initializing the local database schema."""

from sqlalchemy import inspect

from backend.app.database import create_tables, get_engine


def main() -> None:
    """Create the schema and verify that the expected table exists."""

    create_tables()
    table_names = inspect(get_engine()).get_table_names()
    if "service_checks" not in table_names:
        raise RuntimeError("Expected service_checks table was not created")

    print("Database tables are ready: service_checks")


if __name__ == "__main__":
    main()
