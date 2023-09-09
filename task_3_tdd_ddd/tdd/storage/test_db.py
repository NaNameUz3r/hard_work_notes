import os
from .db import DB_NAME


def test__db_created(database):
    database._migrate_db()
    assert os.path.exists(DB_NAME)
