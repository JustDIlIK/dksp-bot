from db.models.vehicle import Vehicle
from db.repositories.base import BaseRepository


class VehicleRepository(BaseRepository):
    model = Vehicle