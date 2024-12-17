# -*- coding: utf-8 -*-

import pygame
import pygame.color
from pykinect import nui
import pygetwindow as gw
import sys
import traceback
import time

KINECTEVENT = pygame.USEREVENT
WINDOW_SIZE = 640, 480
BORDER_SIZE = 10
BORDER_COLOR = pygame.color.THECOLORS["blue"]
BORDER_BLINK_COLOR = pygame.color.THECOLORS["red"]

JOINT_COLOR = pygame.color.THECOLORS["red"]
JOINT_RADIUS = 5

FONT_COLOR = pygame.color.THECOLORS["white"]
FONT_SIZE = 24

skeleton_detected = False
joint_0_coords = (0, 0)
last_detection_time = time.time()
kinect = None  # Global variable to store the Kinect runtime
border_touched = False
blink_timer = 0

def post_frame(frame):
    global skeleton_detected, last_detection_time, border_touched
    try:
        skeletons = [skeleton for skeleton in frame.SkeletonData
                     if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED]

        print "Frames procesados: %d esqueletos detectados." % len(skeletons)

        if skeletons:
            if not skeleton_detected:
                print "Esqueleto(s) detectado(s)!"
            skeleton_detected = True
            last_detection_time = time.time()
            pygame.event.post(
                pygame.event.Event(KINECTEVENT, skeletons=skeletons)
            )
        else:
            current_time = time.time()
            if current_time - last_detection_time > 2:
                if skeleton_detected:
                    skeleton_detected = False
                    print "No se detecta esqueleto."
                pygame.event.post(
                    pygame.event.Event(KINECTEVENT, skeletons=[])
                )
    except Exception as e:
        print "Error en post_frame: %s" % e
        traceback.print_exc()

def draw_joints(skeletons):
    global joint_0_coords
    try:
        for skeleton in skeletons:
            for joint_id, joint in enumerate(skeleton.SkeletonPositions):
                if joint.x != 0 and joint.y != 0 and joint.z != 0:
                    x = int(joint.x * WINDOW_SIZE[0]) + WINDOW_SIZE[0] // 2
                    y = int(-joint.y * WINDOW_SIZE[1]) + WINDOW_SIZE[1] // 2
                    if joint_id == 0:
                        joint_0_coords = (x, y)
                    pygame.draw.circle(screen, JOINT_COLOR, (x, y), JOINT_RADIUS)
    except Exception as e:
        print "Error en draw_joints: %s" % e
        traceback.print_exc()

def draw_text(text, position):
    try:
        text_surface = font.render(text, True, FONT_COLOR)
        screen.blit(text_surface, position)
    except Exception as e:
        print "Error al dibujar texto: %s" % e
        traceback.print_exc()

def draw_border():
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, WINDOW_SIZE[0], BORDER_SIZE))
    pygame.draw.rect(screen, BORDER_COLOR, (0, WINDOW_SIZE[1] - BORDER_SIZE, WINDOW_SIZE[0], BORDER_SIZE))
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, BORDER_SIZE, WINDOW_SIZE[1]))
    pygame.draw.rect(screen, BORDER_COLOR, (WINDOW_SIZE[0] - BORDER_SIZE, 0, BORDER_SIZE, WINDOW_SIZE[1]))

def main():
    global screen, font, skeleton_detected, kinect, last_detection_time
    pygame.init()

    print "Inicializando PyGame..."
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
    pygame.display.set_caption('Juego Kinect con Python')
    font = pygame.font.Font(None, FONT_SIZE)
    print "PyGame Inicializado."

    try:
        window = gw.getWindowsWithTitle('Juego Kinect con Python')[0]
        window.moveTo(0, 0)
    except Exception as e:
        print "Error al mover la ventana: %s" % e

    print "Inicializando Kinect..."
    try:
        kinect = nui.Runtime()
        print "Kinect Inicializado."
        kinect.skeleton_engine.enabled = True
        print "Seguimiento de esqueleto habilitado."
        kinect.skeleton_frame_ready += post_frame
        clock = pygame.time.Clock()
        running = True
        current_skeletons = []

        while running:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == KINECTEVENT:
                        current_skeletons = event.skeletons

                screen.fill(pygame.color.THECOLORS["black"])

                draw_border()
                draw_joints(current_skeletons)

                skeleton_status = "Esqueleto Detectado" if skeleton_detected else "No se detecta Esqueleto"
                draw_text(skeleton_status, (10, 10))

                if not skeleton_detected:
                    draw_text("Buscando cuerpo...", (10, 40))

                draw_text("Joint 0: %s" % str(joint_0_coords), (10, 70))
                draw_text("Running: ON" if running else "Running: OFF", (10, 100))

                pygame.display.flip()
                clock.tick(60)

            except Exception as e:
                print "Error en el bucle principal: %s" % e
                traceback.print_exc()
                continue

    except Exception as e:
        print "Error al inicializar Kinect: %s" % e
        traceback.print_exc()
    finally:
        if kinect:
            kinect.close()

    print "Saliendo del juego..."

if __name__ == '__main__':
    print "Iniciando seguimiento de esqueleto con Kinect..."
    try:
        main()
    except Exception as e:
        print "Error crítico: %s" % e
        traceback.print_exc()
    finally:
        print "Programa terminado."
        pygame.quit()
        sys.exit()
