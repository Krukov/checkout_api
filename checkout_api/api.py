# -*- encoding: utf-8 -*-

import datetime
from copy import deepcopy

from requests import Request, Session

__all__ = ['CheckoutApi']

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
    """Chechout Api (http://www.checkout.ru/)"""
    
    _cache = _Cache()  # cross instance cache for ticket and so on
    __ticket__timeout = 60 * 60
    __host = 'http://platform.checkout.ru/'
    __urls = {
        'getTicket': 'service/login/ticket/',
        'getPlacesByQuery': 'service/checkout/getPlacesByQuery/',
        'calculation': 'service/checkout/calculation/',
        'getStreetsByQuery': 'service/checkout/getStreetsByQuery/',
        'getPostalCodeByAdress': 'service/checkout/getPostalCodeByAdress/',
        'getPlaceByPostalCode': 'service/checkout/getPlaceByPostalCode/',
        'createOrder': 'service/order/create/',
        'status': 'service/order/staus/',
        'statushistory': 'service/order/statushistory/',
        'platformstatushistory': 'service/order/platformstatushistory/',
    }

    CANCELED_STATUS = 'CANCELED_BEFORE_SHIPMENT'
    CREATED_STATUS = 'CREATED'

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
        method = method.upper()
        
        if ticket and method == 'GET':
            data['ticket'] = self.ticket
        elif method == 'POST':
            data['apiKey'] = self._key

        session = Session()
        request = Request(method, self.__build_full_url(name),
                          data=data, **_request_params)
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
        resp = self._response('getPlacesByQuery', data={'place': query})
        return rest.get('suggestions')

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
        resp = self._response('getPostalCodeByAdress', data=data)
        return resp.get('postindex')

    def get_place_by_postcode(self, code):
        """
        Получение населного пункта по почтовму индексу
        """
        return self._response('getPlaceByPostalCode', data={'postIndex': code})

    def __order(self, goods, delivery, user, comment,
                order_id, payment_method, delivery_cost=None, edit=False):
        if payment_method not in ['cash', 'prepay']:
            raise ValueError('payment_method can be "cash" or "prepay"')  # TODO: create special exception
        data = {
            'goods': goods,
            'delivery': delivery,
            'user': user,
            'comment': comment, 
            'shopOrderId': order_id,
            'paymentMethod': paymentMethod,
            'forcedCost': delivery_cost,
            }
            url = 'createOrder'
            if edit:
                url = self.__urls['createOrder'] + edit
        return self._response(url, method='post', data=data)

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
        return self.__order(*args, **kwargs, edit=False)

    def edit_order(self, *args, **kwargs):
        return self.__order(*args, **kwargs, edit=kwargs.pop('id'))

    def _change_status(self, order_id, status):
        url = self.__urls['status'] + order_id
        return self._response(url, method='post', data={'status': status})
or
    def cancel_order(self, order_id):
        """
        Перевод заказа в статус отмены
        """
        return self._change_status(order_id, self.CANCELED_STATUS)

    def change_status_to_created(self, order_id):
        """
        Если заказ в статусе отмены то его можно перевести в статус создан
        """
        return self._change_status(order_id, self.CREATED)

    def get_order_info(self, order_id):
        """
        История смены статуса заказа и информация о  заказе
        """
        url = self.__urls['statushistory'] + order_id
        return self._response(url, data={'API_KEY': self._key}, ticket=False)

    def get_status_history(self, order_id):
        """
        История смены статуса заказа
        """
        url = self.__urls['platformstatushistory'] + order_id
        return self._response(url, data={'API_KEY': self._key}, ticket=False)