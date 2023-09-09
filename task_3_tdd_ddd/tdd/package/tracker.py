from typing import List
from uuid import UUID, uuid4
from ..models.task import Task
from ..storage.db import Database


class TaskTracker:
    def __init__(self, db: Database):
        self.tasks = {}
        self.db = db
        self.db._migrate_db()
        self.VALID_STATUSES = ("todo", "in_progress", "done")

    def add_task(self, task: Task) -> UUID:
        new_task = task
        new_task.id = uuid4()
        self.db.save_task(new_task)
        return new_task.id

    def get_task_by_id(self, task_id: UUID) -> Task | None:
        return self.db.get_task_by_id(task_id)

    def task_set_status(self, task_id: UUID, status: str):
        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status: {status}. Should be one of {self.VALID_STATUSES}"
            )

        self.db.set_task_status(task_id, status)

    def delete_task_by_id(self, task_id: UUID) -> None:
        self.db.delete_task_by_id(task_id)

    def get_all_tasks(self) -> List[dict] | None:
        response = self.db.get_all_tasks()
        return response if response is not None else None
