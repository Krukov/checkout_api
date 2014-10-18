# -*- coding: utf-8 -*-

import json
import re

import pytest
import responses
from requests.exceptions import HTTPError

from six.moves.urllib.parse import parse_qsl


from checkout_api import CheckoutApi

_ticket_test = 'ticket'
_test_api_key = 'api-key'


def callback(request):
    """
    request callback that used for mock responses to checkout host
    """
    response = {}

    def _response(status=200):
        return status, {}, json.dumps(response)
    
    if request.method.upper() == 'GET':
        payload = dict(parse_qsl(request.body or ''))

        if 'ticket' in request.url:
            if request.url.split('/')[-1] == _test_api_key:
                response.update({'ticket': _ticket_test,
                                 'reciverEmailNotRequired': True})
                return _response()
            else:
                return _response(400)
        if 'ticket' not in payload and 'API_KEY' not in payload:
            return _response(400)
        if not (payload.get('ticket') == _ticket_test
                or payload.get('API_KEY') == _test_api_key):
            return _response(400)
        payload.pop('ticket', None)
        payload.pop('API_KEY', None)
    elif request.method.upper() == 'POST':
        payload = json.loads(request.body)
        if not 'apiKey' in payload:
            return _response(400)
        payload.pop('apiKey', None)
    response['status'] = 'ok'
    response['data'] = payload
    response['suggestions'] = {'status': 'ok', 'data': payload}
    return _response()


def add_callbacks():
    for method in [responses.GET, responses.POST]:
        responses.add_callback(
            method, re.compile('https?://.*/.*'),
            callback=callback, content_type='application/json'
        )

api = CheckoutApi(_test_api_key)


def api_test(func):
    def test():
        api._clear_cache()
        add_callbacks()
        res = func()
        return res
    return test

#  TESTS
# ======


@responses.activate
@api_test
def test_ticket_getting():
    assert api.ticket == _ticket_test
    assert len(responses.calls) == 1


@responses.activate
@api_test
def test_ticket_cache():
    assert api.ticket == _ticket_test

    api2 = CheckoutApi(_test_api_key)
    assert api2.ticket == _ticket_test
    assert len(responses.calls) == 1


@responses.activate
@api_test
def test_error():
    api = CheckoutApi(_test_api_key+'wrongdata')
    with pytest.raises(HTTPError):
        api.ticket
    assert len(responses.calls) == 1


@responses.activate
@api_test
def test_timeout():
    import time
    api._CheckoutApi__ticket__timeout = 1
    assert api.ticket == _ticket_test
    assert len(responses.calls) == 1

    time.sleep(2)
    assert api.ticket == _ticket_test
    assert len(responses.calls) == 2
    api._CheckoutApi__ticket__timeout = 60 * 60


@responses.activate
@api_test
def test_get_places():
    resp = api.get_places('Test')
    assert resp['status'] == 'ok'
    assert resp['data'] == {'place': 'Test'}


@responses.activate
@api_test
def test_calculation():
    resp = api.calculation('place', 'price', 'weight', 'count')
    assert resp['status'] == 'ok'
    assert resp['data'] == {'placeId': 'place', 'totalSum': 'price', 
                            'assessedSum': 'price', 'totalWeight': 'weight',
                            'itemsCount': 'count'}


@responses.activate
@api_test
def test_create_order():
    resp = api.create_order(range(2), 'delivery', user='user',
                            comment='comment', order_id='order',
                            payment_method='cash')
    assert resp['status'] == 'ok'
    assert resp['data'] == {'goods': [0, 1], 'delivery': 'delivery',
                            'user': 'user', 'comment': 'comment', 'shopOrderId': 'order',
                            'paymentMethod': 'cash'}

@responses.activate
@api_test
def test_get_order_info():
    resp = api.get_order_info('order_id')
    assert resp['status'] == 'ok'
    assert resp['data'] == {}

