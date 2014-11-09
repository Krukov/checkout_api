# -*- coding: utf-8 -*-

import datetime
import json
import sys
import logging
import inspect
from copy import deepcopy
from enum import Enum

from requests import Request, Session

__all__ = ['CheckoutApi']


logger = logging.getLogger('checkout_api')
_request_params = {'headers': {'User-Agent': 'Python api wrapper'}}


class _Cache(object):
    _cache = {}

    def __set__(self, instance, value):
        if instance is None:
            return
        self._cache.setdefault(instance._key, value)

    def __get__(self, instance, _=None):
        if instance is None:
            return self
        self._cache.setdefault(instance._key, {})
        return self._cache[instance._key]

    @classmethod
    def clear(cls):
        cls._cache = {}


class CheckoutApi(object):
    """Checkout Api (http://www.checkout.ru/)"""

    _cache = _Cache()  # cross instance cache for ticket and so on
    __ticket__timeout = 60 * 60
    __host = 'http://platform.checkout.ru/'
    __urls = {
        'getTicket': 'service/login/ticket/',
        'getPlacesByQuery': 'service/checkout/getPlacesByQuery/',
        'calculation': 'service/checkout/calculation/',
        'getStreetsByQuery': 'service/checkout/getStreetsByQuery/',
        'getPostalCodeByAddress': 'service/checkout/getPostalCodeByAdress/',
        'getPlaceByPostalCode': 'service/checkout/getPlaceByPostalCode/',
        'createOrder': 'service/order/create/',
        'status': 'service/order/status/',
        'statushistory': 'service/order/statushistory/',
        'platformstatushistory': 'service/order/platformstatushistory/',
    }

    class STATUSES(Enum):
        CANCELED = 'CANCELED_BEFORE_SHIPMENT'
        CREATED = 'CREATED'
        FORMED = 'FORMED'
        IN_SENDING = 'IN_SENDING '
        DELIVERED = 'DELIVERED'
        PARTIAL = 'PARTIALY_DELIVERED'
        CANCELED_DELIVERY = 'CANCELED_AT_DELIVERY'
        LOSS = 'LOSS_DAMAGE'
        CONFIRMED = 'CONFIRMED'

    _STATUSES_STR = {
        STATUSES.CANCELED: 'Отмена до отправки',
        STATUSES.CREATED: 'Создан',
        STATUSES.FORMED: 'Сформирован',
        STATUSES.IN_SENDING: 'В отправке',
        STATUSES.DELIVERED: 'Доставлен',
        STATUSES.PARTIAL: 'Доставлен частично',
        STATUSES.CANCELED_DELIVERY: 'Отмена при доставке',
        STATUSES.LOSS: 'Потеря, порча',
        STATUSES.CONFIRMED: 'Доставка клиенткого возврата',
    }

    CHECKING_OPTION = 'checking'
    PARTIAL_OPTION = 'partial'

    class TYPES(Enum):
        MAIL = 'mail'
        EXPRESS = 'express'
        PVZ = 'pvz'
        POSTAMAT = 'postamat'

    def __init__(self, key):
        self._key = key

    @property
    def ticket(self):
        """
        Session key
        Used is some api methods like signature,
        valid only in 60 min(update after using)
        """
        if 'ticket' not in self._cache.keys():
            self._cache['ticket'] = self.__get_ticket()

        if not self.__check_ticket_time():
            self._cache['ticket'] = self.__get_ticket()

        return self._cache['ticket']

    @staticmethod
    def __log_method(name, *args, **kwargs):
        logger.info("Call method {name} with {data}".format(
            name=name, data=list(args[1:]) + list(kwargs.values())
        ))
        result = yield
        logger.info('Method {name} return {data}'.format(
            name=name, data=result
        ))
        yield

    @staticmethod
    def _log_method():
        privios_stack = inspect.currentframe().f_back
        name = privios_stack.f_code.co_name
        kwargs = privios_stack.f_locals
        _ = CheckoutApi.__log_method(name, **kwargs)
        next(_)
        return _

    def __check_ticket_time(self):
        if 'ticket_time' in self._cache:
            delta = datetime.datetime.now() - self._cache.get('ticket_time')
            if delta > datetime.timedelta(seconds=self.__ticket__timeout):
                return False
        return True

    def __get_ticket(self):
        url = self.__urls.get('getTicket') + self._key
        return self._response(url, ticket=False).get('ticket')

    @classmethod
    def __build_full_url(cls, name):
        _dir = cls.__urls.get(name, name)
        return cls.__host + _dir

    def _response(self, name, method='GET', data={}, ticket=True):
        data = deepcopy(data)
        _params = deepcopy(_request_params)
        method = method.upper()
        _param = 'params'

        if ticket and method == 'GET':
            data['ticket'] = self.ticket
        if method == 'POST':
            data['apiKey'] = self._key
            data = json.dumps(data)
            _param = 'data'

        _params[_param] = data
        session = Session()
        request = Request(method, self.__build_full_url(name),
                          **_params)
        resp = session.send(session.prepare_request(request))
        return self._process_result(resp)

    def _process_result(self, response):
        if response.ok:
            self._cache['ticket_time'] = datetime.datetime.now()
            return response.json()
        response.raise_for_status()

    @classmethod
    def _clear_cache(cls):
        cls._cache.clear()

    def _set_host(self, value):
        self.__host = value

    # METHODS

    def get_places(self, query):
        """
        Получение списка населных пунктов
        """
        log = self._log_method()
        resp = self._response('getPlacesByQuery', data={'place': query})
        log.send(resp)
        return resp.get('suggestions')

    def calculation(self, place, price, weight, count, assessed=None):
        """
        Расчет стоимости и сроков доставки
        """
        data = {
            'placeId': place,
            'totalSum': price,
            'assessedSum': assessed or price,
            'totalWeight': weight,
            'itemsCount': count,
        }
        resp = self._response('calculation', data=data)
        return resp

    def get_streets(self, place, query):
        """
        Получение списка улиц
        """
        resp = self._response('getStreetsByQuery',
                              data={'placeId': place, 'street': query})
        return resp.get('suggestions')

    def get_postcode(self, street, house, housing=None, building=None):
        """
        Получение почтового индекса
        """
        data = {
            'streetId': street,
            'house': house,
        }
        if housing is not None:
            data['housing'] = housing
        if building is not None:
            data['building'] = building
        resp = self._response('getPostalCodeByAddress', data=data)
        return resp.get('postindex')

    def get_place_by_postcode(self, code):
        """
        Получение населного пункта по почтовму индексу
        """
        return self._response('getPlaceByPostalCode', data={'postIndex': code})

    def __order(self, goods, delivery, user, comment,
                order_id, payment_method, delivery_cost=None, edit=None):
        if payment_method not in ['cash', 'prepay']:
            # TODO: create special exception
            raise ValueError('payment_method can be "cash" or "prepay"')
        data = {
            'goods': list(goods),
            'delivery': delivery,
            'user': user,
            'comment': comment,
            'shopOrderId': order_id,
            'paymentMethod': payment_method,
        }
        if delivery_cost is not None:
            data['forcedCost'] = delivery_cost

        url = 'createOrder'
        if edit:
            url = self.__urls['createOrder'] + edit
        return self._response(url, method='post', data=data)

    @staticmethod
    def create_delivery(address, delivery, place, delivery_type, cost, min_day, max_day, options='none'):
        if options not in ['none', CheckoutApi.CHECKING_OPTION, CheckoutApi.PARTIAL_OPTION]:
            raise ValueError()
        if delivery_type not in CheckoutApi.TYPES:
            raise ValueError()
        data = {
            'deliveryId': delivery,
            'placeFiasId': place,
            'courierOptions': [options],
            'type': delivery_type,
            'cost': cost,
            'minTerm': min_day,
            'maxTerm': max_day,
        }
        if delivery_type in (CheckoutApi.TYPES.EXPRESS, CheckoutApi.TYPES.MAIL):
            key = 'addressExpress'
        else:
            key = 'addressPvz'
        data[key] = address
        return data

    def create_order(self, *args, **kwargs):
        """
        Создние заказа
        :param goods: array of order items. item is a dict with keys - name, code, variantCode,
             quantity, assessedCost, payCost, weight
        :param delivery: looking for create_delivery method
        :param user: dict with keys - fullname, email, phone
        :param comment: just comment
        :param order_id: order number in shop system
        :param payment_method: can be 'cash' or 'prepay'
        :param delivery_cost: price for delivery (see 'calculation' method)
        :return dict like
            "order": {"id": номер закза в платформе, тип - натуральное},
            "delivery": {
                "id": идентифкатор службы доставки, тип - натуральное "serviceName": "название службы доставки", тип - строка
                "cost": итогвое значение стоимости доставки по даному закзу.
            }
        """
        return self.__order(*args, **kwargs)

    def edit_order(self, *args, **kwargs):
        return self.__order(*args, edit=kwargs.pop('id'), **kwargs)

    def _change_status(self, order_id, status):
        url = self.__urls['status'] + order_id
        return self._response(url, method='post', data={'status': status})

    def cancel_order(self, order_id):
        """
        Перевод заказа в статус отмены
        """
        return self._change_status(order_id, self.STATUSES.CANCELED_STATUS)

    def change_status_to_created(self, order_id):
        """
        Если заказ в статусе отмены то его можно перевести в статус создан
        """
        return self._change_status(order_id, self.STATUSES.CREATED_STATUS)

    def get_order_info(self, order_id):
        """
        История смены статуса заказа и информация о  заказе
        """
        url = self.__urls['statushistory'] + order_id
        return self._response(url, data={'API_KEY': self._key}, ticket=False)

    def get_status_history(self, order_id):
        """
        История статуса заказа
        """
        url = self.__urls['platformstatushistory'] + order_id
        return self._response(url, data={'API_KEY': self._key}, ticket=False)


# INIT Logger default settings
if not logger.handlers:
    logger.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)d %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S'
    )
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
