import os.path

from tornado.web import Application, StaticFileHandler as _StaticFileHandler, HTTPError

from conf import settings, Config
from fs import FileSystem
from .handlers import auth, config, file, ws


class StaticFileHandler(_StaticFileHandler):
    def validate_absolute_path(self, *args, **kwargs):
        # handle SPA router: history mode
        try:
            return super().validate_absolute_path(*args, **kwargs)
        except HTTPError as exc:
            if exc.status_code == 404:
                return os.path.join(self.root, self.default_filename)
            raise


def make_app():
    return Application(
        [
            # auth
            (r'/api/sign', auth.SignHandler),
            (r'/api/me', auth.MeHandler),
            (r'/api/users', auth.UsersHandler),
            (r'/api/users/(.*)', auth.UserHandler),

            # file
            (r'/api/file/tree', file.FileTreeHandler),
            (r'/api/file/mkdir', file.MakeDirHandler),
            (r'/api/file/mkfile', file.MakeFileHandler),
            (r'/api/file/read', file.FileReadHandler),
            (r'/api/file/write', file.FileWriteHandler),
            (r'/api/file/rename', file.FileRenameHandler),
            (r'/api/file/remove', file.FileRemoveHandler),
            (r'/api/file/upload', file.FileUploadHandler),
            (r'/api/file/download', file.FileDownloadHandler),

            # config
            (r'/api/config', config.ConfigHandler),

            # ws
            (r'/ws/run', ws.RunScriptHandler),
            (r'/ws/console', ws.ConsoleHandler),

            # static
            (r'/((?!api|ws).*)', StaticFileHandler, dict(path=settings.STATIC_ROOT,
                                                         default_filename='index.html')
             ),
        ],
        debug=settings.DEBUG,
        cookie_secret=settings.COOKIE_SECRET,
        fs=FileSystem(settings.SCRIPTS_DIR),
        config=Config.sync_build()
    )
