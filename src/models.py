from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func
from typing import Optional


class Base(DeclarativeBase):
    pass


class DataUpdateRecord(Base):
    __tablename__ = "data_update_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str]
    title: Mapped[str]
    success: Mapped[bool]
    message: Mapped[Optional[str]]
    attempts: Mapped[int]
    run_time: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(default=func.now())


def load_tables(engine):
    """Creates tables if they do not exist. Does nothing if a table exists. Table schemas are not validated."""
    Base.metadata.create_all(engine)
