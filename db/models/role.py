from sqlalchemy.orm import Mapped

from db.connection import Base


class Role(Base):
    __tablename__ = "roles"

    title: Mapped[str]