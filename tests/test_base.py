# -*- encoding: utf-8 -*-

import json

import pytest
import responses


def callback(request):
	if request.method == 'GET':
		payload = json.loads(request.body)
	return 200, {}, 'data'