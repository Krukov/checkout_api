#!/usr/bin/env python
from distutils.core import setup
import re


def get_version():
    init_py = open('checkout_api/__init__.py').read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
    return metadata['version']

version = get_version()

setup(
    name='checkout_api',
    version=version,
    packages=['checkout_api'],
    url='https://github.com/Krukov/checkout_api',
    download_url='https://github.com/Krukov/checkout_api/tarball/' + version,
    license='MIT license',
    author='Dmitry Krukov',
    author_email='frog-king69@yandex.ru',
    description='Python API wrappper for Checkout',
    long_description=open('README.rst').read(),
    requires=[
        'requests (>=2.4)',
        'responses (>=0.3)',
        'six (>=1.7.3)',
    ],
    install_requires=[
        'requests >=2.4',
        'responses >=0.3',
        'six >=1.7.3',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)