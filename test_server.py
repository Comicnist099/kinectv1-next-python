# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient
import time
import sys

class TestClient(WebSocketClient):
    def opened(self):
        print("Conexión establecida con el servidor WebSocket")
        # Envía un mensaje al servidor al abrir la conexión
        self.send("Hola, servidor!")

    def closed(self, code, reason=None):
        print("Conexión cerrada. Código: {}, Razón: {}".format(code, reason))

    def received_message(self, message):
        print("Mensaje recibido del servidor: {}".format(message))

# Punto de entrada
if __name__ == '__main__':
    try:
        print("Versión de Python: {}".format(sys.version))
        print("Intentando conectar a ws://127.0.0.1:9001/ws...")
        # Conexión al servidor WebSocket
        ws = TestClient('ws://127.0.0.1:9001/ws')
        ws.connect()
        print("Conexión exitosa. Manteniendo abierta por 5 segundos...")
        time.sleep(5)  # Mantiene la conexión abierta durante 5 segundos
    except KeyboardInterrupt:
        print("Interrupción del usuario. Cerrando...")
    except Exception as e:
        print("Error al conectar: {}".format(e))
        print("Tipo de error: {}".format(type(e)))
    finally:
        # Cierra la conexión si está abierta
        try:
            if 'ws' in locals() and ws.sock is not None:
                print("Cerrando conexión...")
                ws.close()
        except Exception as e:
            print("Error al cerrar la conexión: {}".format(e))
        print("Programa terminado.")
