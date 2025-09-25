# database/__init__.py - Database package initialization
from .connection import get_database_connection, init_database

__all__ = ['get_database_connection', 'init_database']
