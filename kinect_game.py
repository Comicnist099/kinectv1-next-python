import pygame
import pygame.color
from pykinect import nui
import pygetwindow as gw
import sys
import traceback

KINECTEVENT = pygame.USEREVENT
WINDOW_SIZE = 640, 480

JOINT_COLOR = pygame.color.THECOLORS["red"]
JOINT_RADIUS = 5

skeleton_detected = False

def post_frame(frame):
    global skeleton_detected
    try:
        skeletons = [skeleton for skeleton in frame.SkeletonData 
                     if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED]
        
        if skeletons:
            skeleton_detected = True
            print("Esqueleto(s) detectado(s)!")
            pygame.event.post(
                pygame.event.Event(KINECTEVENT, skeletons=skeletons)
            )
        else:
            skeleton_detected = False
            print("No se detecta esqueleto.")

    except Exception as e:
        print(f"Error en post_frame: {e}")
        traceback.print_exc()

def draw_joints(skeletons):
    try:
        for skeleton in skeletons:
            for joint_id, joint in enumerate(skeleton.SkeletonPositions):
                if joint.x != 0 and joint.y != 0 and joint.z != 0:
                    x = int(joint.x * WINDOW_SIZE[0]) + WINDOW_SIZE[0] // 2
                    y = int(-joint.y * WINDOW_SIZE[1]) + WINDOW_SIZE[1] // 2
                    pygame.draw.circle(screen, JOINT_COLOR, (x, y), JOINT_RADIUS)
                    print(f"Joint ID: {joint_id}, Posición: ({x}, {y})")
    except Exception as e:
        print(f"Error en draw_joints: {e}")
        traceback.print_exc()

def main():
    global screen, skeleton_detected
    pygame.init()

    print("Inicializando PyGame...")
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
    pygame.display.set_caption('Juego Kinect con Python')
    print("PyGame Inicializado.")

    window = gw.getWindowsWithTitle('Juego Kinect con Python')[0]
    window.moveTo(0, 0)

    print("Inicializando Kinect...")
    try:
        with nui.Runtime() as kinect:
            print("Kinect Inicializado.")
            kinect.skeleton_engine.enabled = True
            print("Seguimiento de esqueleto habilitado.")

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
                            print("Frame del esqueleto recibido.")
                            current_skeletons = event.skeletons

                    screen.fill(pygame.color.THECOLORS["black"])
                    draw_joints(current_skeletons)
                    pygame.display.flip()
                    clock.tick(60)  # Limita el bucle a 60 FPS
                except Exception as e:
                    print(f"Error en el bucle principal: {e}")
                    traceback.print_exc()
                    continue

    except Exception as e:
        print(f"Error al inicializar Kinect: {e}")
        traceback.print_exc()

    print("Saliendo del juego...")

if __name__ == '__main__':
    print("Iniciando seguimiento de esqueleto con Kinect...")
    try:
        main()
    except Exception as e:
        print(f"Error crítico: {e}")
        traceback.print_exc()
    finally:
        print("Programa terminado.")
        pygame.quit()
        sys.exit()

