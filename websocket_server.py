# coding: utf8

import os.path
import logging
import json
from tornado import ioloop, web, websocket
from appBot.mdAppApi import MdAppApi
import appBot.utils as utils

SERVER_FOLDER = os.path.abspath(os.path.dirname(__file__))
LOGGER = logging.getLogger('tornado.application')

live_sockets = set()

class TestHandler(web.RequestHandler):
    def get(self):
        server = ioloop.IOLoop.current()
        server.add_callback(websocket_send_message, "build your data here")
        self.set_status(200)
        self.finish()


class MideaSubmitCard(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def set_default_headers(self):
    	# self.set_header("Access-Control-Allow-Origin", "*")
    	pass
    
    def open(self):
        LOGGER.debug("WebSocket opened")
        self.set_nodelay(True)
        live_sockets.add(self)
        self.write_message({"status":True,"msg":'ok',"type":'connection'})

    def on_message(self, message):
    	print(message)
    	message = json.loads(message)
    	mdappapi = MdAppApi()
    	try:
            r = eval(message['cmd'])(message['params'])
            '''example: {'cmd': 'mdappapi.appsearchfromsn', 'params': {'businessFlag': 'AZ', 'parseType': '10', 'productSn1': 'f'}, 'admin_uid': 5}'''
            print(r)
            self.write_message(json.dumps(r))
        except Exception as e:
            self.write_message({'status':False,'msg':str(e)})
            print(str(e))
            utils.errorReport(str(e),system_name = 'MdAppapi')
        LOGGER.debug('Message incomming: %s', message)

    def on_close(self):
        LOGGER.debug("WebSocket closed")


def websocket_send_message(message):
    removable = set()
    for ws in live_sockets:
        if not ws.ws_connection or not ws.ws_connection.stream.socket:
            removable.add(ws)
        else:
            ws.write_message(message)
    for ws in removable:
        live_sockets.remove(ws)


def serve_forever(port=80, address=''):
    application = web.Application([
            (r"/test/", TestHandler),#namespace
            (r"/mideacard", MideaSubmitCard),
        ],
        static_path=os.path.join(SERVER_FOLDER,),
        debug=True,
    )
    application.listen(port, address)
    LOGGER.debug(
            'Server listening at http://%s:%d/',
            address or 'localhost', port)
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    serve_forever(port = 3002)