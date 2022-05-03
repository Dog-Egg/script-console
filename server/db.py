import logging
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Integer, select, insert, Text
from tornado.ioloop import IOLoop

from conf import settings
from utils import gen_token

async_session = sessionmaker(expire_on_commit=False, class_=AsyncSession)

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


class Config(Base):
    __tablename__ = 'config'

    version = Column(String(length=8), primary_key=True, default='v1')
    data = Column(Text, nullable=False)


def init():
    engine = create_async_engine('sqlite+aiosqlite:///%s' % os.path.join(settings.DATA_DIR, 'sqlite.db'))
    async_session.configure(bind=engine)

    os.makedirs(settings.DATA_DIR, exist_ok=True)

    async def main():
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)  # test
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as session:
            result = await session.execute(select(User).where(User.id == 1))
            admin: User = result.scalar_one_or_none()
            if not admin:
                token = gen_token()
                await session.execute(insert(User).values(
                    id=1,
                    real_name='admin',
                    token=token,
                    group=settings.ADMINISTRATOR)
                )
                await session.commit()
            else:
                token = admin.token
        return token

    return IOLoop.current().run_sync(main)
