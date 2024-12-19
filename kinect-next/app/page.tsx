'use client'; // Directiva para marcar este componente como cliente

import { useEffect, useRef, useState } from "react";
import Matter from "matter-js";

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [points, setPoints] = useState<{ x: number; y: number }[]>([]); // Guardar puntos recibidos

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");

    if (!canvas || !ctx) return;

    // Configurar WebSocket
    const socket = new WebSocket("ws://localhost:9001");

    // Inicializar Matter.js
    const { Engine, Render, World, Bodies, Body, Events } = Matter;
    const engine = Engine.create();
    const world = engine.world;

    // Crear renderizador de Matter.js
    const render = Render.create({
      element: canvas,
      engine: engine,
      options: {
        width: 640,
        height: 480,
        wireframes: false, // Desactiva los contornos
      },
    });

    // Iniciar el motor y el renderizador
    Engine.run(engine);
    Render.run(render);

    // Crear la pelota que caerá
    const ball = Bodies.circle(320, 50, 20, {
      restitution: 0.8,  // Rebote
      friction: 0.1,     // Fricción
      density: 0.04      // Densidad
    });
    World.add(world, ball);

    // Función para limpiar el lienzo
    const clearCanvas = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    };

    // Función para actualizar los puntos recibidos a través del WebSocket
    const updateBodies = (data: Record<string, { x: number; y: number }>) => {
      // Primero, limpiar el lienzo
      clearCanvas();

      // Recorrer los joints recibidos
      const updatedPoints = Object.keys(data).map((joint) => {
        const { x, y } = data[joint];
        return { x, y };
      });

      // Actualizar el estado con los nuevos puntos
      setPoints(updatedPoints);

      // Dibujar los puntos
      updatedPoints.forEach((point) => {
        ctx.beginPath();
        ctx.arc(point.x, point.y, 5, 0, Math.PI * 2); // Radio de 5 px
        ctx.fillStyle = "red"; // Color de los puntos
        ctx.fill();
        ctx.closePath();
      });

      // Dibujar la pelota en el lienzo
      ctx.beginPath();
      ctx.arc(ball.position.x, ball.position.y, 20, 0, Math.PI * 2);
      ctx.fillStyle = "blue";
      ctx.fill();
      ctx.closePath();
    };

    // Manejar mensajes del WebSocket
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      updateBodies(data); // Actualizar los puntos con los nuevos datos
    };

    socket.onopen = () => console.log("Conexión WebSocket abierta");
    socket.onerror = (error) => console.error("Error en WebSocket:", error);
    socket.onclose = () => console.log("Conexión WebSocket cerrada");

    // Cleanup al desmontar
    return () => {
      socket.close();
    };
  }, []);

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <canvas
          ref={canvasRef}
          width={640}
          height={480}
          className="border border-gray-400"
        />
      </main>
    </div>
  );
}
