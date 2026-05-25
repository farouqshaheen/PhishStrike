"""Pytest configuration — sets isolated env before app imports."""

import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_fd, _TEST_DB = tempfile.mkstemp(suffix=".db")
os.close(_fd)

os.environ["DB_PATH"] = _TEST_DB
os.environ["SECRET_KEY"] = "pytest-secret-key-fixed-for-ci-tests!!"

import pytest

from phishstrike.core import database

database.init_db()


@pytest.fixture
def client():
    from phishstrike.dashboard.app import app

    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

