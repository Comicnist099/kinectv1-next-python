# -*- coding: utf-8 -*-
import pygame
import pygame.color
from pykinect import nui
import pygetwindow as gw
import sys
import traceback
import time
from ws4py.client.threadedclient import WebSocketClient
import json

# Clase WebSocket para Kinect
class KinectWebSocketClient(WebSocketClient):
    def opened(self):
        print("Conexión establecida con el servidor WebSocket")
    
    def closed(self, code, reason=""):
        print("Conexión cerrada: {0} - {1}".format(code, reason))
    
    def received_message(self, message):
        print("Mensaje recibido: {0}".format(message))

# Clase principal del juego Kinect
class KinectGame(object):
    KINECTEVENT = pygame.USEREVENT
    WINDOW_SIZE = 640, 480
    BORDER_SIZE = 10
    BORDER_COLOR = pygame.color.THECOLORS["blue"]
    JOINT_COLOR = pygame.color.THECOLORS["red"]
    JOINT_RADIUS = 5
    FONT_COLOR = pygame.color.THECOLORS["white"]
    FONT_SIZE = 24

    def __init__(self):
        self.skeleton_detected = False
        self.joint_0_coords = (0, 0)
        self.last_detection_time = time.time()
        self.kinect = None
        self.screen = None
        self.font = None
        self.running = True
        self.current_skeletons = []
        self.ws_client = None
        self.last_sent_time = time.time()  # Tiempo del último envío

    def send_joints(self, joints_data):
        current_time = time.time()
        if current_time - self.last_sent_time >= 0:  # Solo enviar si ha pasado 1 segundo
            if self.ws_client and not self.ws_client.client_terminated:
                try:
                    self.ws_client.send(json.dumps(joints_data))  # Enviar los datos de los joints como JSON
                    self.last_sent_time = current_time  # Actualizar el tiempo de envío
                except Exception as e:
                    print("Error al enviar datos: %s" % e)
                    traceback.print_exc()
            elif self.ws_client is None:
                pass  # El cliente WebSocket no existe, no hace nada
            else:
                print("Cliente WebSocket está terminado. Reconectando...")
                self.initialize_websocket()

    def initialize_websocket(self):
        try:
            self.ws_client = KinectWebSocketClient('ws://127.0.0.1:9001/ws')  # Cambié el puerto a 9001
            self.ws_client.connect()
            print("Conectado al servidor WebSocket")
        except Exception as e:
            print("Error al conectar con WebSocket: %s" % e)
            print("El juego continuará sin conexión WebSocket.")
            self.ws_client = None

    def post_frame(self, frame):
        try:
            skeletons = [skeleton for skeleton in frame.SkeletonData
                         if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED]

            print("Frames procesados: {0} esqueletos detectados.".format(len(skeletons)))

            if skeletons:
                if not self.skeleton_detected:
                    print("Esqueleto(s) detectado(s)!")
                self.skeleton_detected = True
                self.last_detection_time = time.time()
                pygame.event.post(
                    pygame.event.Event(self.KINECTEVENT, skeletons=skeletons)
                )
                
                # Enviar los datos de las articulaciones del primer esqueleto detectado
                joints_data = self.get_joints_data(skeletons[0], joints_to_send=[2, 3])

                self.send_joints(joints_data)
            else:
                current_time = time.time()
                if current_time - self.last_detection_time > 2:
                    if self.skeleton_detected:
                        self.skeleton_detected = False
                        print("No se detecta esqueleto.")
                    pygame.event.post(
                        pygame.event.Event(self.KINECTEVENT, skeletons=[])
                    )
        except Exception as e:
            print("Error en post_frame: {0}".format(e))
            traceback.print_exc()

    def get_joints_data(self, skeleton, joints_to_send=None):
        if joints_to_send is None:
            joints_to_send = [2, 3]  # Si no se pasa, por defecto se envían los joints 2 y 3.

        joints_data = {}
        for joint_id, joint in enumerate(skeleton.SkeletonPositions):
            if joint_id in joints_to_send and joint.x != 0 and joint.y != 0 and joint.z != 0:
                x = int(joint.x * self.WINDOW_SIZE[0]) + self.WINDOW_SIZE[0] // 2
                y = int(-joint.y * self.WINDOW_SIZE[1]) + self.WINDOW_SIZE[1] // 2
                joints_data["joint_{0}".format(joint_id)] = {"x": x, "y": y}

        return joints_data


    def draw_joints(self, skeletons):
        for skeleton in skeletons:
            for joint_id, joint in enumerate(skeleton.SkeletonPositions):
                if joint.x != 0 and joint.y != 0 and joint.z != 0:
                    x = int(joint.x * self.WINDOW_SIZE[0]) + self.WINDOW_SIZE[0] // 2
                    y = int(-joint.y * self.WINDOW_SIZE[1]) + self.WINDOW_SIZE[1] // 2
                    pygame.draw.circle(self.screen, self.JOINT_COLOR, (x, y), self.JOINT_RADIUS)

    def draw_text(self, text, position):
        text_surface = self.font.render(text, True, self.FONT_COLOR)
        self.screen.blit(text_surface, position)

    def draw_border(self):
        pygame.draw.rect(self.screen, self.BORDER_COLOR, (0, 0, self.WINDOW_SIZE[0], self.BORDER_SIZE))
        pygame.draw.rect(self.screen, self.BORDER_COLOR, (0, self.WINDOW_SIZE[1] - self.BORDER_SIZE, self.WINDOW_SIZE[0], self.BORDER_SIZE))
        pygame.draw.rect(self.screen, self.BORDER_COLOR, (0, 0, self.BORDER_SIZE, self.WINDOW_SIZE[1]))
        pygame.draw.rect(self.screen, self.BORDER_COLOR, (self.WINDOW_SIZE[0] - self.BORDER_SIZE, 0, self.BORDER_SIZE, self.WINDOW_SIZE[1]))

    def initialize(self):
        pygame.init()

        self.screen = pygame.display.set_mode(self.WINDOW_SIZE, 0, 32)
        pygame.display.set_caption('Juego Kinect con Python')
        self.font = pygame.font.Font(None, self.FONT_SIZE)

        try:
            window = gw.getWindowsWithTitle('Juego Kinect con Python')[0]
            window.moveTo(0, 0)
        except Exception as e:
            print("Error al mover la ventana: %s" % e)

        try:
            self.kinect = nui.Runtime()
            self.kinect.skeleton_engine.enabled = True
            self.kinect.skeleton_frame_ready += self.post_frame
        except Exception as e:
            print("Error al inicializar Kinect: %s" % e)

        # Inicializa la conexión WebSocket
        try:
            self.ws_client = KinectWebSocketClient('ws://127.0.0.1:9001/ws')  # Cambié el puerto a 9001
            self.ws_client.connect()
        except Exception as e:
            print("Error al conectar con WebSocket: %s" % e)
            self.ws_client = None

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == self.KINECTEVENT:
                    self.current_skeletons = event.skeletons

            self.screen.fill(pygame.color.THECOLORS["black"])

            self.draw_border()
            self.draw_joints(self.current_skeletons)

            skeleton_status = "Esqueleto Detectado" if self.skeleton_detected else "No se detecta Esqueleto"
            self.draw_text(skeleton_status, (10, 10))

            pygame.display.flip()
            clock.tick(60)

    def cleanup(self):
        if self.ws_client:
            self.ws_client.close()
        if self.kinect:
            self.kinect.close()
        pygame.quit()
        sys.exit()

def main():
    game = KinectGame()
    try:
        game.initialize()
        game.run()
    except Exception as e:
        print("Error crítico: {0}".format(e))
        traceback.print_exc()
    finally:
        game.cleanup()

if __name__ == '__main__':
    print("Iniciando seguimiento de esqueleto con Kinect...")
    main()
