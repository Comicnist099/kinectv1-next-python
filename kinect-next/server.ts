import { WebSocketServer } from 'ws';

const wss = new WebSocketServer({ port: 9001 });

console.log('Servidor WebSocket iniciado en ws://127.0.0.1:9001');

wss.on('connection', (ws) => {
  console.log('Cliente conectado al WebSocket');

  ws.on('message', (data) => {
    try {
      const jointsData = JSON.parse(data.toString());
      console.log('Datos recibidos de los joints:', jointsData);

      // Reenviar los datos a todos los clientes conectados
      wss.clients.forEach(client => {
        if (client.readyState === ws.OPEN) {
          client.send(JSON.stringify(jointsData));
        }
      });
    } catch (error) {
      console.error('Error al procesar los datos:', error);
    }
  });

  ws.on('close', () => {
    console.log('Cliente desconectado');
  });

  ws.send(JSON.stringify({ message: 'Conexión WebSocket establecida' }));
});
