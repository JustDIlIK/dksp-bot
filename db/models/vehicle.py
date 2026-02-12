from sqlalchemy.orm import Mapped, mapped_column

from db.connection import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    model: Mapped[str]
    number: Mapped[str] = mapped_column(unique=True)
