from typing import List
from uuid import UUID, uuid4
from ..models.task import Task


class TaskTracker:
    def __init__(self):
        self.tasks = {}
        self.VALID_STATUSES = ("todo", "in_progress", "done")

    def add_task(self, task: Task) -> UUID:
        new_task = task
        new_task.id = uuid4()
        self.tasks[new_task.id] = task
        return new_task.id

    def get_task_by_id(self, task_id: UUID) -> Task:
        return self.tasks[task_id]

    def task_set_status(self, task_id: UUID, status: str):
        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status: {status}. Should be one of {self.VALID_STATUSES}"
            )

        lookup_id = self.get_task_by_id(task_id)
        if lookup_id:
            self.tasks[task_id].status = status

    def delete_task_by_id(self, task_id: UUID) -> None:
        self.tasks.pop(task_id)

    def get_all_tasks(self) -> List[dict]:
        response = []
        for _, task in self.tasks.items():
            response.append(dict(task))
        return response
