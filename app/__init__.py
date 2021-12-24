import os

from tornado.web import Application, StaticFileHandler
from . import file, ws, auth


def make_app(debug=False):
    static_path = os.path.join(os.path.dirname(__file__), 'web/build')
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

            # ws
            (r'/ws/run', ws.RunScriptHandler),

            # static
            (r'/((?!api|ws).*)', StaticFileHandler, dict(path=static_path, default_filename='index.html')),
        ],
        debug=debug,
        cookie_secret='__secret__'
    )
