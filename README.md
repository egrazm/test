# Protocolo del Chat (TCP, delimitado por líneas)

- Transporte: TCP (IPv4).
- Codificación: UTF-8.
- Delimitador de mensajes: **línea** terminada en `\n`.
- Reglas del mensaje:
  - No puede estar vacío (ni solo espacios).
  - Longitud máxima (tras recortar `\r\n`): **256** caracteres.
- Comportamiento del servidor:
  - Al recibir un mensaje **válido**: lo retransmite (broadcast) a **todos** los clientes conectados (incluye al emisor).
  - Al recibir un mensaje **inválido**: responde solo al emisor con:
    ```
    ERR Invalid message\n
    ```
  - Si un cliente se desconecta, el servidor continúa funcionando y atiende al resto.

Ejemplos:
- Cliente → Servidor: `hola a todos\n`
- Servidor → Todos: `hola a todos\n`
- Cliente → Servidor: `   \n`
- Servidor → Emisor: `ERR Invalid message\n`
