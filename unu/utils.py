from hydrogram import Client, filters
from hydrogram.types import Message

from config import sudoers
from unu.db import User


async def filter_sudoers_logic(flt, c: Client, m: Message):
    if not m.from_user:
        return None
    usr = m.from_user
    db_usr = await User.get_or_none(id=usr.id)
    if not db_usr:
        return False
    return bool(db_usr.sudo or usr.id in sudoers)


filter_sudoers = filters.create(filter_sudoers_logic, "FilterSudoers")


__all__ = ["filter_sudoers"]
