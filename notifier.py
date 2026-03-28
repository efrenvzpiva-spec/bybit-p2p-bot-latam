#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo de notificaciones via Telegram para el Bot Bybit P2P LATAM.
Envia alertas de nuevas ordenes, actualizaciones y reportes diarios.
"""

import logging
import requests
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Envia notificaciones a Telegram via Bot API.
    """

    TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

    # Emojis para los mensajes
    EMOJI_NEW_ORDER = "🔔"
    EMOJI_COMPRA = "🟢"
    EMOJI_VENTA = "🔴"
    EMOJI_COMPLETED = "✅"
    EMOJI_CANCELLED = "❌"
    EMOJI_APPEAL = "⚠️"
    EMOJI_REPORT = "📊"
    EMOJI_ERROR = "🚨"
    EMOJI_BOT = "🤖"
    EMOJI_MONEY = "💵"

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        logger.info(f"TelegramNotifier inicializado - Chat ID: {chat_id}")

    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """
        Envia un mensaje de texto a Telegram.
        parse_mode: 'HTML' o 'Markdown'
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get('ok'):
                logger.debug(f"Mensaje enviado a Telegram exitosamente")
                return True
            else:
                logger.error(f"Error Telegram: {result.get('description')}")
                return False

        except requests.exceptions.Timeout:
            logger.error("Timeout al enviar mensaje a Telegram")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red enviando a Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado en Telegram: {e}")
            return False

    def send_new_order_alert(self, order_id: str, side: str, amount: float,
                             currency: str, counterparty: str, status: str) -> bool:
        """
        Envia alerta de nueva orden P2P detectada.
        """
        emoji = self.EMOJI_COMPRA if side == 'COMPRA' else self.EMOJI_VENTA
        short_id = order_id[:12] + '...' if len(str(order_id)) > 12 else order_id

        message = (
            f"{self.EMOJI_NEW_ORDER} <b>NUEVA ORDEN P2P DETECTADA</b>\n"
            f"{'━' * 30}\n"
            f"{emoji} <b>Tipo:</b> {side}\n"
            f"{self.EMOJI_MONEY} <b>Monto:</b> {amount} {currency}\n"
            f"👤 <b>Contraparte:</b> {counterparty}\n"
            f"🔑 <b>ID Orden:</b> <code>{short_id}</code>\n"
            f"📋 <b>Estado:</b> {status}\n"
            f"🕐 <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}\n"
            f"{'━' * 30}\n"
            f"{self.EMOJI_BOT} Bot Bybit P2P LATAM"
        )

        return self.send_message(message)

    def send_order_update(self, order_id: str, old_status: str, new_status: str) -> bool:
        """
        Notifica cambio de estado en una orden.
        """
        STATUS_EMOJIS = {
            '5': '⏳',
            '10': '💸',
            '20': '⚠️',
            '30': '❌',
            '40': '✅',
            '50': '🚫'
        }

        STATUS_NAMES = {
            '5': 'Pendiente de pago',
            '10': 'Pago recibido - liberar fondos',
            '20': 'Apelacion abierta',
            '30': 'Cancelada',
            '40': 'Completada',
            '50': 'Cancelada por sistema'
        }

        new_emoji = STATUS_EMOJIS.get(str(new_status), '❓')
        new_name = STATUS_NAMES.get(str(new_status), f'Estado {new_status}')
        short_id = str(order_id)[:12] + '...'

        # Alerta especial si hay que liberar fondos
        urgent = ""
        if str(new_status) == '10':
            urgent = "\n🚨 <b>ACCION REQUERIDA: Verificar pago y liberar fondos!</b>"
        elif str(new_status) == '20':
            urgent = "\n⚠️ <b>ATENCION: Orden en apelacion - revisar inmediatamente!</b>"

        message = (
            f"{new_emoji} <b>ACTUALIZACION DE ORDEN</b>\n"
            f"{'━' * 30}\n"
            f"🔑 <b>ID:</b> <code>{short_id}</code>\n"
            f"📊 <b>Nuevo estado:</b> {new_name}\n"
            f"🕐 <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}"
            f"{urgent}\n"
            f"{'━' * 30}\n"
            f"{self.EMOJI_BOT} Bot Bybit P2P LATAM"
        )

        return self.send_message(message)

    def send_daily_report(self, report: Dict) -> bool:
        """
        Envia el reporte diario de operaciones.
        """
        date = report.get('date', datetime.now().strftime('%d/%m/%Y'))
        time = report.get('time', '')
        completed = report.get('completed_orders', 0)
        cancelled = report.get('cancelled_orders', 0)
        active = report.get('active_orders', 0)
        stats = report.get('stats', {})

        total_volume = stats.get('total_volume_usdt', 0)
        buy_orders = stats.get('buy_orders', 0)
        sell_orders = stats.get('sell_orders', 0)
        currencies = stats.get('currencies', {})

        # Construir linea de monedas
        currencies_line = ""
        for curr, vol in currencies.items():
            currencies_line += f"\n   • {curr}: {vol:.2f}"

        message = (
            f"{self.EMOJI_REPORT} <b>REPORTE DIARIO P2P - BYBIT LATAM</b>\n"
            f"{'━' * 30}\n"
            f"📅 <b>Fecha:</b> {date} {time}\n"
            f"{'━' * 30}\n"
            f"✅ <b>Completadas:</b> {completed}\n"
            f"❌ <b>Canceladas:</b> {cancelled}\n"
            f"⏳ <b>Activas:</b> {active}\n"
            f"{'━' * 30}\n"
            f"💰 <b>Volumen Total:</b> {total_volume:.2f} USDT\n"
            f"🟢 <b>Compras:</b> {buy_orders}\n"
            f"🔴 <b>Ventas:</b> {sell_orders}\n"
        )

        if currencies_line:
            message += f"💱 <b>Por Moneda:</b>{currencies_line}\n"

        message += (
            f"{'━' * 30}\n"
            f"{self.EMOJI_BOT} Bot Bybit P2P LATAM"
        )

        return self.send_message(message)

    def send_error_alert(self, error_msg: str) -> bool:
        """
        Envia alerta de error critico.
        """
        message = (
            f"{self.EMOJI_ERROR} <b>ERROR EN BOT P2P</b>\n"
            f"{'━' * 30}\n"
            f"📝 <b>Error:</b>\n"
            f"<code>{error_msg[:500]}</code>\n"
            f"🕐 <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}\n"
            f"{'━' * 30}\n"
            f"{self.EMOJI_BOT} Bot Bybit P2P LATAM"
        )

        return self.send_message(message)

    def send_release_confirmation(self, order_id: str, amount: float, currency: str) -> bool:
        """
        Confirma que una orden fue liberada exitosamente.
        """
        short_id = str(order_id)[:12] + '...'
        message = (
            f"{self.EMOJI_COMPLETED} <b>ORDEN LIBERADA EXITOSAMENTE</b>\n"
            f"{'━' * 30}\n"
            f"🔑 <b>ID:</b> <code>{short_id}</code>\n"
            f"{self.EMOJI_MONEY} <b>Monto:</b> {amount} {currency}\n"
            f"🕐 <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}\n"
            f"{'━' * 30}\n"
            f"{self.EMOJI_BOT} Bot Bybit P2P LATAM"
        )

        return self.send_message(message)

    def test_connection(self) -> bool:
        """
        Prueba la conexion con Telegram enviando mensaje de test.
        """
        return self.send_message(
            f"{self.EMOJI_BOT} <b>Conexion con Telegram verificada!</b>\n"
            f"Bot Bybit P2P LATAM funcionando correctamente.\n"
            f"Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
