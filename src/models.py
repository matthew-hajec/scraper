from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func


class Base(DeclarativeBase):
    pass


class DataUpdateRecord(Base):
    __tablename__ = "date_update_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str]
    title: Mapped[str]
    message: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now())


def load_tables(engine):
    """Creates tables if they do not exist. Does nothing if a table exists. Table schemas are not validated."""
    Base.metadata.create_all(engine)
