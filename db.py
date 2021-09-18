import asyncio
import logging
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, select, insert

import settings
from utils import gen_token

DB_DIR = os.getenv('SC_DATA_DIR') or os.path.dirname(__file__)
DB_FILE = os.path.join(DB_DIR, 'sqlite.db')

engine = create_async_engine('sqlite+aiosqlite:///%s' % DB_FILE, echo=False)

Base = declarative_base()

logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    real_name = Column(String(length=50), nullable=False, index=True)
    token = Column(String(length=255), nullable=False, unique=True)
    group = Column(String(length=50))

    @property
    def is_admin(self):
        return self.group == settings.ADMINISTRATOR


def init():
    os.makedirs(DB_DIR, exist_ok=True)

    async def main():
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)  # test
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSession(engine) as session:
            result = await session.execute(select(User).where(User.real_name == 'admin'))
            admin: User = result.scalar_one_or_none()
            if not admin or not admin.is_admin:
                token = gen_token()
                await session.execute(insert(User).values(
                    real_name='admin',
                    token=token,
                    group=settings.ADMINISTRATOR)
                )
                await session.commit()
            else:
                token = admin.token
            logger.info('Admin Token: %s', token)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


if __name__ == '__main__':
    init()
