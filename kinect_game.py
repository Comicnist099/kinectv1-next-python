import pygame
import pygame.color
from pykinect import nui
import pygetwindow as gw  # Importar la librería para manipular las ventanas
import time

KINECTEVENT = pygame.USEREVENT
WINDOW_SIZE = 640, 480

# Colores para dibujar el esqueleto
SKELETON_COLOR = pygame.color.THECOLORS["red"]
JOINT_RADIUS = 10

def post_frame(frame):
    """Obtiene eventos del esqueleto del dispositivo Kinect y los publica en la cola de eventos de PyGame."""
    try:
        pygame.event.post(
            pygame.event.Event(KINECTEVENT, skeletons=frame.SkeletonData)
        )
        
        # Imprimir si se detecta un esqueleto o no
        skeleton_detected = False
        for skeleton in frame.SkeletonData:
            if skeleton.eTrackingState == nui.SkeletonTrackingState.TRACKED:
                skeleton_detected = True
                print("Esqueleto detectado!")

                # Dibujar el esqueleto en la pantalla
                draw_skeleton(skeleton)
        
        if not skeleton_detected:
            print("No se detecta esqueleto.")

    except Exception as e:
        print(f"Error: {e}")

def draw_skeleton(skeleton):
    """Dibuja el esqueleto en la pantalla."""
    # Dibujar articulaciones
    for joint_id in range(nui.JointId.Count):
        joint = skeleton.SkeletonPositions[joint_id]
        if joint.x != 0 and joint.y != 0 and joint.z != 0:  # Verificar que la articulación esté dentro del campo de visión
            x = int(joint.x * WINDOW_SIZE[0])
            y = int(joint.y * WINDOW_SIZE[1])
            pygame.draw.circle(screen, SKELETON_COLOR, (x + 320, -1 * y + 100), JOINT_RADIUS)
            print(f"Joint ID: {joint_id}, Posición: ({x}, {y})")

    # Dibujar las conexiones entre articulaciones
    draw_bones(skeleton)

def draw_bones(skeleton):
    """Dibuja las conexiones (huesos) entre las articulaciones del esqueleto."""
    # Definir las conexiones entre articulaciones (huesos)
    bones = [
        (nui.JointId.Head, nui.JointId.ShoulderCenter),
        (nui.JointId.ShoulderCenter, nui.JointId.ShoulderLeft),
        (nui.JointId.ShoulderCenter, nui.JointId.ShoulderRight),
        (nui.JointId.ShoulderCenter, nui.JointId.Spine),
        (nui.JointId.Spine, nui.JointId.HipCenter),
        (nui.JointId.HipCenter, nui.JointId.HipLeft),
        (nui.JointId.HipCenter, nui.JointId.HipRight),
        (nui.JointId.ShoulderLeft, nui.JointId.ElbowLeft),
        (nui.JointId.ElbowLeft, nui.JointId.WristLeft),
        (nui.JointId.WristLeft, nui.JointId.HandLeft),
        (nui.JointId.ShoulderRight, nui.JointId.ElbowRight),
        (nui.JointId.ElbowRight, nui.JointId.WristRight),
        (nui.JointId.WristRight, nui.JointId.HandRight),
        (nui.JointId.HipLeft, nui.JointId.KneeLeft),
        (nui.JointId.KneeLeft, nui.JointId.AnkleLeft),
        (nui.JointId.AnkleLeft, nui.JointId.FootLeft),
        (nui.JointId.HipRight, nui.JointId.KneeRight),
        (nui.JointId.KneeRight, nui.JointId.AnkleRight),
        (nui.JointId.AnkleRight, nui.JointId.FootRight)
    ]

    # Dibujar las líneas entre las articulaciones correspondientes
    for bone in bones:
        joint0 = skeleton.SkeletonPositions[bone[0]]
        joint1 = skeleton.SkeletonPositions[bone[1]]
        
        if joint0.x != 0 and joint0.y != 0 and joint1.x != 0 and joint1.y != 0:
            x0 = int(joint0.x * WINDOW_SIZE[0])
            y0 = int(joint0.y * WINDOW_SIZE[1])
            x1 = int(joint1.x * WINDOW_SIZE[0])
            y1 = int(joint1.y * WINDOW_SIZE[1])
            pygame.draw.line(screen, SKELETON_COLOR, (x0, y0), (x1, y1), 2)

def main():
    """Inicializa y ejecuta el juego."""
    pygame.init()

    # Inicializar PyGame
    print("Inicializando PyGame...")
    global screen
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 16)
    pygame.display.set_caption('Juego Kinect con Python')
    print("PyGame Inicializado.")

    # Obtener la ventana de Pygame y moverla a la esquina superior izquierda
    window = gw.getWindowsWithTitle('Juego Kinect con Python')[0]
    window.moveTo(0, 0)  # Mover la ventana a la esquina superior izquierda de la pantalla

    print("Inicializando Kinect...")
    with nui.Runtime() as kinect:
        print("Kinect Inicializado.")
        kinect.skeleton_engine.enabled = True
        print("Seguimiento de esqueleto habilitado.")
        
        kinect.skeleton_frame_ready += post_frame
        
        # Bucle principal del juego
        while True:
            event = pygame.event.wait()

            if event.type == pygame.QUIT:
                print("Saliendo del juego...")
                break
            elif event.type == KINECTEVENT:
                print("Frame del esqueleto recibido.")
                # Limpiar la pantalla antes de dibujar el esqueleto
                pass

            pygame.display.flip()
            screen.fill(pygame.color.THECOLORS["black"])


if __name__ == '__main__':
    print("Iniciando seguimiento de esqueleto con Kinect...")
    main()
    print("Programa terminado.")
