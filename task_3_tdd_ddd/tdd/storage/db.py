import sqlite3
from ..models.task import Task
from typing import List
from uuid import UUID

DB_NAME = "tasks.db"


class Database:
    def __init__(self):
        self.db_connection = sqlite3.connect(database=DB_NAME)
        self.db_connection.row_factory = sqlite3.Row
        self.cursor = self.db_connection.cursor()

    def _migrate_db(self):
        self.cursor.execute(
            """
                       CREATE TABLE IF NOT EXISTS tasks
                       (id VARCHAR(500) PRIMARY KEY, name TEXT, description TEXT, status TEXT);"""
        )
        self.db_connection.commit()

    def _truncate_tasks(self):
        self.cursor.execute("""DELETE FROM tasks;""")
        self.db_connection.commit()

    def save_task(self, task: Task):
        dict_to_save = task.model_dump()
        dict_to_save["id"] = str(dict_to_save["id"])
        self.cursor.execute(
            "INSERT INTO tasks VALUES (:id, :name, :description, :status)", dict_to_save
        )
        self.db_connection.commit()

    def get_task_by_id(self, task_id: UUID) -> Task | None:
        task_dict = self.cursor.execute(
            "SELECT * FROM tasks WHERE id=:id", {"id": str(task_id)}
        ).fetchone()
        if task_dict:
            return Task(
                id=task_dict["id"],
                name=task_dict["name"],
                description=task_dict["description"],
                status=task_dict["status"],
            )

    def get_all_tasks(self) -> List[dict] | None:
        tasks = self.cursor.execute("SELECT * FROM tasks").fetchall()
        if tasks:
            response = []
            for task in tasks:
                response.append(
                    Task(
                        id=task["id"],
                        name=task["name"],
                        description=task["description"],
                        status=task["status"],
                    )
                )
            return response
        return None

    def set_task_status(self, task_id: UUID, status: str):
        self.cursor.execute(
            "UPDATE tasks SET status=:status WHERE id=:id",
            {"id": str(task_id), "status": status},
        )
        self.db_connection.commit()

    def delete_task_by_id(self, task_id: UUID) -> None:
        self.cursor.execute("DELETE FROM tasks WHERE id=:id", {"id": str(task_id)})
        self.db_connection.commit()
