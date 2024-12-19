'use client'; // Directiva para marcar este componente como cliente

import { useEffect, useRef, useState } from 'react';
import Matter, { Body } from 'matter-js';

const { Engine, World, Bodies, Runner } = Matter;

const PhysicsSimulation = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [balls, setBalls] = useState<Matter.Body[]>([]); // Lista de bolas dinámicas (azules)
  const [jointPositions, setJointPositions] = useState<Record<string, { x: number, y: number }>>({}); // Estado para las posiciones de los joints
  const engineRef = useRef<any>(null); // Ref para el motor de Matter.js
  const runnerRef = useRef<any>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    // Crear motor de física
    const engine = Engine.create();
    const world = engine.world;

    // Crear el suelo estático
    const ground = Bodies.rectangle(320, 460, 640, 60, { isStatic: true });

    // Crear bolitas estáticas (las posiciones se actualizarán desde los datos del WebSocket)
    const initialBallPositions = [
      { x: 295, y: 546 },
      { x: 428, y: 285 },
      { x: 309, y: 517 },
      { x: 369, y: 399 },
      { x: 394, y: 227 },
      { x: 365, y: 179 },
      { x: 388, y: 261 },
      { x: 477, y: 248 },
      { x: 401, y: 142 },
      { x: 414, y: 105 },
      { x: 486, y: 260 },
      { x: 440, y: 191 },
      { x: 471, y: 219 },
      { x: 453, y: 193 },
      { x: 420, y: 241 },
      { x: 451, y: 317 },
      { x: 470, y: 218 },
      { x: 429, y: 159 },
      { x: 412, y: 271 },
      { x: 419, y: 269 },
    ];

    // Crear las bolitas estáticas con posiciones iniciales
    const staticBalls: Matter.Body[] = initialBallPositions.map((pos) => {
      return Bodies.circle(pos.x, pos.y, 10, {
        isStatic: true, // Hacerlas estáticas
        restitution: 0.5,  // Rebote
        friction: 0.1,     // Fricción
        density: 0.05,     // Densidad
      });
    });

    // Agregar las bolitas estáticas y el suelo al mundo de Matter.js
    World.add(world, [ground, ...staticBalls]);

    engineRef.current = engine; // Guardamos la referencia al motor
    runnerRef.current = Runner.create();

    // Configurar WebSocket
    const socket = new WebSocket('ws://localhost:9001');

    // WebSocket: Manejar mensajes y actualizar posiciones
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // Obtener las posiciones de los joints
      const updatedPositions: Record<string, { x: number, y: number }> = {};

      Object.keys(data).forEach((joint) => {
        const { x, y } = data[joint];
        updatedPositions[joint] = { x, y };
      });

      // Actualizar las posiciones de los joints en el estado
      setJointPositions(updatedPositions);

      // Actualizar las posiciones de las bolitas en el mundo de Matter.js
      staticBalls.forEach((ball, index) => {
        const jointKey = `joint_${index}`; // Usamos el índice de la bola para encontrar el joint correspondiente
        if (updatedPositions[jointKey]) {
          // Si hay datos para ese joint, actualizamos la posición de la bolita
          Body.setPosition(ball, updatedPositions[jointKey]);
        }
      });
    };

    socket.onopen = () => console.log('Conexión WebSocket abierta');
    socket.onerror = (error) => console.error('Error en WebSocket:', error);
    socket.onclose = () => console.log('Conexión WebSocket cerrada');

    // Función para limpiar el canvas
    const clearCanvas = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    };

    // Dibujar objetos en el canvas manualmente
    const drawObjects = () => {
      clearCanvas();

      // Dibujar las bolitas estáticas con las posiciones actualizadas
      staticBalls.forEach((body) => {
        ctx.beginPath();
        ctx.arc(body.position.x, body.position.y, 10, 0, Math.PI * 2);
        ctx.fillStyle = 'red'; // Color de las bolitas
        ctx.fill();
        ctx.closePath();
      });

      // Dibujar las bolas dinámicas (azules)
      balls.forEach((body) => {
        ctx.beginPath();
        ctx.arc(body.position.x, body.position.y, 15, 0, Math.PI * 2);
        ctx.fillStyle = 'blue'; // Color de las bolas dinámicas
        ctx.fill();
        ctx.closePath();
      });
    };

    // Iniciar motor y renderizado
    Runner.run(runnerRef.current, engine);

    // Animación de actualización
    const animate = () => {
      Engine.update(engine);
      drawObjects(); // Dibujamos manualmente
      requestAnimationFrame(animate);
    };

    animate();

    // Cleanup cuando el componente se desmonta
    return () => {
      socket.close();
      Engine.clear(engine);
      Runner.stop(runnerRef.current);
    };
  }, [balls]); // Dependencia para actualizar el canvas cuando cambian las bolas

  // Función para agregar una nueva bolita
  const addBall = () => {
    if (!engineRef.current) return; // Asegurarse de que el motor está inicializado

    const newBall = Bodies.circle(Math.random() * 640, Math.random() * 480, 15, {
      restitution: 0.8,
      friction: 0.1,
      mass: 1,
    });

    setBalls((prevBalls) => {
      World.add(engineRef.current.world, newBall); // Agregar la nueva bolita al mundo de Matter.js
      return [...prevBalls, newBall]; // Agregar la nueva bolita al estado
    });
  };

  return (
    <div style={{ position: 'relative', height: '100vh' }}>
      {/* Botón en la parte superior */}
      <button
        onClick={addBall} // Llamamos a la función `addBall` aquí
        style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          zIndex: 10,
          padding: '10px 20px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
        }}
      >
        Add Ball
      </button>

      {/* Canvas donde ocurre la simulación */}
      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        className="border border-gray-400"
      />
    </div>
  );
};

export default PhysicsSimulation;
