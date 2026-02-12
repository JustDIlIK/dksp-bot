from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.connection import Base


class Media(Base):
    __tablename__ = "media"

    file_url: Mapped[str]
    file_type: Mapped[str]

    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"))

    report = relationship("Report", back_populates="media")
