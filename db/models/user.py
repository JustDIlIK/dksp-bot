from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.connection import Base


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[str] = mapped_column(unique=True)
    fio: Mapped[str]

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
