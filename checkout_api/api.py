# -*- encoding: utf-8 -*-

import os
from copy import deepcopy

from requests import Request, Session

__all__ = ['ChechoutApi',]

_request_params = {'headers': 'Python api wrapper'}


class ChechoutApi(object):

    __cache = {}

    __ticket__timeout = 60 * 60
    __host = 'http:/platform.checkout.ru'
    __urls = {
        'ticket': '/service/login/ticket/'
    }

    """docstring for ChechoutApi"""
    def __init__(self, key):
        self.__key = key
    
    @property
    def ticket(self):
        if 'ticket' not in self.__cache:
            self.__cache['ticket'] = self.__get_ticket()

        if not self.__check_ticket_time():
            self.__cache['ticket'] = self.__get_ticket()

        return self.__cache['ticket']

    def __check_ticket_time(self):
        if self.__cache.get('last_time') > self.__ticket__timeout: # todo: check time 
            return False
        return True

    def __get_ticket(self):
        return self._response('ticket', ticket=False)

    @classmethod
    def __build_full_url(cls, name):
        _dir = cls.__urls.get(name, name)
        return os.path.join(cls.__host, _dir)


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
            return response.json()
        response.raise_for_status()