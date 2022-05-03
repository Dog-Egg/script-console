import sqlalchemy

import db
from web.base import APIHandler, admin_required, not_authenticate
from utils import gen_token


class UsersHandler(APIHandler):
    @admin_required
    async def get(self):
        async with db.async_session().bind.connect() as conn:
            result = await conn.execute(sqlalchemy.select(db.User))
            users = [dict(i) for i in result.fetchall()]
            self.write(dict(users=users))

    @admin_required
    async def post(self):
        real_name = self.get_body_argument('real_name')
        group = self.get_body_argument('group', default=None) or None
        async with db.async_session() as session:
            data = dict(real_name=real_name, token=gen_token(), group=group)
            await session.execute(sqlalchemy.insert(db.User).values(**data))
            await session.commit()
        await self.finish(data)


class UserHandler(APIHandler):
    @admin_required
    async def delete(self, uid):
        async with db.async_session() as session:
            await session.execute(sqlalchemy.delete(db.User).where(db.User.id == uid))
            await session.commit()
        await self.finish()


class SignHandler(APIHandler):
    @not_authenticate
    async def post(self):
        token = self.get_body_argument('token')
        async with db.async_session() as session:
            result = await session.execute(sqlalchemy.select(db.User).where(db.User.token == token))
            user = result.scalar_one_or_none()
        if user:
            self.set_secure_cookie('sessionid', user.token)
        else:
            await self.finish_error(errors={'token': '无效的令牌'})

    @not_authenticate
    def delete(self):
        self.clear_cookie('sessionid')


class MeHandler(APIHandler):
    async def get(self):
        user = await self.current_user
        if user:
            data = dict(anonymous=False, id=user.id, realName=user.real_name, group=user.group)
        else:
            data = dict(anonymous=True)
        await self.finish(data)
