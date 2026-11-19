"""bot_state kalit-qiymat jadvali (rejalashtirilgan ishlar uchun)."""

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import BotState


class StateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, key: str) -> str | None:
        row = await self.session.get(BotState, key)
        return row.value if row is not None else None

    async def set(self, key: str, value: str) -> None:
        row = await self.session.get(BotState, key)
        if row is None:
            self.session.add(BotState(key=key, value=value))
        else:
            row.value = value
        await self.session.commit()
