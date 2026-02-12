from db.models.tool import Tool
from db.repositories.base import BaseRepository


class ToolRepository(BaseRepository):
    model = Tool