"""Anonim savollar bilan ishlash."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Question


class QuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, asker_id: int, language: str, text: str) -> Question:
        question = Question(asker_id=asker_id, language=language, text=text)
        self.session.add(question)
        await self.session.commit()
        await self.session.refresh(question)
        return question

    async def set_group_message_id(self, question_id: int, message_id: int) -> None:
        question = await self.session.get(Question, question_id)
        if question is not None:
            question.group_message_id = message_id
            await self.session.commit()

    async def get_by_group_message_id(self, message_id: int) -> Question | None:
        result = await self.session.execute(
            select(Question).where(Question.group_message_id == message_id)
        )
        return result.scalar_one_or_none()
