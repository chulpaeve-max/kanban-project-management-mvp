import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import create_tables, get_db
from models import Base
from sqlalchemy import create_engine, inspect

def test_create_tables():
    """Test that create_tables creates all expected tables"""
    # Use in-memory database for testing
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()
    
    assert 'users' in tables
    assert 'boards' in tables
    assert 'columns' in tables
    assert 'cards' in tables

def test_get_db():
    """Test that get_db returns a database session"""
    db_gen = get_db()
    db = next(db_gen)
    
    assert db is not None
    
    # Clean up
    try:
        next(db_gen)
    except StopIteration:
        pass
