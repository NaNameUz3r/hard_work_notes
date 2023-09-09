import pytest
from .package.tracker import TaskTracker
from tdd.models.task import Task


@pytest.fixture
def task_tracker() -> TaskTracker:
    return TaskTracker()


@pytest.fixture
def new_task() -> Task:
    return Task(name="Task 1", description="description", status="todo")
