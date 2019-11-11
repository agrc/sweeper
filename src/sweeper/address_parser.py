#!/usr/bin/env python
# * coding: utf8 *
'''
address_parser.py
A module that parses street addresses into their various parts.
'''
import pprint
import usaddress

TAG_MAPPING = {
    'AddressNumber': 'address_number',
    # 'AddressNumberPrefix': 'address1',
    'AddressNumberSuffix': 'address_number_suffix',
    'StreetNamePreDirectional': 'prefix_direction',
    'StreetName': 'street_name',
    # 'StreetNamePreModifier': 'address1',
    # 'StreetNamePreType': 'address1',
    'StreetNamePostDirectional': 'suffix_direction',
    # 'StreetNamePostModifier': 'address1',
    'StreetNamePostType': 'street_type',
    # 'CornerOf': 'address1',
    # 'IntersectionSeparator': 'address1',
    # 'LandmarkName': 'address1',
    # 'USPSBoxGroupID': 'address1',
    # 'USPSBoxGroupType': 'address1',
    # 'USPSBoxID': 'address1',
    # 'USPSBoxType': 'address1',
    # 'BuildingName': 'address2',
    'OccupancyType': 'unit_type',
    'OccupancyIdentifier': 'unit_id',
    # 'SubaddressIdentifier': 'address2',
    # 'SubaddressType': 'address2',
    'PlaceName': 'city',
    # 'StateName': 'state',
    'ZipCode': 'zip_code',
}


class Address():
    '''
    Class for parsing address strings
    '''
    address_number = None
    address_number_suffix = None
    prefix_direction = None
    street_name = None
    street_suffix = None
    street_type = None
    unit_type = None
    unit_id = None
    city = None
    zip_code = None
    def __init__(self, address_text):
        parts, parsed_as = usaddress.tag(address_text, TAG_MAPPING)
        if parsed_as != 'Street Address':
            raise Exception(f'{address_text} is not recognized as a valid street address')

        for part in parts:
            try:
                value = parts[part].upper()
                if part.endswith('direction'):
                    value = normalize_direction(value)

                setattr(self, part, value)
            except AttributeError:
                pass


    def __repr__(self):
        return f'Parsed Address:\n{pprint.pformat(vars(self))}'


def normalize_direction(direction_text):
    return direction_text[0].upper()
