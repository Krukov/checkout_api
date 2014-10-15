# -*- encoding: utf-8 -*-

import json
import re

import pytest
import responses

from six.moves.urllib.parse import parse_qsl


from checkout_api import ChechoutApi

_ticket_test = 'ticket'
_test_api_key = 'api-key'


def callback(request):
    response = {}

    def _response(status=200):
        return status, {}, json.dumps(response)
    
    if request.method.upper() == 'GET':
        payload = json.loads(request.body)
    
        if 'ticket' in request.path:
            response = {'ticket': _ticket_test,
                        'reciverEmailNotRequired': True}
            return _response()    


    elif request.method.upper() == 'POST':
        payload = dict(parse_qsl(request.body))

for method in [responses.GET, responses.POST]:
    responses.add_callback(
        method, re.compile('https?://.*/.*'),
        callback=callback, content_type='application/json'
    )

api = ChechoutApi(_test_api_key)

@responses.activate
def test_ticket_getting():
    assert api.ticket == _ticket_test
    assert len(responses.calls) == 1

