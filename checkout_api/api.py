# -*- encoding: utf-8 -*-

import os
import datetime
from copy import deepcopy

from requests import Request, Session

__all__ = ['CheckoutApi',]

_request_params = {'headers': {'User-Agent': 'Python api wrapper'}}


class _Cache:
    
    def __set__(self, instance, value):
        if instance is None:
            return

        instance.__cache[instance.__key] = value

    def __get__(self, instance, _=None):
        if instance is None:
            return
        return instance.__cache[instance.__key]



class CheckoutApi(object):

    __cache = {}

    __ticket__timeout = 60 * 60
    __host = 'http://platform.checkout.ru/'
    __urls = {
        'ticket': 'service/login/ticket/'
    }

    """docstring for ChechoutApi"""
    def __init__(self, key):
        self.__key = key
        self.__cache[key] = {}
    
    _cache = _Cache()    

    @property
    def ticket(self):
        if 'ticket' not in self.__cache:
            self._cache['ticket'] = self.__get_ticket()

        if not self.__check_ticket_time():
            self._cache['ticket'] = self.__get_ticket()

        return self._cache['ticket']

    def __check_ticket_time(self):
        delta = self._cache.get('ticket_time') - datetime.datetime.now()
        if delta > datetime.timedelta(seconds=self.__ticket__timeout): 
            return False
        return True

    def __get_ticket(self):
        return self._response('ticket', ticket=False).get('ticket')

    @classmethod
    def __build_full_url(cls, name):
        _dir = cls.__urls.get(name, name)
        return cls.__host + _dir


    def _response(self, name, method='get', data={}, ticket=True):
        data = deepcopy(data)
        method = method.upper()
        
        if ticket and method == 'GET':
            data['ticket'] = self.ticket

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

