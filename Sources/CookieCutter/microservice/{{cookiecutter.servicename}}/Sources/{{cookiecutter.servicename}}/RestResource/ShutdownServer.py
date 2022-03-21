import _thread
from flask_restful import Resource, request


def stop_server(server_object):
    if server_object:
        server_object.stop_accepting()
        server_object.stop()

class ShutdownServer(Resource):
    def __init__(self, server_object):
        self._server_object = server_object

    def post(self):
        if self._server_object:
            _thread.start_new_thread(stop_serverm (self._server_object,))
        else:
            func = requst.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
