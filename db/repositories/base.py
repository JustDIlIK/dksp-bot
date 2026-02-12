from sqlalchemy import select, insert, update, delete

from db.connection import async_session


class BaseRepository:
    model = None

    @classmethod

    async def get_all(cls):
        async with async_session() as session:
            query = select(cls.model).order_by(cls.model.id)
            result = await session.execute(query)

            return result.scalars().all()

    @classmethod
    async def get_by_id(cls, id):
        async with async_session() as session:
            query = select(cls.model).filter_by(id=id)
            result = await session.execute(query)

            return result.scalar()

    @classmethod
    async def get_by_variable(cls, **data):
        async with async_session() as session:
            query = select(cls.model).filter_by(**data)
            result = await session.execute(query)

            return result.scalar()

    @classmethod
    async def get_all_by_variable(cls, **data):
        async with async_session() as session:
            query = select(cls.model).filter_by(**data)
            result = await session.execute(query)

            return result.scalars().all()

    @classmethod
    async def add_record(cls, **data):
        async with async_session() as session:
            query = insert(cls.model).values(**data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()

            return result.scalar()

    @classmethod
    async def update_record(cls, id, **data):
        async with async_session() as session:
            query = update(cls.model).values(**data).filter_by(id=id).returning(cls.model)
            result = await session.execute(query)
            await session.commit()

            return result.scalar()

    @classmethod
    async def delete_by_id(cls, id: int):
        async with async_session() as session:
            await session.execute(delete(cls.model).where(cls.model.id == id))
            await session.commit()

