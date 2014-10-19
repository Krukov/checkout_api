===========================
Checkout API python wrapper
===========================


.. image:: https://travis-ci.org/Krukov/checkout_api.svg?branch=master
    :target: https://travis-ci.org/Krukov/checkout_api
.. image:: https://img.shields.io/coveralls/Krukov/checkout_api.svg
    :target: https://coveralls.io/r/Krukov/checkout_api
.. image:: https://pypip.in/py_versions/checkout_api/badge.svg
    :target: https://pypi.python.org/pypi/checkout_api/
    :alt: Supported Python versions
.. image:: https://pypip.in/download/checkout_api/badge.svg
    :target: https://pypi.python.org/pypi//checkout_api/
    :alt: Downloads
.. image:: https://pypip.in/version/checkout_api/badge.svg
    :target: https://pypi.python.org/pypi/checkout_api/
    :alt: Latest Version

Python wrapper for Chechout API (http://www.checkout.ru/, https://platform.checkout.ru/files/Checkout.API.1.9.7.pdf) 


Installation
============

::

    pip install checkout_api


Usage
=====


Main::

    from checkout_api import CheckoutApi

    api = CheckoutApi('api-key')

    api.calculation(place, price, weight, count, assessed, data)  # Расчет стоимости и сроков доставки
            
    api.cancel_order(order_id)  # Перевод заказа в статус отмены
            
    api.change_status_to_created(order_id)  # Если заказ в статусе отмены то его можно перевести в статус создан
            
    api.create_order(goods, delivery, user, comment, order_id, payment_method, delivery_cost=None)  # Создние заказа
    api.edit_order(same as create)  # Редактирование заказа
    api.get_order_info(order_id)  # История смены статуса заказа и информация о  заказе
            
    api.get_place_by_postcode(code)  # Получение населного пункта по почтовму индексу
            
    api.get_places(query)  # Получение списка населных пунктов
            
    api.get_postcode(street, house, housing, building, data)  # Получение почтового индекса
            
    api.get_status_history(order_id)  # История статуса заказа
            
    api.get_streets(place, query)  # Получение списка улиц



