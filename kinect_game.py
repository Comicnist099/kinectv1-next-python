import pygame
import pygame.color
from pykinect import nui
import pygetwindow as gw
import sys
import traceback
import time

KINECTEVENT = pygame.USEREVENT
WINDOW_SIZE = 640, 480

JOINT_COLOR = pygame.color.THECOLORS["red"]
JOINT_RADIUS = 5

FONT_COLOR = pygame.color.THECOLORS["white"]
FONT_SIZE = 24

skeleton_detected = False
joint_0_coords = (0, 0)
last_detection_time = time.time()  # Marca de tiempo para la última detección

def post_frame(frame):
    """
    Procesa el cuadro del esqueleto y actualiza la detección.
    """
    global skeleton_detected, last_detection_time
    try:
        # Filtra los esqueletos que están siendo rastreados
        skeletons = [skeleton for skeleton in frame.SkeletonData
                     if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED]
        
        print(f"Frames procesados: {len(skeletons)} esqueletos detectados.")  # Verificación de esqueletos

        if skeletons:
            # Si se detecta un esqueleto, actualiza el estado
            if not skeleton_detected:
                print("Esqueleto(s) detectado(s)!")  # Imprime si detecta un esqueleto
            skeleton_detected = True
            last_detection_time = time.time()  # Actualiza la marca de tiempo de detección
            pygame.event.post(
                pygame.event.Event(KINECTEVENT, skeletons=skeletons)
            )
        else:
            # Si no se detecta esqueleto y ha pasado un tiempo considerable (más de 2 segundos)
            if time.time() - last_detection_time > 2 and skeleton_detected:
                skeleton_detected = False
                print("No se detecta esqueleto. Buscando nuevo esqueleto...")
                pygame.event.post(
                    pygame.event.Event(KINECTEVENT, skeletons=[])
                )
    except Exception as e:
        print(f"Error en post_frame: {e}")
        traceback.print_exc()


def draw_joints(skeletons):
    """
    Dibuja las articulaciones en la pantalla.
    """
    global joint_0_coords
    try:
        for skeleton in skeletons:
            for joint_id, joint in enumerate(skeleton.SkeletonPositions):
                if joint.x != 0 and joint.y != 0 and joint.z != 0:
                    x = int(joint.x * WINDOW_SIZE[0]) + WINDOW_SIZE[0] // 2
                    y = int(-joint.y * WINDOW_SIZE[1]) + WINDOW_SIZE[1] // 2
                    if joint_id == 0:  # Joint 0 (base del esqueleto)
                        joint_0_coords = (x, y)
                    pygame.draw.circle(screen, JOINT_COLOR, (x, y), JOINT_RADIUS)
    except Exception as e:
        print(f"Error en draw_joints: {e}")
        traceback.print_exc()


def draw_text(text, position):
    """
    Dibuja texto en la pantalla en una posición específica.
    """
    try:
        text_surface = font.render(text, True, FONT_COLOR)
        screen.blit(text_surface, position)
    except Exception as e:
        print(f"Error al dibujar texto: {e}")
        traceback.print_exc()

def main():
    global screen, font, skeleton_detected
    pygame.init()

    print("Inicializando PyGame...")
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
    pygame.display.set_caption('Juego Kinect con Python')
    font = pygame.font.Font(None, FONT_SIZE)
    print("PyGame Inicializado.")

    # Posicionar la ventana al inicio de la pantalla
    try:
        window = gw.getWindowsWithTitle('Juego Kinect con Python')[0]
        window.moveTo(0, 0)
    except Exception as e:
        print(f"Error al mover la ventana: {e}")

    print("Inicializando Kinect...")
    try:
        with nui.Runtime() as kinect:
            print("Kinect Inicializado.")
            kinect.skeleton_engine.enabled = True
            print("Seguimiento de esqueleto habilitado.")
             # Cambié el nombre de la función a `handle_skeleton_frame`
            kinect.skeleton_frame_ready += post_frame  # Escucha los eventos de Kinect
            clock = pygame.time.Clock()
            running = True
            current_skeletons = []

            while running:
                try:
                    # Procesar los eventos
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        elif event.type == KINECTEVENT:
                            current_skeletons = event.skeletons

                    # Limpia la pantalla
                    screen.fill(pygame.color.THECOLORS["black"])

                    # Dibuja las articulaciones
                    draw_joints(current_skeletons)

                    # Muestra el estado del esqueleto
                    skeleton_status = "Esqueleto Detectado" if skeleton_detected else "No se detecta Esqueleto"
                    draw_text(skeleton_status, (10, 10))

                    # Si no hay esqueleto, muestra "Buscando cuerpo..."
                    if not skeleton_detected:
                        searching_text = "Buscando cuerpo..."
                        draw_text(searching_text, (10, 40))

                    # Muestra las coordenadas del Joint 0
                    joint_0_text = f"Joint 0: {joint_0_coords}"
                    draw_text(joint_0_text, (10, 70))

                    # Muestra el texto de "Running"
                    running_text = "Running: ON" if running else "Running: OFF"
                    draw_text(running_text, (10, 100))

                    # Actualiza la pantalla
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
