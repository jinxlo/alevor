"""Database connection management."""

import logging
import os
from typing import Optional
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class Database:
    """Manages database connections."""
    
    def __init__(self, db_url: Optional[str] = None):
        """Initialize database connection.
        
        Args:
            db_url: Database URL (default: from DB_URL env var)
        """
        self.db_url = db_url or os.getenv("DB_URL")
        if not self.db_url:
            raise ValueError("DB_URL not provided")
        
        self.connection_pool: Optional[pool.ThreadedConnectionPool] = None
        self._init_pool()
    
    def _init_pool(self) -> None:
        """Initialize connection pool."""
        try:
            self.connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=self.db_url
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Error initializing connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool."""
        if self.connection_pool is None:
            raise RuntimeError("Connection pool not initialized")
        return self.connection_pool.getconn()
    
    def return_connection(self, conn) -> None:
        """Return a connection to the pool."""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """Execute a SELECT query.
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            List of result rows
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()
        finally:
            self.return_connection(conn)
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            Number of affected rows
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing update: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def close(self) -> None:
        """Close all connections."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")

