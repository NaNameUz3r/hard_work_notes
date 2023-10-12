import pytest
from .package.tracker import TaskTracker
from .models.task import Task
from .storage.db import Database


@pytest.fixture
def new_task() -> Task:
    return Task(name="Task 1", description="description", status="todo")


@pytest.fixture
def database():
    return Database()


@pytest.fixture
def task_tracker(database) -> TaskTracker:
    return TaskTracker(db=database)


@pytest.fixture(autouse=True, scope="function")
def truncate_db(database):
    database._migrate_db()
    database._truncate_tasks()
