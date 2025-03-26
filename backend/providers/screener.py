from typing import Optional
from resources.postgres import Screener, db
from sqlalchemy import select


def get_screener_by_id(id_: str) -> Optional[Screener]:
    """Gets a Screener from the database by id. Returns None if it does not exist"""
    return db.session.scalars(select(Screener).where(Screener.id == id_)).one_or_none()
