#!/usr/bin/env python
# * coding: utf8 *
'''
test_address_parser.py
tests for the address parser module
'''
import pytest

from .address_parser import Address, normalize_direction, normalize_street_type, InvalidStreetTypeError


class TestAddressNumber():
    '''
    tests for parsing address numbers
    '''
    def test_parses_address_number(self):
    tests = [
        ['123 main street', '123'],
        ['4 main street', '4']
    ]

    for input_text, expected in tests:
        assert Address(input_text).address_number == expected


class TestAddressNumberSuffix():
    '''
    tests for parsing address number suffixes
    '''
    def test_parses_address_number_suffix(self):
    tests = [
            ['123 1/2 s main street', '1/2']
        ]

        for input_text, expected in tests:
            assert Address(input_text).address_number_suffix == expected


class TestPrefixDirection():
    '''
    tests for parsing prefix directions
    '''
    def test_parses_prefix_direction(self):
        tests = [
            ['123 1/2 S main street', 'S'],
        ['123 S main street', 'S'],
            ['456 North main', 'N'],
            ['123 EA Some Street', 'E']
    ]

    for input_text, expected in tests:
        assert Address(input_text).prefix_direction == expected


class TestStreetName():
    '''
    tests for parsing street names
    '''
    def test_parses_street_name(self):
    tests = [
        ['123 S main street', 'MAIN'],
        ['456 North main', 'MAIN']
    ]

    for input_text, expected in tests:
        assert Address(input_text).street_name == expected

    def test_multi_word_street_name(self):
        address = Address('123 S Main Hello Street')

        assert address.street_name == 'MAIN HELLO'

    def test_no_prefix_direction_street_name(self):
        address = Address('123 Main Street')

        assert address.street_name == 'MAIN'
        assert address.prefix_direction is None


class TestStreetDirection():
    '''
    tests for parsing suffix directions
    '''
    def test_street_direction(self):
        address = Address('123 E 400 N')

        assert address.street_direction == 'N'
        assert address.street_type is None


class TestNormalizeDirection():
    '''
    tests for normalizing cardinal directions
    '''
    def test_normalize_direction(self):
    north_tests = [
        'North',
        'N',
        'north',
        'n'
    ]

    for text in north_tests:
        assert normalize_direction(text) == 'N'

    def test_two_characters(self):
        assert normalize_direction('EA') == 'E'

def test_white_space():
    address = Address(' 123 S Main ')

    assert address.address_number == '123'
    assert address.street_name == 'MAIN'


class TestNormalizeStreetType():
    '''
    tests for normalizing street types
    '''
    def test_normalize_street_type(self):
        tests = [
            ['ALY', 'ALY'],
            ['AVEN', 'AVE'],
            ['corner', 'COR']
        ]

        for input_text, expected in tests:
            assert normalize_street_type(input_text) == expected

    def test_raises_exceptions(self):
        with pytest.raises(InvalidStreetTypeError):
            normalize_street_type('9999')


def test_normalized_address_string():
    address = Address('123 EA Fifer Place ')

    assert address.normalized == '123 E FIFER PL'

    address = Address(' 123 east 400 w  ')

    assert address.normalized == '123 E 400 W'

