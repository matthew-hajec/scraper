from datetime import datetime
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func


class Base(DeclarativeBase):
    pass


class ItemRecord(Base):
    __tablename__ = "steam_item_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_url: Mapped[int] = Mapped[Optional[str]]
    name: Mapped[str]
    hash_name: Mapped[str]
    sell_listings: Mapped[int]
    sell_price: Mapped[int]
    sale_price_text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    def __repr__(self) -> str:
        return f'ItemRecord(id={self.id}, item_url={self.item_url }, name={self.name}, hash_name={self.hash_name}, ' + \
               f'sell_listings={self.sell_listings}, sell_price={self.sell_price}, sale_price_text={self.sale_price_text})'


def load_tables(engine):
    """Creates tables if they do not exist. Does nothing if a table exists. Table schemas are not validated."""
    Base.metadata.create_all(engine)
