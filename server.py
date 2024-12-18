# -*- coding: utf-8 -*-
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage
import cherrypy
import json

# Clase para manejar conexiones WebSocket
class KinectWebSocketHandler(WebSocket):
    _clients = set()  # Mantiene una lista de clientes conectados

    def received_message(self, message):
        print("Mensaje recibido del cliente: {}".format(message))
        # Echo del mensaje recibido
        self.send(message)

    def opened(self):
        print("Nueva conexión establecida")
        self.__class__._clients.add(self)

    def closed(self, code, reason="No se proporcionó razón"):
        print("Conexión cerrada. Razón: {}".format(reason))
        self.__class__._clients.remove(self)

    @classmethod
    def broadcast(cls, message):
        """Envía un mensaje a todos los clientes conectados."""
        for client in cls._clients:
            client.send(TextMessage(message))


# Clase del servidor WebSocket
class WebSocketServer(object):
    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler llamado: ws")
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        handler = cherrypy.request.ws_handler  # WebSocket handler asociado


# Configuración y arranque del servidor
def start_server():
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    # Configuración del servidor
    config = {
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': KinectWebSocketHandler
        }
    }

    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',  # Usa IPv4 explícitamente
        'server.socket_port': 9001,        # Puerto del servidor
        'log.screen': True                 # Habilitar logs en pantalla
    })

    print("Iniciando servidor WebSocket en ws://127.0.0.1:9001/ws")
    cherrypy.quickstart(WebSocketServer(), '/', config)


# Punto de entrada
if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        print("Servidor detenido")
