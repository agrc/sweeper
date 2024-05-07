#!/usr/bin/env python
# * coding: utf8 *
"""
address_parser.py
A module that parses street addresses into their various parts.
"""

import json
import pprint
import re
from os.path import dirname, join, realpath

import usaddress

TAG_MAPPING = {
    "AddressNumber": "address_number",
    "AddressNumberPrefix": "address_number",
    "AddressNumberSuffix": "address_number_suffix",
    "StreetNamePreDirectional": "prefix_direction",
    "StreetName": "street_name",
    # 'StreetNamePreModifier': 'street_name', #: handled in class below
    # 'StreetNamePreType': 'street_name', #: handled in class below
    "StreetNamePostDirectional": "street_direction",
    "StreetNamePostModifier": "street_type",
    "StreetNamePostType": "street_type",
    # 'CornerOf': 'address1',
    # 'IntersectionSeparator': 'address1',
    # 'LandmarkName': 'address1',
    # 'USPSBoxGroupID': 'address1',
    # 'USPSBoxGroupType': 'address1',
    # 'USPSBoxID': 'address1',
    # 'USPSBoxType': 'address1',
    "BuildingName": "unit_id",
    "OccupancyType": "unit_type",
    "OccupancyIdentifier": "unit_id",
    "SubaddressIdentifier": "unit_id",
    "SubaddressType": "unit_type",
    "PlaceName": "city",
    "StateName": "state",
    "ZipCode": "zip_code",
    "USPSBoxID": "po_box",
}
TWO_CHAR_DIRECTIONS = ["NO", "SO", "EA", "WE"]
with open(join(dirname(realpath(__file__)), "street_types.json"), "r") as file:
    STREET_TYPES = json.loads(file.read())
HWY_REGEX = re.compile("(SR|STATE ROUTE|HIGHWAY)")
UNIT_VALUES_NOT_APPROPRIATE_FOR_HASH_SIGN = ["rear"]
CARDINALS = ["N", "S", "E", "W", "NO", "SO", "EA", "WE", "NORTH", "SOUTH", "EAST", "WEST"]
SHORTENED_CARDINALS = re.compile("rd|nd|th$", re.IGNORECASE)


class Address:
    """
    Class for parsing address strings
    """

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
    po_box = None
    state = None
    StreetNamePreType = None
    StreetNamePreModifier = None

    def __init__(self, address_text):
        address_text = address_text.replace(".", "")
        extra_unit_parts = None
        try:
            parts, parsed_as = usaddress.tag(address_text, TAG_MAPPING)
        except usaddress.RepeatedLabelError:
            parts, parsed_as = usaddress.tag(" ".join(address_text.split(" ")[:-2]), TAG_MAPPING)
            extra_unit_parts, _ = usaddress.tag(" ".join(address_text.split(" ")[-2:]), TAG_MAPPING)
        if parsed_as not in ["Street Address", "PO Box"]:
            raise Exception(f'"{address_text}" is not recognized as a valid street address, or P.O. Box')

        for part in parts:
            try:
                value = parts[part].upper()
                if part.endswith("direction"):
                    value = normalize_direction(value)

                setattr(self, part, value)
            except AttributeError:
                pass

        #: check for incorrectly included prefix directions in street name
        if self.street_name is not None:
            street_name_parts = self.street_name.split(" ")
            first_word = street_name_parts[0].upper()
            if len(street_name_parts) > 1 and is_cardinal(first_word) and self.prefix_direction is None:
                self.prefix_direction = normalize_direction(first_word)
                self.street_name = " ".join(street_name_parts[1:])

        #: check for cardinals incorrectly parsed as address_number_suffix
        if is_cardinal(self.address_number_suffix):
            self.street_name = f"{parts['prefix_direction'].upper()} {self.street_name}"
            self.prefix_direction = self.address_number_suffix
            self.address_number_suffix = None

        if self.po_box is not None:
            return

        if self.StreetNamePreType is not None:
            #: e.g. US HWY
            self.street_name = f"{normalize_street_name_pre_type(self.StreetNamePreType)} {self.street_name}"
            del self.StreetNamePreType

        if self.StreetNamePreModifier is not None:
            self.street_name = f"{self.StreetNamePreModifier} {self.street_name}"
            del self.StreetNamePreModifier

        #: look for two-character prefix directions which usaddress does not handle
        if self.street_name is not None:
            street_name_parts = self.street_name.split(" ")
            if len(street_name_parts) > 1:
                if street_name_parts[0].upper() in TWO_CHAR_DIRECTIONS and self.prefix_direction is None:
                    self.prefix_direction = normalize_direction(street_name_parts[0])
                    self.street_name = " ".join(street_name_parts[1:])
                elif street_name_parts[-1].upper() in TWO_CHAR_DIRECTIONS and self.street_direction is None:
                    self.street_direction = normalize_direction(street_name_parts[-1])
                    self.street_name = " ".join(street_name_parts[:-1])

        if self.street_type is not None:
            #: handle multiple street_types (assume only the last one is valid and move all others to the street name)
            if len(self.street_type.split(" ")) > 1:
                parsed_street_types = self.street_type.split(" ")
                new_street_name = " ".join(parsed_street_types[:-1])
                if self.street_name is None:
                    self.street_name = new_street_name
                else:
                    self.street_name += f" {new_street_name}"
                self.street_type = parsed_street_types[-1]

            try:
                self.street_type = normalize_street_type(self.street_type)
            except InvalidStreetTypeError:
                #: must be part of the street name
                if self.street_name is None:
                    self.street_name = self.street_type
                else:
                    self.street_name += f" {self.street_type}"
                self.street_type = None

        if self.street_direction is not None and self.street_name is not None:
            #: check for shortened cardinals
            self.street_name = SHORTENED_CARDINALS.sub("00", self.street_name)

        if self.unit_id is not None:
            #: add `#` if there is not unit type and the unit is numeric
            if (
                not self.unit_id.startswith("#")
                and self.unit_type is None
                and self.unit_id.lower() not in UNIT_VALUES_NOT_APPROPRIATE_FOR_HASH_SIGN
            ):
                self.unit_id = f"# {self.unit_id}"

            #: strip `#` if there is a unit type
            elif self.unit_id.startswith("#") and self.unit_type is not None:
                self.unit_id = self.unit_id[1:].strip()

            if extra_unit_parts:
                self.unit_id = f"{self.unit_id}-{extra_unit_parts['unit_id']}"

    def __repr__(self):
        properties = vars(self)
        properties.update({"normalized": self.normalized})

        return f"Parsed Address:\n{pprint.pformat(properties)}"

    @property
    def normalized(self):
        """
        getter for normalized address string
        """
        if self.po_box is not None:
            return f"PO BOX {self.po_box}"

        parts = [
            self.address_number,
            self.address_number_suffix,
            self.prefix_direction,
            self.street_name,
            self.street_type,
            self.street_direction,
            self.unit_type,
            self.unit_id,
        ]

        return " ".join([part for part in parts if part is not None])


def normalize_direction(direction_text):
    """
    returns the single letter corresponding to the input direction
    """

    return direction_text[0].upper()


def normalize_street_type(type_text):
    """
    returns the standard abbreviation for the input street type
    """

    type_text = type_text.upper()
    for abbreviation, values in STREET_TYPES.items():
        if type_text in values:
            return abbreviation

    raise InvalidStreetTypeError(type_text)


def normalize_street_name_pre_type(text):
    """normalizes highways by doing things like replaces SR with HWY and removes US

    No need to worried about casing or "."s because usaddress has already taken care of them by this point.
    """
    return HWY_REGEX.sub("HWY", text).replace("US ", "")


class InvalidStreetTypeError(Exception):
    """
    exception for when the street type does not have a corresponding value in street_types.json
    """

    def __init__(self, type_text):
        super().__init__()
        self.message = f"No matching abbreviation found for {type_text}"


def is_cardinal(text):
    """
    returns True if the input text is a cardinal direction
    """

    if text is None:
        return False

    return text.upper() in CARDINALS
