from uuid import UUID
from pydantic import BaseModel


class Task(BaseModel):
    id: UUID | None = None
    name: str
    description: str
    status: str
