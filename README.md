# 🧠 Sock-it-to-Me Chat (Python Sockets Edition)

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/egrazm/test/ci.yml?branch=main&label=CI)
![Coverage](https://img.shields.io/badge/coverage-71%25-yellow)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

### 🧩 Descripción

**Sock-it-to-Me Chat** es un servidor de chat TCP simple, desarrollado en **Python puro con sockets**, para practicar:
- comunicación en tiempo real,  
- validación de mensajes,  
- pruebas unitarias e integración con `pytest`,  
- y principios de **Test-Driven Development (TDD)**.  

El proyecto incluye un servidor ejecutable, un cliente de consola interactivo y una suite de pruebas automatizadas con cobertura.

---

### ⚙️ Estructura del proyecto

```
chat_py_sockets/
│
├── src/
│   ├── server.py          # Lógica del servidor (acepta clientes, transmite mensajes)
│   ├── protocol.py        # Envoltura, envío y recepción de mensajes
│   └── validation.py      # Validación de entrada (TDD)
│
├── tests/
│   ├── unit/              # Pruebas unitarias
│   ├── integration/       # Pruebas de integración cliente-servidor
│   └── perf/              # (opcional) pruebas de rendimiento
│
├── client_cli.py          # Cliente CLI para probar manualmente
├── run_server.py          # Script ejecutable del servidor
├── requirements.txt       # Dependencias mínimas
└── pyproject.toml         # Configuración de pytest y cobertura
```

---

### 🚀 Ejecución manual

#### 1️⃣ Iniciar el servidor
```bash
python run_server.py
```
Ejemplo de salida:
```
[server] listening on 127.0.0.1:60060. Press Ctrl+C to stop.
```

#### 2️⃣ Conectarse con un cliente
En otra terminal:
```bash
python client_cli.py 127.0.0.1 60060
```

💬 Abrí varias terminales y escribí mensajes.  
El servidor los retransmitirá (broadcast) a todos los clientes conectados en tiempo real.

---

### 🧪 Pruebas automatizadas

#### Ejecutar todos los tests
```bash
pytest
```

#### Con reporte de cobertura
```bash
pytest --cov=src --cov-report=term-missing
```

#### Con límite de tiempo
```bash
pytest --timeout=5
```

---

### 🧰 Tecnologías y librerías

| Herramienta | Uso |
|--------------|-----|
| `socket` | Comunicación TCP entre clientes y servidor |
| `threading` | Manejo concurrente de conexiones |
| `pytest` | Pruebas unitarias e integración |
| `pytest-cov` | Métrica de cobertura |
| `pytest-timeout` | Evita bloqueos durante CI |
| `GitHub Actions` | Integración continua automática |

---

### ✅ Requerimientos del Challenge

| Módulo | Estado |
|--------|--------|
| Pruebas unitarias con TDD | ✅ |
| Servidor concurrente TCP | ✅ |
| Pruebas de integración multi-cliente | ✅ |
| Manejo de desconexiones inesperadas | ✅ |
| Ejecución manual (CLI + Server) | ✅ |
| Cobertura mínima 70% | ✅ (71%) |
| CI automatizado (GitHub Actions) | ✅ |
| Documentación y entrega final | ✅ |

---

### 🧑‍💻 Autor

**Elias Gonzalez (@egrazm)**  
Desarrollador Full Stack & entusiasta del aprendizaje basado en proyectos.  
Parte del ecosistema **Penguin Academy** 🐧

---

### 📜 Licencia

Este proyecto está bajo la licencia **MIT**.  
Puedes usarlo, modificarlo y compartirlo libremente dando el crédito correspondiente.

---

💬 *“El código bien probado no solo funciona, también enseña.”*  
