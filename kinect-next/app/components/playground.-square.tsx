'use client';

import { useEffect, useRef } from 'react';
import Matter, { Engine, Render, World, Bodies, Runner } from 'matter-js';

const PhysicsSimulation = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const engineRef = useRef<Matter.Engine | null>(null);
  const renderRef = useRef<Matter.Render | null>(null);
  const runnerRef = useRef<Matter.Runner | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Create engine
    const engine = Engine.create({
      gravity: { x: 0, y: 1, scale: 0.001 } // Adjust gravity
    });
    engineRef.current = engine;

    // Create renderer
    const render = Render.create({
      canvas: canvasRef.current,
      engine: engine,
      options: {
        width: 640,
        height: 480,
        wireframes: false,
        background: '#f0f0f0'
      }
    });
    renderRef.current = render;

    // Create runner
    const runner = Runner.create();
    runnerRef.current = runner;

    // Create ground
    const ground = Bodies.rectangle(320, 460, 640, 60, { 
      isStatic: true,
      render: { fillStyle: '#8B4513' }
    });

    // Add ground to the world
    World.add(engine.world, [ground]);

    // Start the renderer
    Render.run(render);

    // Start the runner
    Runner.run(runner, engine);

    // Function to add a new square
    const addSquare = () => {
      if (engineRef.current) {
        const square = Bodies.rectangle(
          Math.random() * 640, // Random x position
          -30, // Start above the canvas
          30,
          30,
          {
            restitution: 0.6,
            friction: 0.1,
            render: { fillStyle: '#0000FF' }
          }
        );
        World.add(engineRef.current.world, square);
      }
    };

    // Add squares every 5 seconds
    const intervalId = setInterval(addSquare, 5000);

    // Cleanup function
    return () => {
      clearInterval(intervalId);
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
        width={640}
        height={480}
        style={{ border: '1px solid #000' }}
      />
    </div>
  );
};

export default PhysicsSimulation;

