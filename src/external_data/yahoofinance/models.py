from datetime import datetime
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func


class Base(DeclarativeBase):
    pass


class CurrencyRecord(Base):
    __tablename__ = "yahoofinance_currency_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    last_price: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    def __repr__(self) -> str:
        return f'CurrencyRecord(id={self.id}, name={self.name}, last_price={self.last_price})'


def load_tables(engine):
    """Creates tables if they do not exist. Does nothing if a table exists. Table schemas are not validated."""
    Base.metadata.create_all(engine)
