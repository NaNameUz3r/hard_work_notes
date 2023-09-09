import pytest
from ..models.task import Task
from dirty_equals import IsUUID


def test__create__task(new_task) -> None:
    task = new_task
    assert task.name == "Task 1"
    assert task.description == "description"
    assert task.status == "todo"


def test__create__task_tracker(task_tracker) -> None:
    tracker = task_tracker
    assert len(tracker.tasks) == 0


def test__add_task__to_tracker(task_tracker, new_task):
    tracker = task_tracker
    assert len(tracker.tasks) == 0
    tracker.add_task(new_task)
    assert new_task.id == IsUUID
    assert len(tracker.tasks) == 1


def test__get_task_by_existing_id(task_tracker, new_task):
    task_id = task_tracker.add_task(new_task)
    get_task = task_tracker.get_task_by_id(task_id)

    assert new_task.id == get_task.id


def test__set_new_correct_status_to_task(task_tracker, new_task):
    task_id = task_tracker.add_task(new_task)
    task_tracker.task_set_status(task_id, status="in_progress")
    assert new_task.status == "in_progress"


def test__set_new_incorrect_status_to_task(task_tracker, new_task):
    task_id = task_tracker.add_task(new_task)
    with pytest.raises(ValueError) as excinfo:
        task_tracker.task_set_status(task_id, status="YOLO")
    assert (
        str(excinfo.value)
        == "Invalid status: YOLO. Should be one of ('todo', 'in_progress', 'done')"
    )


def test__delete_task_by_id(task_tracker, new_task):
    task_id = task_tracker.add_task(new_task)
    assert len(task_tracker.tasks) == 1
    task_tracker.delete_task_by_id(task_id)
    assert len(task_tracker.tasks) == 0


def test__get_all_tasks(task_tracker):
    task_1 = Task(name="Task 1", description="description", status="todo")
    task_2 = Task(name="Task 2", description="description", status="in_progress")
    task_3 = Task(name="Task 2", description="description", status="done")
    task_tracker.add_task(task_1)
    task_tracker.add_task(task_2)
    task_tracker.add_task(task_3)
    fetch_all = task_tracker.get_all_tasks()
    assert fetch_all == [dict(task_1), dict(task_2), dict(task_3)]
