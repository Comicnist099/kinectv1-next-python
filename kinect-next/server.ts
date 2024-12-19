"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var ws_1 = require("ws");
var wss = new ws_1.WebSocketServer({ port: 9001 });
console.log('Servidor WebSocket iniciado en ws://127.0.0.1:9001');

// Tiempo de espera en milisegundos para retrasar el envío de datos (ej. 200ms)
const DEBOUNCE_TIME = 200;
let timeout: NodeJS.Timeout | null = null;

wss.on('connection', function (ws) {
    console.log('Cliente conectado al WebSocket');
    
    // Variables para almacenar los datos recibidos antes de enviarlos
    let jointsData: Record<string, any> | null = null;

    ws.on('message', function (data) {
        try {
            // Parsear los datos recibidos
            jointsData = JSON.parse(data.toString());
            console.log('Datos recibidos de los joints:', jointsData);

            // Si ya existe un timeout pendiente, lo limpiamos
            if (timeout) {
                clearTimeout(timeout);
            }

            // Establecemos un nuevo timeout para enviar los datos después del tiempo de debounce
            timeout = setTimeout(() => {
                if (jointsData) {
                    // Reenviar los datos a todos los clientes conectados
                    wss.clients.forEach(function (client) {
                        if (client.readyState === ws.OPEN) {
                            client.send(JSON.stringify(jointsData));
                        }
                    });
                    console.log('Datos enviados a todos los clientes');
                    jointsData = null; // Limpiar datos después de enviarlos
                }
            }, DEBOUNCE_TIME); // Retraso de 200ms (puedes ajustar este valor)
        } catch (error) {
            console.error('Error al procesar los datos:', error);
        }
    });

    ws.on('close', function () {
        console.log('Cliente desconectado');
    });

    // Enviar un mensaje de bienvenida al nuevo cliente
    ws.send(JSON.stringify({ message: 'Conexión WebSocket establecida' }));
});
