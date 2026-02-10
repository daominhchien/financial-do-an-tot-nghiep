# loaders/__init__.py
"""
Loaders package - Lưu trữ dữ liệu

Modules:
    - csv_loader: Xuất ra file CSV
    - postgres_loader: Lưu vào PostgreSQL database
"""

from .csv_loader import CSVLoader

__all__ = ['CSVLoader']

# PostgresLoader được import riêng vì cần database connection
# from .postgres_loader import PostgresLoader
