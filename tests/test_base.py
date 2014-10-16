# -*- encoding: utf-8 -*-

import json
import re

import pytest
import responses

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
        payload = json.loads(request.body or '{}')
    
        if 'ticket' in request.url:
            if request.url.split('/')[-1] == _test_api_key:
                response.update({'ticket': _ticket_test,
                                 'reciverEmailNotRequired': True})
            else:
                pass
            return _response()    


    elif request.method.upper() == 'POST':
        payload = dict(parse_qsl(request.body))

for method in [responses.GET, responses.POST]:
    responses.add_callback(
        method, re.compile('https?://.*/.*'),
        callback=callback, content_type='application/json'
    )


#  TESTS
# ======

api = CheckoutApi(_test_api_key)

@responses.activate
def test_ticket_getting():
    assert api.ticket == _ticket_test
    assert len(responses.calls) == 1


@responses.activate
def test_ticket_cache():
    assert api.ticket == _ticket_test
    
    api2 = CheckoutApi(_test_api_key)
    assert api2.ticket == _ticket_test
    assert len(responses.calls) == 1


@responses.activate
def test_error():
    api2 = CheckoutApi(_test_api_key+'wrongdata')
    
    assert api2.ticket != _ticket_test
    assert len(responses.calls) == 1
    