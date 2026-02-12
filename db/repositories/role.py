from db.models.role import Role
from db.repositories.base import BaseRepository


class RoleRepository(BaseRepository):
    model = Role