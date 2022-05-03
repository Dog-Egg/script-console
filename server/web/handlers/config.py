import json
import traceback

import pydantic
from tornado.web import HTTPError

import db
from sqlalchemy.dialects.sqlite import insert
from web.base import APIHandler, admin_required


class ConfigHandler(APIHandler):
    @admin_required
    def get(self):
        error = self.config.error
        if isinstance(self.config.error, Exception):
            error = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        self.finish({'data': self.config.to_dict(), 'error': error})

    @admin_required
    async def put(self):
        error = HTTPError(400)
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            raise error

        if not isinstance(data, dict):
            raise error

        try:
            self.config.read_dict(data)
        except pydantic.ValidationError:
            raise error

        async with db.async_session() as session:
            stmt = insert(db.Config).values(version='v1', data=self.config.to_json())
            stmt = stmt.on_conflict_do_update(index_elements=['version'], set_={'data': self.config.to_json()})
            await session.execute(stmt)
            await session.commit()
        await self.finish()
