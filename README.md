# 🤖 Bybit P2P Bot LATAM

> Bot automatizado para gestion de operaciones P2P en Bybit LATAM

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Bybit](https://img.shields.io/badge/Exchange-Bybit-orange.svg)](https://bybit.com)
[![Telegram](https://img.shields.io/badge/Notificaciones-Telegram-blue.svg)](https://telegram.org)
[![LATAM](https://img.shields.io/badge/Region-LATAM-green.svg)](#)

---

## 📌 Descripcion

Bot en Python que automatiza el monitoreo de ordenes P2P en Bybit para merchants de America Latina. Detecta nuevas ordenes, rastrea cambios de estado y envia notificaciones en tiempo real via Telegram. Incluye generacion de reportes diarios de operaciones.

---

## ✨ Funcionalidades

- 🔔 **Alertas en tiempo real** de nuevas ordenes P2P via Telegram
- 📊 **Monitoreo continuo** de ordenes activas y cambios de estado
- 💸 **Alerta de liberacion** cuando el comprador marca el pago como enviado
- ⚠️ **Alerta de apelacion** cuando una orden entra en disputa
- 📈 **Reporte diario** automatico con estadisticas de operaciones
- 🌎 **Soporte multi-moneda** para toda LATAM (VES, COP, ARS, PEN, CLP, MXN)
- 🛡️ **Autenticacion HMAC-SHA256** con la API oficial de Bybit
- 📁 **Logs detallados** de todas las operaciones

---

## 📂 Estructura del Proyecto

```
bybit-p2p-bot-latam/
├── bot.py              # Bot principal - loop y logica central
├── bybit_api.py        # Cliente API Bybit P2P con autenticacion HMAC
├── order_manager.py    # Gestion de ordenes, estadisticas y reportes
├── notifier.py         # Notificaciones Telegram con emojis y formato
├── config.py           # Configuracion central via variables de entorno
├── .env.example        # Plantilla de configuracion (copiar como .env)
├── requirements.txt    # Dependencias Python
└── .gitignore          # Archivos ignorados por Git
```

---

## 🚀 Instalacion y Configuracion

### 1. Clonar el repositorio

```bash
git clone https://github.com/efrenvzpiva-spec/bybit-p2p-bot-latam.git
cd bybit-p2p-bot-latam
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales:

```env
# API de Bybit (obtener en bybit.com > API Management)
BYBIT_API_KEY=tu_api_key
BYBIT_API_SECRET=tu_api_secret

# Bot de Telegram
TELEGRAM_BOT_TOKEN=token_de_tu_bot
TELEGRAM_CHAT_ID=tu_chat_id

# Configuracion regional LATAM
FIAT_CURRENCY=VES
TIMEZONE=America/Caracas
```

### 4. Obtener credenciales de Bybit

1. Ir a **Bybit > API Management**
2. Crear nueva API Key con permisos de **P2P Trading**
3. Copiar API Key y Secret en el `.env`

### 5. Configurar bot de Telegram

1. Buscar `@BotFather` en Telegram
2. Enviar `/newbot` y seguir instrucciones
3. Copiar el token al `.env`
4. Obtener tu chat_id: `https://api.telegram.org/bot<TOKEN>/getUpdates`

---

## ▶️ Uso

```bash
python bot.py
```

El bot enviara un mensaje de inicio a Telegram y comenzara a monitorear.

---

## 📲 Notificaciones Telegram

| Evento | Descripcion |
|--------|-------------|
| 🔔 Nueva orden | Orden P2P creada |
| 💸 Pago recibido | Comprador marco pago - liberar fondos |
| ⚠️ Apelacion | Orden en disputa - accion inmediata |
| ✅ Completada | Orden finalizada exitosamente |
| 📊 Reporte diario | Estadisticas de operaciones del dia |
| 🚨 Error | Alerta de error critico en el bot |

---

## 🌎 Paises LATAM Soportados

| Pais | Moneda | FIAT_CURRENCY |
|------|--------|---------------|
| Venezuela | Bolivar | VES |
| Colombia | Peso | COP |
| Argentina | Peso | ARS |
| Peru | Sol | PEN |
| Chile | Peso | CLP |
| Mexico | Peso | MXN |

---

## ⚙️ Configuracion Avanzada

| Variable | Default | Descripcion |
|----------|---------|-------------|
| CHECK_INTERVAL | 30 | Segundos entre verificaciones |
| UPDATE_INTERVAL | 60 | Segundos entre chequeos de actualizacion |
| REPORT_TIME | 23:00 | Hora del reporte diario |
| MIN_ALERT_AMOUNT | 0 | Monto minimo para alertas (USDT) |
| BYBIT_TESTNET | false | Usar testnet para pruebas |

---

## 🛡️ Seguridad

- **NUNCA** subas el archivo `.env` a GitHub
- El `.gitignore` ya excluye el `.env` automaticamente
- Las API keys se manejan solo via variables de entorno
- Usar permisos minimos necesarios en la API de Bybit

---

## 📝 Licencia

Proyecto desarrollado por **efrenvzpiva-spec** para uso en operaciones P2P Bybit LATAM.

---

*Bot Bybit P2P LATAM v1.0.0*
