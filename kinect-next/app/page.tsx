"use client";

import { useEffect, useRef } from "react";

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");

    if (!canvas || !ctx) return;

    // Configurar WebSocket
    const socket = new WebSocket("ws://localhost:9001");

    // Limpia el lienzo
    const clearCanvas = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    };

    // Dibujar puntos
    const drawPoints = (data: Record<string, { x: number; y: number }>) => {
      clearCanvas();
      Object.keys(data).forEach((joint) => {
        const { x, y } = data[joint];
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fillStyle = "red";
        ctx.fill();
        ctx.closePath();
      });
    };

    // Manejar mensajes de WebSocket
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      drawPoints(data);
    };

    socket.onopen = () => console.log("Conexión WebSocket abierta");
    socket.onerror = (error) => console.error("Error en WebSocket:", error);
    socket.onclose = () => console.log("Conexión WebSocket cerrada");


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
