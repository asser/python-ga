#!/usr/bin/python2
# coding: utf-8

from distutils.core import setup

setup(
    name='googleanalytics',
    version='0.3.8',
    author='Asser Schrøder Femø',
    author_email='asser@diku.dk',
    packages=['googleanalytics', 'googleanalytics.test', 'googleanalytics.request'],
    scripts=[],
    url='http://github.com/asser/python-ga',
    license='LICENSE.txt',
    description='Google Analytics client',
    long_description=open('README.md').read(),
)
