import os
from jupyter_server.base.handlers import JupyterHandler
import tornado

class JupytexprHandler(JupyterHandler):

    @tornado.web.authenticated
    async def get(self, path):
        with open(path, 'rb') as f:
            data = f.read()
        os.remove(path)
        self.finish(data)

    @tornado.web.authenticated
    async def post(self, path):
        data = self.request.body
        with open(path, 'wb') as f:
            f.write(data)
        self.finish()
