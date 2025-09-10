"""
This module initializes the database.
Essentially a copy of DESDEO/desdeo/api/db_init.py, just with the test user and example problems removed.
"""

import warnings

from sqlalchemy_utils import database_exists
from sqlmodel import Session, SQLModel

from desdeo.api.config import ServerDebugConfig, SettingsConfig
from desdeo.api.db import engine
from desdeo.api.models import ProblemDB, User, UserRole
from desdeo.api.routers.user_authentication import get_password_hash
from desdeo.problem.testproblems import dtlz2, river_pollution_problem, simple_knapsack

problems = [dtlz2(10, 3), simple_knapsack(), river_pollution_problem()]

if __name__ == "__main__":
    if SettingsConfig.debug:
        # debug stuff

        print("Creating database tables.")
        if not database_exists(engine.url):
            SQLModel.metadata.create_all(engine)
        else:
            warnings.warn("Database already exists. Clearing it.", stacklevel=1)
            # Drop all tables
            SQLModel.metadata.drop_all(bind=engine)
            SQLModel.metadata.create_all(engine)
        print("Database tables created.")

        with Session(engine) as session:
            user_analyst = User(
                username=ServerDebugConfig.test_user_analyst_name,
                password_hash=get_password_hash(ServerDebugConfig.test_user_analyst_password),
                role=UserRole.analyst,
                group="",
            )
            session.add(user_analyst)
            session.commit()
            session.refresh(user_analyst)

    else:
        # deployment stuff
        pass