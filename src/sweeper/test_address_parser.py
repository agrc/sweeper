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
        tests = [['123 main street', '123'], ['4 main street', '4']]

        for input_text, expected in tests:
            assert Address(input_text).address_number == expected


class TestAddressNumberSuffix():
    '''
    tests for parsing address number suffixes
    '''

    def test_parses_number_suffix(self):
        tests = [['123 1/2 s main street', '1/2'], ['123 A S Main St', 'A']]

        for input_text, expected in tests:
            assert Address(input_text).address_number_suffix == expected


class TestPrefixDirection():
    '''
    tests for parsing prefix directions
    '''

    def test_parses_prefix_direction(self):
        tests = [['123 1/2 S main street', 'S'], ['123 S main street', 'S'], ['456 North main', 'N'], ['123 EA Some Street', 'E'], ['9258 So 3090 W', 'S'],
                 ['9258 SO. 3090 w', 'S']]

        for input_text, expected in tests:
            assert Address(input_text).prefix_direction == expected

    def test_no_prefix_direction(self):
        address = Address('1901 Sidewinder Dr')

        assert address.address_number == '1901'
        assert address.prefix_direction is None
        assert address.street_name == 'SIDEWINDER'
        assert address.street_type == 'DR'
        assert address.street_direction is None
        assert address.normalized == '1901 SIDEWINDER DR'


class TestStreetName():
    '''
    tests for parsing street names
    '''

    def test_parses_street_name(self):
        tests = [
            ['123 S main street', 'MAIN'],
            ['456 North main', 'MAIN'],
            ['9258 w 3090 so.', '3090'],
            ['9258 w 3090 so', '3090'],
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
        north_tests = ['North', 'N', 'north', 'n']

        for text in north_tests:
            assert normalize_direction(text) == 'N'

    def test_two_characters(self):
        assert normalize_direction('EA') == 'E'
        assert normalize_direction('SO') == 'S'
        assert normalize_direction('WE') == 'W'
        assert normalize_direction('NO') == 'N'


class TestWhiteSpace():
    '''
    tests for dealing with white space
    '''

    def test_white_space(self):
        address = Address(' 123 S Main ')

        assert address.address_number == '123'
        assert address.street_name == 'MAIN'

    def test_double_spaces(self):
        address = Address('  123  ea main  st')

        assert address.address_number == '123'
        assert address.prefix_direction == 'E'
        assert address.street_name == 'MAIN'
        assert address.street_type == 'ST'


class TestNormalizeStreetType():
    '''
    tests for normalizing street types
    '''

    def test_normalize_street_type(self):
        tests = [['ALY', 'ALY'], ['AVEN', 'AVE'], ['corner', 'COR']]

        for input_text, expected in tests:
            assert normalize_street_type(input_text) == expected

    def test_raises_exceptions(self):
        with pytest.raises(InvalidStreetTypeError):
            normalize_street_type('9999')

    def test_street_names_with_types(self):
        '''
        street names with types as part of the name
        '''
        address = Address('123 E PARKWAY AVE')

        assert address.address_number == '123'
        assert address.prefix_direction == 'E'
        assert address.street_name == 'PARKWAY'
        assert address.street_type == 'AVE'
        assert address.street_direction is None
        assert address.normalized == '123 E PARKWAY AVE'

        address = Address('123 E PARKWAY TRAIL AVE')

        assert address.address_number == '123'
        assert address.prefix_direction == 'E'
        assert address.street_name == 'PARKWAY TRAIL'
        assert address.street_type == 'AVE'
        assert address.street_direction is None
        assert address.normalized == '123 E PARKWAY TRAIL AVE'


class TestUnitParts():
    '''
    tests for unit_type and unit_id
    '''

    def test_add_hash_if_no_type(self):
        address = Address('123 s main st 3')

        assert address.unit_type is None
        assert address.unit_id == '# 3'

        address = Address('123 s main st suite 3')

        assert address.unit_type == 'SUITE'
        assert address.unit_id == '3'

    def test_strip_hash_if_type(self):
        address = Address('123 s main st suite #3')

        assert address.unit_type == 'SUITE'
        assert address.unit_id == '3'


class TestPOBox():
    '''
    tests for parsing PO box numbers
    '''

    def test_parses_po_boxes(self):
        tests = [
            #: input, po_box, normalized
            ['po box 1', '1', 'PO BOX 1'],
            ['p.o. box 2', '2', 'PO BOX 2'],
            ['P.O. BOX G', 'G', 'PO BOX G']
        ]

        for address_input, expected_box_name, normalized in tests:
            address = Address(address_input)

            assert address.po_box == expected_box_name
            assert address.normalized == normalized


def test_normalized_address_string():
    address = Address('123 EA Fifer Place ')

    assert address.normalized == '123 E FIFER PL'

    address = Address(' 123 east 400 w  ')

    assert address.normalized == '123 E 400 W'


def test_strip_periods():
    address = Address('  123 ea. main st.')

    assert address.address_number == '123'
    assert address.prefix_direction == 'E'
    assert address.street_name == 'MAIN'
    assert address.street_type == 'ST'
    assert address.street_direction is None
    assert address.normalized == '123 E MAIN ST'


def test_steve():
    '''
    tests from steve's geocoder
    '''
    address = Address('5301 w jacob hill cir')
    assert address.address_number == '5301'
    assert address.street_name == 'JACOB HILL'
    assert address.street_type == 'CIR'

    address = Address('400 S 532 E')
    assert address.address_number == '400'
    assert address.street_name == '532'
    assert address.street_direction == 'E'

    address = Address('5625 S 995 E')
    assert address.address_number == '5625'
    assert address.street_name == '995'
    assert address.street_direction == 'E'

    address = Address('372 North 600 East')
    assert address.address_number == '372'
    assert address.street_name == '600'
    assert address.street_direction == 'E'

    address = Address('30 WEST 300 NORTH')
    assert address.address_number == '30'
    assert address.street_name == '300'
    assert address.street_direction == 'N'

    address = Address('126 E 400 N')
    assert address.address_number == '126'
    assert address.street_name == '400'
    assert address.street_direction == 'N'

    address = Address('270 South 1300 East')
    assert address.address_number == '270'
    assert address.street_name == '1300'
    assert address.street_direction == 'E'

    address = Address('126 W SEGO LILY DR')
    assert address.address_number == '126'
    assert address.street_name == 'SEGO LILY'
    assert address.street_type == 'DR'

    address = Address('261 E MUELLER PARK RD')
    assert address.address_number == '261'
    assert address.street_name == 'MUELLER PARK'
    assert address.street_type == 'RD'

    address = Address('17 S VENICE MAIN ST')
    assert address.address_number == '17'
    assert address.street_name == 'VENICE MAIN'
    assert address.street_type == 'ST'

    address = Address('20 W Center St')
    assert address.address_number == '20'
    assert address.prefix_direction == 'W'
    assert address.street_name == 'CENTER'
    assert address.street_type == 'ST'

    address = Address('9314 ALVEY LN')
    assert address.address_number == '9314'
    assert address.street_name == 'ALVEY'
    assert address.street_type == 'LN'

    address = Address('167 DALY AVE')
    assert address.address_number == '167'
    assert address.street_name == 'DALY'
    assert address.street_type == 'AVE'

    address = Address('1147 MCDANIEL CIR')
    assert address.address_number == '1147'
    assert address.street_name == 'MCDANIEL'
    assert address.street_type == 'CIR'

    address = Address('300 Walk St')
    assert address.address_number == '300'
    assert address.street_name == 'WALK'
    assert address.street_type == 'ST'

    address = Address('5 Cedar Ave')
    assert address.address_number == '5'
    assert address.street_name == 'CEDAR'
    assert address.street_type == 'AVE'

    address = Address('1238 E 1ST Avenue')
    assert address.address_number == '1238'
    assert address.street_name == '1ST'
    assert address.street_type == 'AVE'

    address = Address('1238 E FIRST Avenue')
    assert address.address_number == '1238'
    assert address.street_name == 'FIRST'
    assert address.street_type == 'AVE'

    address = Address('1238 E 2ND Avenue')
    assert address.address_number == '1238'
    assert address.street_name == '2ND'
    assert address.street_type == 'AVE'

    address = Address('1238 E 3RD Avenue')
    assert address.address_number == '1238'
    assert address.street_name == '3RD'
    assert address.street_type == 'AVE'

    address = Address('1573 24TH Street')
    assert address.address_number == '1573'
    assert address.street_name == '24TH'
    assert address.street_type == 'ST'

    # if you don't have a street name but you have a prefix direction then the
    # prefix direction is probably the street name.
    address = Address('168 N ST')
    assert address.address_number == '168'
    assert address.street_name == 'N'
    assert address.street_type == 'ST'

    address = Address('168 N N ST')
    assert address.address_number == '168'
    assert address.street_name == 'N'
    assert address.street_type == 'ST'

    address = Address('478 S WEST FRONTAGE RD')
    assert address.address_number == '478'
    assert address.street_name == 'WEST FRONTAGE'
    assert address.street_type == 'RD'

    address = Address('1048 W 1205 N')
    assert address.address_number == '1048'
    assert address.street_name == '1205'
    assert address.street_type is None
    assert address.street_direction == 'N'

    address = Address('2139 N 50 W')
    assert address.address_number == '2139'
    assert address.street_name == '50'
    assert address.street_type is None
    assert address.street_direction == 'W'
