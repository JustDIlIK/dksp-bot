from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db.connection import Base


class Report(Base):
    __tablename__ = "reports"

    user_id: Mapped[int]  = mapped_column(ForeignKey("users.id"))
    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    is_finished: Mapped[bool]  = mapped_column(default=False)

    media = relationship("Media", back_populates="report", cascade="all, delete-orphan")

    user = relationship("User")
    tool = relationship("Tool")
    vehicle = relationship("Vehicle")