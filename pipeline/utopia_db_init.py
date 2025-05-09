"""
This module initializes the database.
Essentially a copy of DESDEO/desdeo/api/db_init.py, just with the test user and example problems removed.
"""

import json
from os import walk
import warnings

import numpy as np
import polars as pl
from sqlalchemy import text
from sqlalchemy_utils import create_database, database_exists, drop_database

from desdeo.api import db_models
from desdeo.api.config import DBConfig
from desdeo.api.db import Base, SessionLocal, engine
from desdeo.api.routers.UserAuth import get_password_hash
from desdeo.api.schema import Methods, ObjectiveKind, ProblemKind, Solvers, UserPrivileges, UserRole
from desdeo.problem.schema import DiscreteRepresentation, Objective, Problem, Variable

# The following line creates the database and tables. This is not ideal, but it is simple for now.
# TODO: Remove this line and create a proper database migration system.
print("Creating database tables.")
if not database_exists(engine.url):
    create_database(engine.url)
else:
    warnings.warn("Database already exists. Clearing it.", stacklevel=1)

    # Drop all active connections
    db = SessionLocal()
    terminate_connections_sql = text("""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = :db_name AND pid <> pg_backend_pid();
    """)
    db.execute(terminate_connections_sql, {"db_name": DBConfig.db_database})

    # Drop all tables
    Base.metadata.drop_all(bind=engine)
print("Database tables created.")

# Create the tables in the database.
Base.metadata.create_all(bind=engine)

# Create test users
db = SessionLocal()

# Add the NIMBUS method into the database
nimbus = db_models.Method(
    kind=Methods.NIMBUS,
    properties=[],
    name="NIMBUS",
)
db.add(nimbus)
db.commit()

db.close()
