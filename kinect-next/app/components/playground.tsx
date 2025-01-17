"use client"; // Add this line at the top of the file

import React, { useEffect, useRef, useState } from 'react';
import Matter, { IChamferableBodyDefinition } from 'matter-js';

const PI = Math.PI;
const { Engine, Render, World, Bodies, Runner } = Matter;

const Playground: React.FC = () => {
  const canvasRef = useRef<HTMLDivElement | null>(null);
  const [balls, setBalls] = useState<Matter.Body[]>([]); // State to manage balls
  const engineRef = useRef<any>(null); // Ref for Matter.js engine
  const renderRef = useRef<any>(null);
  const runnerRef = useRef<any>(null);
  const boundariesRef = useRef<Matter.Body[]>([]);

  useEffect(() => {
    const engine = Engine.create();
    const render = Render.create({
      element: canvasRef.current as HTMLElement,
      engine,
      options: {
        wireframes: false,
        showAngleIndicator: true,
        showVelocityIndicator: true,
      },
    });

    const runner = Runner.create();
    Runner.run(runner, engine);

    engineRef.current = engine; // Store engine in ref for later use

    const boxA = Bodies.circle(300, 200, 15, { restitution: 0.8, friction: 0.1, mass: 1 });
    const boxB = Bodies.circle(350, 50, 20, { restitution: 0.8, friction: 0.1, mass: 1 });
    const ground = Bodies.rectangle(400, 610, 810, 60, { isStatic: true });

    const boundaryOptions: IChamferableBodyDefinition = {
      isStatic: true,
      friction: 1,
      restitution: 0.9,
      render: {
        fillStyle: 'red',
        strokeStyle: 'blue',
        lineWidth: 1,
      },
    };

    const setupBoundaries = (width: number, height: number) => {
      boundariesRef.current.push(
        Bodies.rectangle((width * 1) / 3, height / 4, width / 2, 10, {
          ...boundaryOptions,
          angle: PI / 12,
        })
      );
      boundariesRef.current.push(
        Bodies.rectangle((width * 1) / 3, height / 1.5, width / 2, 10, {
          ...boundaryOptions,
          angle: PI / 12,
        })
      );
      boundariesRef.current.push(
        Bodies.rectangle((width * 2) / 3, height / 2.2, width / 2, 10, {
          ...boundaryOptions,
          angle: -PI / 12,
        })
      );
      World.add(engine.world, boundariesRef.current);
    };

    setupBoundaries(700, 600);

    World.add(engine.world, [boxA, boxB, ground]);

    Engine.run(engine);
    Render.run(render);

    return () => {
      Engine.clear(engine);
      Render.stop(render);
      Runner.stop(runner);
    };
  }, []);

//   const addSquareInterval = setInterval(() => {
// if (!engineRef.current) return; // Ensure engine is initialized

//     const newBall = Bodies.circle(Math.random() * 700, Math.random() * 400, 15, {
//       restitution: 0.8,
//       friction: 0.1,
//       mass: 1,
//     });

//     setBalls((prevBalls) => {
//       World.add(engineRef.current.world, newBall); // Add the new ball to the Matter.js world
//       return [...prevBalls, newBall]; // Add the new ball to the state
//     });
//   }, 1000);
  const addBall = () => {
    if (!engineRef.current) return; // Ensure engine is initialized

    const newBall = Bodies.circle(Math.random() * 700, Math.random() * 400, 15, {
      restitution: 0.8,
      friction: 0.1,
      mass: 1,
    });

    setBalls((prevBalls) => {
      World.add(engineRef.current.world, newBall); // Add the new ball to the Matter.js world
      return [...prevBalls, newBall]; // Add the new ball to the state
    });
  };

  return (
    <div style={{ position: 'relative', height: '100vh' }}>
      {/* Button at the top */}
      <button
        onClick={addBall}
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

      {/* Canvas where the simulation occurs */}
      <div ref={canvasRef} style={{ width: '100%', height: 'calc(100vh - 60px)' }} />
    </div>
  );
};

export default Playground;
