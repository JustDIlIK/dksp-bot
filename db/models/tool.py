from sqlalchemy.orm import Mapped

from db.connection import Base


class Tool(Base):
    __tablename__ = "tools"

    title: Mapped[str]