"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var ws_1 = require("ws");
var wss = new ws_1.WebSocketServer({ port: 9001 });
console.log('Servidor WebSocket iniciado en ws://127.0.0.1:9001');
wss.on('connection', function (ws) {
    console.log('Cliente conectado al WebSocket');
    ws.on('message', function (data) {
        try {
            var jointsData_1 = JSON.parse(data.toString());
            console.log('Datos recibidos de los joints:', jointsData_1);
            // Reenviar los datos a todos los clientes conectados
            wss.clients.forEach(function (client) {
                if (client.readyState === ws.OPEN) {
                    client.send(JSON.stringify(jointsData_1));
                }
            });
        }
        catch (error) {
            console.error('Error al procesar los datos:', error);
        }
    });
    ws.on('close', function () {
        console.log('Cliente desconectado');
    });
    ws.send(JSON.stringify({ message: 'Conexión WebSocket establecida' }));
});
