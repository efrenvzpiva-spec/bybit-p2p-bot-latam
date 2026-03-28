#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuracion del Bot Bybit P2P LATAM.
Carga variables desde archivo .env para mantener credenciales seguras.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class Config:
    """
    Configuracion central del bot.
    Todas las variables se cargan desde el archivo .env
    """

    # ==================== BYBIT API ====================
    BYBIT_API_KEY: str = os.getenv('BYBIT_API_KEY', '')
    BYBIT_API_SECRET: str = os.getenv('BYBIT_API_SECRET', '')

    # Usar testnet para pruebas (True) o mainnet para produccion (False)
    TESTNET: bool = os.getenv('BYBIT_TESTNET', 'False').lower() == 'true'

    # ==================== TELEGRAM ====================
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')

    # ==================== INTERVALOS ====================
    # Cada cuantos segundos verificar nuevas ordenes
    CHECK_INTERVAL: int = int(os.getenv('CHECK_INTERVAL', '30'))

    # Cada cuantos segundos verificar actualizaciones de ordenes activas
    UPDATE_INTERVAL: int = int(os.getenv('UPDATE_INTERVAL', '60'))

    # Hora del reporte diario (formato HH:MM)
    REPORT_TIME: str = os.getenv('REPORT_TIME', '23:00')

    # ==================== CONFIGURACION REGIONAL ====================
    # Moneda fiat principal de la region
    FIAT_CURRENCY: str = os.getenv('FIAT_CURRENCY', 'VES')  # VES=Venezuela, COP=Colombia, etc.

    # Zona horaria
    TIMEZONE: str = os.getenv('TIMEZONE', 'America/Caracas')

    # ==================== LIMITES Y ALERTAS ====================
    # Monto minimo para alertas (en USDT)
    MIN_ALERT_AMOUNT: float = float(os.getenv('MIN_ALERT_AMOUNT', '0'))

    # Maximo de ordenes simultaneas antes de alertar
    MAX_ACTIVE_ORDERS: int = int(os.getenv('MAX_ACTIVE_ORDERS', '10'))

    def validate(self) -> bool:
        """
        Valida que todas las variables criticas esten configuradas.
        Retorna True si la configuracion es valida.
        """
        errors = []

        if not self.BYBIT_API_KEY:
            errors.append("BYBIT_API_KEY no configurada")
        if not self.BYBIT_API_SECRET:
            errors.append("BYBIT_API_SECRET no configurada")
        if not self.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN no configurado")
        if not self.TELEGRAM_CHAT_ID:
            errors.append("TELEGRAM_CHAT_ID no configurado")

        if errors:
            for error in errors:
                print(f"[CONFIG ERROR] {error}")
            return False

        return True

    def __str__(self) -> str:
        return (
            f"Config Bybit P2P Bot LATAM:\n"
            f"  API Key: {'*' * 8}{self.BYBIT_API_KEY[-4:] if self.BYBIT_API_KEY else 'NO CONFIGURADA'}\n"
            f"  Testnet: {self.TESTNET}\n"
            f"  Telegram Chat: {self.TELEGRAM_CHAT_ID}\n"
            f"  Intervalo checks: {self.CHECK_INTERVAL}s\n"
            f"  Reporte diario: {self.REPORT_TIME}\n"
            f"  Moneda fiat: {self.FIAT_CURRENCY}\n"
            f"  Timezone: {self.TIMEZONE}"
        )
