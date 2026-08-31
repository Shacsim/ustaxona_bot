"""Foydalanuvchilar bilan ishlash — barcha SQL shu yerda."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, UserRole


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def create(
        self,
        telegram_id: int,
        full_name: str,
        username: str | None,
        role: UserRole,
        is_active: bool,
        language: str = "uz",
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
            role=role,
            is_active=is_active,
            language=language,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def list_all(self) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.created_at))
        return list(result.scalars().all())

    async def list_active_admins(self) -> list[User]:
        result = await self.session.execute(
            select(User).where(
                User.role == UserRole.ADMIN, User.is_active.is_(True)
            )
        )
        return list(result.scalars().all())

    async def set_language(self, user_id: int, language: str) -> None:
        user = await self.session.get(User, user_id)
        if user is not None:
            user.language = language
            await self.session.commit()

    async def set_active(self, user_id: int, is_active: bool) -> User | None:
        user = await self.session.get(User, user_id)
        if user is None:
            return None
        user.is_active = is_active
        await self.session.commit()
        return user

    async def delete(self, user_id: int) -> bool:
        """O'chiradi; ustaga bog'langan buyurtmalar bo'lsa False qaytaradi."""
        user = await self.session.get(User, user_id)
        if user is None:
            return False
        try:
            await self.session.delete(user)
            await self.session.commit()
            return True
        except IntegrityError:
            await self.session.rollback()
            return False

    async def count_active(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.is_active.is_(True))
        )
        return int(result.scalar_one())
