#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bybit P2P Bot LATAM
===================
Bot automatizado para gestion de operaciones P2P en Bybit LATAM.
Monitorea ordenes, notifica via Telegram y gestiona merchants.

Autor: efrenvzpiva-spec
Version: 1.0.0
"""

import time
import logging
import schedule
from datetime import datetime
from config import Config
from bybit_api import BybitP2PAPI
from order_manager import OrderManager
from notifier import TelegramNotifier

# Configuracion del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BybitP2PBot:
    """
    Bot principal para gestion P2P de Bybit LATAM.
    """

    def __init__(self):
        self.config = Config()
        self.api = BybitP2PAPI(
            api_key=self.config.BYBIT_API_KEY,
            api_secret=self.config.BYBIT_API_SECRET,
            testnet=self.config.TESTNET
        )
        self.order_manager = OrderManager(self.api)
        self.notifier = TelegramNotifier(
            token=self.config.TELEGRAM_BOT_TOKEN,
            chat_id=self.config.TELEGRAM_CHAT_ID
        )
        self.processed_orders = set()
        logger.info("Bot Bybit P2P LATAM iniciado correctamente")

    def check_new_orders(self):
        """
        Revisa si hay nuevas ordenes P2P pendientes.
        """
        try:
            logger.info("Verificando nuevas ordenes P2P...")
            orders = self.order_manager.get_pending_orders()

            for order in orders:
                order_id = order.get('orderId')
                if order_id not in self.processed_orders:
                    self.processed_orders.add(order_id)
                    self._handle_new_order(order)

        except Exception as e:
            logger.error(f"Error al verificar ordenes: {e}")
            self.notifier.send_error_alert(str(e))

    def _handle_new_order(self, order):
        """
        Procesa una nueva orden y envia notificacion.
        """
        order_id = order.get('orderId')
        amount = order.get('amount')
        currency = order.get('currencyId', 'USDT')
        side = order.get('side', '')  # 1=compra, 0=venta
        counterparty = order.get('nickName', 'Desconocido')
        status = order.get('orderStatus', '')

        side_text = 'COMPRA' if str(side) == '1' else 'VENTA'

        logger.info(f"Nueva orden detectada: {order_id} - {side_text} {amount} {currency}")

        # Notificar via Telegram
        self.notifier.send_new_order_alert(
            order_id=order_id,
            side=side_text,
            amount=amount,
            currency=currency,
            counterparty=counterparty,
            status=status
        )

    def check_order_updates(self):
        """
        Revisa actualizaciones de estado en ordenes activas.
        """
        try:
            active_orders = self.order_manager.get_active_orders()
            for order in active_orders:
                order_id = order.get('orderId')
                status = order.get('orderStatus')
                updated_status = self.order_manager.check_order_status(order_id)

                if updated_status and updated_status != status:
                    logger.info(f"Orden {order_id} cambio de estado: {status} -> {updated_status}")
                    self.notifier.send_order_update(
                        order_id=order_id,
                        old_status=status,
                        new_status=updated_status
                    )
        except Exception as e:
            logger.error(f"Error al verificar actualizaciones: {e}")

    def generate_daily_report(self):
        """
        Genera y envia el reporte diario de operaciones.
        """
        try:
            logger.info("Generando reporte diario...")
            report = self.order_manager.generate_daily_report()
            self.notifier.send_daily_report(report)
            logger.info("Reporte diario enviado correctamente")
        except Exception as e:
            logger.error(f"Error al generar reporte diario: {e}")

    def run(self):
        """
        Inicia el bot y programa las tareas periodicas.
        """
        logger.info("=" * 50)
        logger.info(" BYBIT P2P BOT LATAM v1.0.0 ")
        logger.info("=" * 50)

        # Enviar mensaje de inicio
        self.notifier.send_message(
            "Bot Bybit P2P LATAM iniciado\n"
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            "Monitoreando ordenes P2P..."
        )

        # Programar tareas
        schedule.every(self.config.CHECK_INTERVAL).seconds.do(self.check_new_orders)
        schedule.every(self.config.UPDATE_INTERVAL).seconds.do(self.check_order_updates)
        schedule.every().day.at(self.config.REPORT_TIME).do(self.generate_daily_report)

        logger.info(f"Verificando ordenes cada {self.config.CHECK_INTERVAL} segundos")
        logger.info(f"Reporte diario a las {self.config.REPORT_TIME}")

        # Verificacion inicial
        self.check_new_orders()

        # Loop principal
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Bot detenido por el usuario")
                self.notifier.send_message("Bot Bybit P2P LATAM detenido.")
                break
            except Exception as e:
                logger.error(f"Error en loop principal: {e}")
                time.sleep(30)


if __name__ == '__main__':
    bot = BybitP2PBot()
    bot.run()
