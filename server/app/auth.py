import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

import db
from app.base import BaseHandler, admin_required
from utils import gen_token


class UsersHandler(BaseHandler):
    @admin_required
    async def get(self):
        async with db.engine.connect() as conn:
            result = await conn.execute(sqlalchemy.select(db.User))
            users = [dict(i) for i in result.fetchall()]
            self.write(dict(users=users))

    @admin_required
    async def post(self):
        real_name = self.get_body_argument('real_name')
        group = self.get_body_argument('group', default=None) or None
        async with AsyncSession(db.engine) as session:
            data = dict(real_name=real_name, token=gen_token(), group=group)
            await session.execute(sqlalchemy.insert(db.User).values(**data))
            await session.commit()
        await self.finish(data)


class UserHandler(BaseHandler):
    @admin_required
    async def delete(self, uid):
        async with AsyncSession(db.engine) as session:
            await session.execute(sqlalchemy.delete(db.User).where(db.User.id == uid))
            await session.commit()
        await self.finish()


class SignHandler(BaseHandler):
    async def post(self):
        token = self.get_body_argument('token')
        async with AsyncSession(db.engine) as session:
            result = await session.execute(sqlalchemy.select(db.User).where(db.User.token == token))
            user = result.scalar_one_or_none()
        if user:
            self.set_secure_cookie('sessionid', user.token)
        else:
            await self.finish_error(errors={'token': '无效的令牌'})

    def delete(self):
        self.clear_cookie('sessionid')


class MeHandler(BaseHandler):
    async def get(self):
        user = await self.current_user
        if user:
            data = dict(anonymous=False, id=user.id, realName=user.real_name, group=user.group)
        else:
            data = dict(anonymous=True)
        await self.finish(data)
