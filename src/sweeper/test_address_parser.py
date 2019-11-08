#!/usr/bin/env python
# * coding: utf8 *
'''
test_address_parser.py
tests for the address parser module
'''
from .address_parser import Address, normalize_direction


def test_parses_address_number():
    tests = [
        ['123 main street', '123'],
        ['4 main street', '4']
    ]

    for input_text, expected in tests:
        assert Address(input_text).address_number == expected

def test_parses_prefix_direction():
    tests = [
        ['123 S main street', 'S'],
        ['456 North main', 'N']
    ]

    for input_text, expected in tests:
        assert Address(input_text).prefix_direction == expected

def test_parses_street_name():
    tests = [
        ['123 S main street', 'MAIN'],
        ['456 North main', 'MAIN']
    ]

    for input_text, expected in tests:
        assert Address(input_text).street_name == expected

def test_normalize_direction():
    north_tests = [
        'North',
        'N',
        'north',
        'n'
    ]

    for text in north_tests:
        assert normalize_direction(text) == 'N'
