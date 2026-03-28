#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo de conexion con la API de Bybit P2P.
Maneja autenticacion, firma de requests y llamadas al endpoint P2P.
"""

import hmac
import hashlib
import time
import json
import logging
import requests
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class BybitP2PAPI:
    """
    Cliente para la API de Bybit P2P.
    Soporta mainnet y testnet.
    """

    MAINNET_URL = "https://api.bybit.com"
    TESTNET_URL = "https://api-testnet.bybit.com"

    # Endpoints P2P
    P2P_ORDER_LIST = "/v5/p2p/order/list"
    P2P_ORDER_INFO = "/v5/p2p/order/info"
    P2P_ORDER_RELEASE = "/v5/p2p/order/release"
    P2P_ORDER_CANCEL = "/v5/p2p/order/cancel"
    P2P_ORDER_CHAT = "/v5/p2p/order/message/listpage"
    P2P_SEND_MESSAGE = "/v5/p2p/order/message/send"
    P2P_AD_LIST = "/v5/p2p/item/list"
    P2P_AD_ONLINE = "/v5/p2p/item/online"
    P2P_AD_OFFLINE = "/v5/p2p/item/offline"
    P2P_USER_INFO = "/v5/p2p/user/info"

    # Codigos de estado de ordenes P2P
    ORDER_STATUS = {
        '5': 'Pendiente de pago',
        '10': 'Pago enviado - esperando liberacion',
        '20': 'Apelacion en proceso',
        '30': 'Cancelada',
        '40': 'Completada',
        '50': 'Cancelada por sistema'
    }

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = self.TESTNET_URL if testnet else self.MAINNET_URL
        self.session = requests.Session()
        self.recv_window = 5000
        logger.info(f"API inicializada - {'TESTNET' if testnet else 'MAINNET'}")

    def _generate_signature(self, timestamp: str, params: str) -> str:
        """
        Genera la firma HMAC-SHA256 para autenticar requests.
        """
        param_str = f"{timestamp}{self.api_key}{self.recv_window}{params}"
        return hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _get_headers(self, timestamp: str, signature: str) -> dict:
        """
        Retorna los headers necesarios para requests autenticados.
        """
        return {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': str(self.recv_window),
            'Content-Type': 'application/json'
        }

    def _post(self, endpoint: str, payload: dict) -> dict:
        """
        Realiza un request POST autenticado a la API de Bybit.
        """
        timestamp = str(int(time.time() * 1000))
        json_payload = json.dumps(payload)
        signature = self._generate_signature(timestamp, json_payload)
        headers = self._get_headers(timestamp, signature)
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.post(url, headers=headers, data=json_payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('retCode') != 0:
                logger.error(f"Error API Bybit: {data.get('retMsg')} - Endpoint: {endpoint}")
                return None

            return data.get('result', {})

        except requests.exceptions.Timeout:
            logger.error(f"Timeout en request a {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red en {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en {endpoint}: {e}")
            return None

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """
        Realiza un request GET autenticado a la API de Bybit.
        """
        if params is None:
            params = {}

        timestamp = str(int(time.time() * 1000))
        query_string = urlencode(params)
        signature = self._generate_signature(timestamp, query_string)
        headers = self._get_headers(timestamp, signature)
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('retCode') != 0:
                logger.error(f"Error API Bybit: {data.get('retMsg')} - Endpoint: {endpoint}")
                return None

            return data.get('result', {})

        except requests.exceptions.Timeout:
            logger.error(f"Timeout en request a {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red en {endpoint}: {e}")
            return None

    # ==================== ORDENES ====================

    def get_orders(self, status: str = None, page: int = 1, size: int = 20) -> dict:
        """
        Obtiene lista de ordenes P2P.
        Status: '5'=Pendiente, '10'=Pagada, '20'=Apelacion, '30'=Cancelada, '40'=Completada
        """
        payload = {
            'page': page,
            'size': size
        }
        if status:
            payload['status'] = status

        return self._post(self.P2P_ORDER_LIST, payload)

    def get_order_info(self, order_id: str) -> dict:
        """
        Obtiene informacion detallada de una orden especifica.
        """
        payload = {'orderId': order_id}
        return self._post(self.P2P_ORDER_INFO, payload)

    def release_order(self, order_id: str) -> dict:
        """
        Libera los fondos de una orden (confirmar pago recibido).
        """
        payload = {'orderId': order_id}
        result = self._post(self.P2P_ORDER_RELEASE, payload)
        if result is not None:
            logger.info(f"Orden {order_id} liberada exitosamente")
        return result

    def cancel_order(self, order_id: str) -> dict:
        """
        Cancela una orden P2P.
        """
        payload = {'orderId': order_id}
        result = self._post(self.P2P_ORDER_CANCEL, payload)
        if result is not None:
            logger.info(f"Orden {order_id} cancelada")
        return result

    # ==================== CHAT ====================

    def get_chat_messages(self, order_id: str) -> dict:
        """
        Obtiene los mensajes de chat de una orden.
        """
        payload = {'orderId': order_id, 'size': 50}
        return self._post(self.P2P_ORDER_CHAT, payload)

    def send_message(self, order_id: str, message: str, msg_type: int = 1) -> dict:
        """
        Envia un mensaje en el chat de una orden.
        msg_type: 1=texto, 2=imagen
        """
        payload = {
            'orderId': order_id,
            'message': message,
            'msgType': msg_type
        }
        return self._post(self.P2P_SEND_MESSAGE, payload)

    # ==================== ANUNCIOS ====================

    def get_my_ads(self, status: int = 1) -> dict:
        """
        Obtiene los anuncios del merchant.
        status: 1=online, 2=offline
        """
        payload = {'status': status}
        return self._post(self.P2P_AD_LIST, payload)

    def set_ad_online(self, item_id: str) -> dict:
        """
        Activa un anuncio P2P.
        """
        payload = {'itemId': item_id}
        result = self._post(self.P2P_AD_ONLINE, payload)
        if result is not None:
            logger.info(f"Anuncio {item_id} activado")
        return result

    def set_ad_offline(self, item_id: str) -> dict:
        """
        Desactiva un anuncio P2P.
        """
        payload = {'itemId': item_id}
        result = self._post(self.P2P_AD_OFFLINE, payload)
        if result is not None:
            logger.info(f"Anuncio {item_id} desactivado")
        return result

    # ==================== USUARIO ====================

    def get_user_info(self) -> dict:
        """
        Obtiene informacion del merchant/usuario P2P.
        """
        return self._post(self.P2P_USER_INFO, {})

    def get_order_status_text(self, status_code: str) -> str:
        """
        Retorna el texto legible del codigo de estado de una orden.
        """
        return self.ORDER_STATUS.get(str(status_code), f'Estado desconocido ({status_code})')
