from db.models.user import User
from db.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User