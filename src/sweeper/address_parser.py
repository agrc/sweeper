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
    'StreetNamePostDirectional': 'street_direction',
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
TWO_CHAR_DIRECTIONS = ['NO', 'SO', 'EA', 'WE']


class Address():
    '''
    Class for parsing address strings
    '''
    address_number = None
    address_number_suffix = None
    prefix_direction = None
    street_name = None
    street_direction = None
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

        #: look for two-character prefix directions which usaddress does not handle
        street_name_parts = self.street_name.split(' ')
        if len(street_name_parts) > 1 and street_name_parts[0].upper() in TWO_CHAR_DIRECTIONS and self.prefix_direction is None:
            self.prefix_direction = normalize_direction(street_name_parts[0])
            self.street_name = ' '.join(street_name_parts[1:])

    def __repr__(self):
        return f'Parsed Address:\n{pprint.pformat(vars(self))}'

    @property
    def normalized(self):
        '''
        getter for normalized address string
        '''
        parts = [
            self.address_number,
            self.address_number_suffix,
            self.prefix_direction,
            self.street_name,
            self.street_type,
            self.unit_type,
            self.unit_id
        ]

        return ' '.join([part for part in parts if part is not None])


def normalize_direction(direction_text):
    return direction_text[0].upper()
