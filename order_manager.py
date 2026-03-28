#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo de gestion de ordenes P2P de Bybit.
Maneja el ciclo de vida de ordenes, estadisticas y reportes diarios.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bybit_api import BybitP2PAPI

logger = logging.getLogger(__name__)


class OrderManager:
    """
    Gestiona las ordenes P2P: consulta, seguimiento y reportes.
    """

    # Estados de ordenes Bybit P2P
    STATUS_PENDING = '5'        # Esperando pago del comprador
    STATUS_PAID = '10'          # Pago enviado, esperando liberacion
    STATUS_APPEAL = '20'        # En apelacion
    STATUS_CANCELLED = '30'     # Cancelada
    STATUS_COMPLETED = '40'     # Completada exitosamente
    STATUS_SYS_CANCEL = '50'   # Cancelada por el sistema

    def __init__(self, api: BybitP2PAPI):
        self.api = api
        self._active_orders_cache = {}
        logger.info("OrderManager inicializado")

    def get_pending_orders(self) -> List[Dict]:
        """
        Obtiene todas las ordenes pendientes de pago.
        """
        result = self.api.get_orders(status=self.STATUS_PENDING)
        if not result:
            return []

        orders = result.get('result', [])
        logger.info(f"Ordenes pendientes encontradas: {len(orders)}")
        return orders

    def get_paid_orders(self) -> List[Dict]:
        """
        Obtiene ordenes donde el comprador ya marco el pago.
        Estas requieren verificacion y liberacion de fondos.
        """
        result = self.api.get_orders(status=self.STATUS_PAID)
        if not result:
            return []

        orders = result.get('result', [])
        logger.info(f"Ordenes pagadas (esperando liberacion): {len(orders)}")
        return orders

    def get_active_orders(self) -> List[Dict]:
        """
        Obtiene todas las ordenes activas (pendientes + pagadas + en apelacion).
        """
        active = []

        for status in [self.STATUS_PENDING, self.STATUS_PAID, self.STATUS_APPEAL]:
            result = self.api.get_orders(status=status)
            if result and result.get('result'):
                active.extend(result['result'])

        logger.info(f"Total ordenes activas: {len(active)}")
        return active

    def get_completed_orders_today(self) -> List[Dict]:
        """
        Obtiene las ordenes completadas hoy.
        """
        result = self.api.get_orders(status=self.STATUS_COMPLETED, size=50)
        if not result:
            return []

        orders = result.get('result', [])
        today = datetime.now().date()
        today_orders = []

        for order in orders:
            created_time = order.get('createDate', 0)
            if created_time:
                # Bybit usa timestamp en milisegundos
                order_date = datetime.fromtimestamp(int(created_time) / 1000).date()
                if order_date == today:
                    today_orders.append(order)

        return today_orders

    def check_order_status(self, order_id: str) -> Optional[str]:
        """
        Consulta el estado actual de una orden especifica.
        Retorna el codigo de estado o None si hay error.
        """
        order_info = self.api.get_order_info(order_id)
        if not order_info:
            return None

        return str(order_info.get('status', ''))

    def get_order_details(self, order_id: str) -> Optional[Dict]:
        """
        Obtiene todos los detalles de una orden.
        """
        return self.api.get_order_info(order_id)

    def calculate_order_stats(self, orders: List[Dict]) -> Dict:
        """
        Calcula estadisticas de un conjunto de ordenes.
        Retorna totales por moneda, volumen y conteos.
        """
        stats = {
            'total_orders': len(orders),
            'total_volume_usdt': 0.0,
            'buy_orders': 0,
            'sell_orders': 0,
            'currencies': {},
            'payment_methods': {}
        }

        for order in orders:
            side = str(order.get('side', ''))
            amount = float(order.get('amount', 0))
            currency = order.get('currencyId', 'USDT')
            payment = order.get('paymentType', 'Desconocido')

            # Contar por tipo (compra/venta)
            if side == '1':
                stats['buy_orders'] += 1
            else:
                stats['sell_orders'] += 1

            # Sumar volumen
            stats['total_volume_usdt'] += amount

            # Agrupar por moneda
            if currency not in stats['currencies']:
                stats['currencies'][currency] = 0.0
            stats['currencies'][currency] += amount

            # Agrupar por metodo de pago
            if payment not in stats['payment_methods']:
                stats['payment_methods'][payment] = 0
            stats['payment_methods'][payment] += 1

        return stats

    def generate_daily_report(self) -> Dict:
        """
        Genera el reporte diario de operaciones P2P.
        Incluye: ordenes completadas, volumen total, estadisticas.
        """
        logger.info("Generando reporte diario de operaciones...")

        today_orders = self.get_completed_orders_today()
        stats = self.calculate_order_stats(today_orders)

        # Obtener ordenes canceladas del dia
        cancelled_result = self.api.get_orders(status=self.STATUS_CANCELLED, size=50)
        cancelled_today = []
        if cancelled_result and cancelled_result.get('result'):
            today = datetime.now().date()
            for order in cancelled_result['result']:
                created_time = order.get('createDate', 0)
                if created_time:
                    order_date = datetime.fromtimestamp(int(created_time) / 1000).date()
                    if order_date == today:
                        cancelled_today.append(order)

        # Obtener ordenes activas actuales
        active_orders = self.get_active_orders()

        report = {
            'date': datetime.now().strftime('%d/%m/%Y'),
            'time': datetime.now().strftime('%H:%M'),
            'completed_orders': len(today_orders),
            'cancelled_orders': len(cancelled_today),
            'active_orders': len(active_orders),
            'stats': stats,
            'orders_detail': today_orders[:10]  # Top 10 para el reporte
        }

        logger.info(f"Reporte generado: {len(today_orders)} completadas, {len(cancelled_today)} canceladas")
        return report

    def format_order_summary(self, order: Dict) -> str:
        """
        Formatea una orden para mostrar en notificacion.
        """
        order_id = order.get('orderId', 'N/A')
        amount = order.get('amount', 0)
        currency = order.get('currencyId', 'USDT')
        side = order.get('side', '')
        side_text = 'COMPRA' if str(side) == '1' else 'VENTA'
        counterparty = order.get('nickName', 'Desconocido')
        status_code = str(order.get('orderStatus', ''))
        status_text = self.api.get_order_status_text(status_code)
        price = order.get('price', 0)
        fiat_amount = order.get('orderAmount', 0)
        fiat_currency = order.get('tokenId', 'USD')

        return (
            f"ID: {order_id[:12]}...\n"
            f"Tipo: {side_text}\n"
            f"Monto: {amount} {currency}\n"
            f"Precio: {price} {fiat_currency}\n"
            f"Total Fiat: {fiat_amount} {fiat_currency}\n"
            f"Contraparte: {counterparty}\n"
            f"Estado: {status_text}"
        )
