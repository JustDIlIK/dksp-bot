from db.models.media import Media
from db.repositories.base import BaseRepository


class MediaRepository(BaseRepository):
    model = Media