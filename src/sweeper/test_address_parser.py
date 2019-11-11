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
    def test_parses_number_suffix(self):
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

    def test_no_prefix_direction_street(self):
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

    # def test_doubleSpaces(self):
    #     address = Address('  123  ea main  st')

    #     assert address.houseNumber == '123'
    #     assert address.prefixDirection == 'E'
    #     assert address.streetName == 'MAIN'
    #     assert address.suffix_type == 'ST'

    # def test_noPreDir(self):
    #     address = Address('1901 Sidewinder Dr')

    #     assert address.houseNumber == '1901'
    #     assert address.prefixDirection == None
    #     assert address.streetName == 'SIDEWINDER'
    #     assert address.suffix_type == 'DR'
    #     assert address.suffix_direction == None
    #     assert address.normalizedAddressString == '1901 SIDEWINDER DR'

    # def test_stripPeriods(self):
    #     address = Address('  123 ea main st.')

    #     assert address.houseNumber == '123'
    #     assert address.prefixDirection == 'E'
    #     assert address.streetName == 'MAIN'
    #     assert address.suffix_type == 'ST'
    #     assert address.suffix_direction == None
    #     assert address.normalizedAddressString == '123 E MAIN ST'

    # # tests from Steve's geocoder...
    # def test_steves(self):
    #     address = Address("5301 w jacob hill cir")
    #     assert '5301' == address.houseNumber
    #     assert "JACOB HILL" == address.streetName
    #     assert 'CIR' == address.suffix_type

    #     address = Address("400 S 532 E")
    #     assert '400' == address.houseNumber
    #     assert "532" == address.streetName
    #     assert 'E' == address.suffix_direction

    #     address = Address("5625 S 995 E")
    #     assert '5625' == address.houseNumber
    #     assert "995" == address.streetName
    #     assert 'E' == address.suffix_direction

    #     address = Address("372 North 600 East")
    #     assert '372' == address.houseNumber
    #     assert "600" == address.streetName
    #     assert 'E' == address.suffix_direction

    #     address = Address("30 WEST 300 NORTH")
    #     assert '30' == address.houseNumber
    #     assert "300" == address.streetName
    #     assert 'N' == address.suffix_direction

    #     address = Address("126 E 400 N")
    #     assert '126' == address.houseNumber
    #     assert "400" == address.streetName
    #     assert 'N' == address.suffix_direction

    #     address = Address("270 South 1300 East")
    #     assert '270' == address.houseNumber
    #     assert "1300" == address.streetName
    #     assert 'E' == address.suffix_direction

    #     address = Address("126 W SEGO LILY DR")
    #     assert '126' == address.houseNumber
    #     assert "SEGO LILY" == address.streetName
    #     assert 'DR' == address.suffix_type

    #     address = Address("261 E MUELLER PARK RD")
    #     assert '261' == address.houseNumber
    #     assert "MUELLER PARK" == address.streetName
    #     assert 'RD' == address.suffix_type

    #     address = Address("17 S VENICE MAIN ST")
    #     assert '17' == address.houseNumber
    #     assert "VENICE MAIN" == address.streetName
    #     assert 'ST' == address.suffix_type

    #     address = Address("20 W Center St")
    #     assert '20' == address.houseNumber
    #     assert 'W' == address.prefixDirection
    #     assert "CENTER" == address.streetName
    #     assert 'ST' == address.suffix_type

    #     address = Address("9314 ALVEY LN")
    #     assert '9314' == address.houseNumber
    #     assert "ALVEY" == address.streetName
    #     assert 'LN' == address.suffix_type

    #     address = Address("167 DALY AVE")
    #     assert '167' == address.houseNumber
    #     assert "DALY" == address.streetName
    #     assert 'AVE' == address.suffix_type

    #     address = Address("1147 MCDANIEL CIR")
    #     assert '1147' == address.houseNumber
    #     assert "MCDANIEL" == address.streetName
    #     assert 'CIR' == address.suffix_type

    #     address = Address("300 Walk St")
    #     assert '300' == address.houseNumber
    #     assert "WALK" == address.streetName
    #     assert 'ST' == address.suffix_type

    #     address = Address("5 Cedar Ave")
    #     assert '5' == address.houseNumber
    #     assert "CEDAR" == address.streetName
    #     assert 'AVE' == address.suffix_type

    #     address = Address("1238 E 1ST Avenue")
    #     assert '1238' == address.houseNumber
    #     assert "1ST" == address.streetName
    #     assert 'AVE' == address.suffix_type

    #     address = Address("1238 E FIRST Avenue")
    #     assert '1238' == address.houseNumber
    #     assert "FIRST" == address.streetName
    #     assert 'AVE' == address.suffix_type

    #     address = Address("1238 E 2ND Avenue")
    #     assert '1238' == address.houseNumber
    #     assert "2ND" == address.streetName
    #     assert 'AVE' == address.suffix_type

    #     address = Address("1238 E 3RD Avenue")
    #     assert '1238' == address.houseNumber
    #     assert "3RD" == address.streetName
    #     assert 'AVE' == address.suffix_type

    #     address = Address("1573 24TH Street")
    #     assert '1573' == address.houseNumber
    #     assert "24TH" == address.streetName
    #     assert 'ST' == address.suffix_type

    #     # if you dont' have a street name but you have a prefix direction then the
    #     # prefix diretion is probably the street name.
    #     address = Address("168 N ST")
    #     assert '168' == address.houseNumber
    #     assert "N" == address.streetName
    #     assert 'ST' == address.suffix_type

    #     address = Address("168 N N ST")
    #     assert '168' == address.houseNumber
    #     assert "N" == address.streetName
    #     assert 'ST' == address.suffix_type

    #     address = Address("478 S WEST FRONTAGE RD")
    #     assert '478' == address.houseNumber
    #     assert "WEST FRONTAGE" == address.streetName
    #     assert 'RD' == address.suffix_type

    #     address = Address("1048 W 1205 N")
    #     assert '1048' == address.houseNumber
    #     assert "1205" == address.streetName
    #     assert None == address.suffix_type
    #     assert 'N' == address.suffix_direction

    #     address = Address("2139 N 50 W")
    #     assert '2139' == address.houseNumber
    #     assert "50" == address.streetName
    #     assert None == address.suffix_type
    #     assert 'W' == address.suffix_direction

    # def test_streetTypeNames(self):
    #     address = Address('123 E PARKWAY AVE')

    #     assert address.houseNumber == '123'
    #     assert address.prefixDirection == 'E'
    #     assert address.streetName == 'PARKWAY'
    #     assert address.suffix_type == 'AVE'
    #     assert address.suffix_direction == None
    #     assert address.normalizedAddressString == '123 E PARKWAY AVE'

    #     address = Address('123 E PARKWAY TRAIL AVE')

    #     assert address.houseNumber == '123'
    #     assert address.prefixDirection == 'E'
    #     assert address.streetName == 'PARKWAY TRAIL'
    #     assert address.suffix_type == 'AVE'
    #     assert address.suffix_direction == None
    #     assert address.normalizedAddressString == '123 E PARKWAY TRAIL AVE'
