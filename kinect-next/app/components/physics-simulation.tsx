'use client';

import { useEffect, useRef, useState } from 'react';
import Matter from 'matter-js';

const { Engine, Render, World, Bodies, Runner, Body, Vector, Events } = Matter;

interface JointData {
  x: number;
  y: number;
}

const PhysicsSimulation = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [squares, setSquares] = useState<Matter.Body[]>([]);
  const [jointPositions, setJointPositions] = useState<Record<string, JointData>>({});
  const engineRef = useRef<Matter.Engine | null>(null);
  const renderRef = useRef<Matter.Render | null>(null);
  const runnerRef = useRef<Matter.Runner | null>(null);
  const platformRef = useRef<Matter.Body | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Establece el tamaño del lienzo
    const canvasWidth = 1280; // Nuevo ancho
    const canvasHeight = 960; // Nueva altura

    // Calcula el factor de escala
    const scaleFactorX = canvasWidth / 640; // Factor de escala horizontal
    const scaleFactorY = canvasHeight / 480; // Factor de escala vertical

    // Crear el motor de Matter.js
    const engine = Engine.create({
      gravity: { x: 0, y: 1, scale: 0.001 }
    });
    engineRef.current = engine;

    // Crear el renderizador de Matter.js
    const render = Render.create({
      canvas: canvasRef.current,
      engine: engine,
      options: {
        width: canvasWidth,
        height: canvasHeight,
        wireframes: false,
        background: '#f0f0f0'
      }
    });
    renderRef.current = render;

    // Crear el runner de Matter.js
    const runner = Runner.create();
    runnerRef.current = runner;

    // Crear el suelo
    const ground = Bodies.rectangle(640 / 2, 960 - 60, canvasWidth, 60, { 
      isStatic: true,
      render: { fillStyle: '#8B4513' }
    });

    const initialBallPositions = Array(20).fill({ x: 0, y: 0 });

    const staticBalls: Matter.Body[] = initialBallPositions.map((pos) => {
      return Bodies.circle(pos.x, pos.y, 10, {
        isStatic: false, // Establecer isStatic en false para que el círculo caiga
        restitution: 0.5,
        friction: 0.1,
        density: 0.05,
        render: { fillStyle: 'red' }
      });
    });

    // Crear la plataforma
    const platform = Bodies.rectangle(canvasWidth / 2, 400, 500, 50, { 
      isStatic: true,
      render: { fillStyle: 'green' }
    });
    platformRef.current = platform;

    // Agregar todos los cuerpos al mundo de Matter.js
    World.add(engine.world, [ground, ...staticBalls, platform]);

    // Iniciar el renderizador
    Render.run(render);

    // Iniciar el runner
    Runner.run(runner, engine);

    // Conexión WebSocket
    const socket = new WebSocket('ws://localhost:9001');

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const updatedPositions: Record<string, JointData> = {};

      Object.keys(data).forEach((joint) => {
        updatedPositions[joint] = {
          x: data[joint].x * scaleFactorX, // Escalar la coordenada X
          y: data[joint].y * scaleFactorY, // Escalar la coordenada Y
        };
      });

      setJointPositions(updatedPositions);

      if (updatedPositions['joint_2'] && updatedPositions['joint_3'] && platformRef.current) {
        const joint2 = updatedPositions['joint_2'];
        const joint3 = updatedPositions['joint_3'];

        // Calcular el ángulo entre joint_2 y joint_3
        const dx = joint3.x - joint2.x;
        const dy = joint3.y - joint2.y;
        const angle = Math.atan2(dy, dx);

        // Calcular la inclinación (0 grados es vertical)
        const inclination = angle - Math.PI / 2;

        // Mover la plataforma en función de la posición de joint_3
        Body.setPosition(platformRef.current, {
          x: joint3.x,
          y: joint3.y + 50, // Desplazar la plataforma un poco por debajo de joint_3
        });

        // Rotar la plataforma según la inclinación calculada
        Body.setAngle(platformRef.current, inclination);

        // Dibujar una línea entre joint_2 y joint_3
        if (renderRef.current) {
          const { context } = renderRef.current;
          context.beginPath();
          context.moveTo(joint2.x, joint2.y);
          context.lineTo(joint3.x, joint3.y);
          context.strokeStyle = 'blue';
          context.lineWidth = 2;
          context.stroke();
        }

        // Actualizar el texto de la inclinación
        const rotationHead = document.querySelector('#rotation_head');
        if (rotationHead) {
          rotationHead.textContent = `Inclination: ${(inclination * 180 / Math.PI).toFixed(2)}°`;
        }
      }
    };

    socket.onopen = () => console.log('WebSocket connection opened');
    socket.onerror = (error) => console.error('WebSocket error:', error);
    socket.onclose = () => console.log('WebSocket connection closed');

    // Función para agregar un nuevo círculo
    const addCircle = () => {
      if (engineRef.current) {
        const circle = Bodies.circle(
          Math.random() * canvasWidth,
          -30,
          20,
          {
            restitution: 1,
            friction: 3,
            render: { fillStyle: '#0000FF' }
          }
        );
        World.add(engineRef.current.world, circle);
        setSquares((prevSquares) => [...prevSquares, circle]);
      }
    };

    // Agregar círculos cada 1 segundo
    const intervalId = setInterval(addCircle, 1000);

    // Escuchar colisiones para eliminar círculos cuando tocan el suelo
    Events.on(engine, 'collisionStart', (event) => {
      event.pairs.forEach((pair) => {
        const { bodyA, bodyB } = pair;
        // Verificar si el cuerpo A o B es un círculo y si colisiona con el suelo
        if (
          (bodyA === ground && bodyB.circleRadius) || // Si bodyB es un círculo y colisiona con el suelo
          (bodyB === ground && bodyA.circleRadius) // Si bodyA es un círculo y colisiona con el suelo
        ) {
          const bodyToRemove = bodyA === ground ? bodyB : bodyA;
          World.remove(engine.world, bodyToRemove); // Eliminar el círculo
          setSquares((prevSquares) => prevSquares.filter((square) => square !== bodyToRemove)); // Actualizar el estado
        }
      });
    });

    // Función de limpieza
    return () => {
      clearInterval(intervalId);
      socket.close();
      if (renderRef.current) Render.stop(renderRef.current);
      if (runnerRef.current) Runner.stop(runnerRef.current);
      if (engineRef.current) World.clear(engineRef.current.world, false);
      if (engineRef.current) Engine.clear(engineRef.current);
    };
  }, []);

  return (
    <div style={{ position: 'relative', height: '100vh' }}>
      <canvas
        ref={canvasRef}
        width={1280} // Tamaño mayor del lienzo
        height={960} // Tamaño mayor del lienzo
        style={{ border: '1px solid #000' }}
      />
      <h1 id="rotation_head" style={{ position: 'absolute', top: '10px', left: '10px', color: 'black' }}></h1>
    </div>
  );
};

export default PhysicsSimulation;
