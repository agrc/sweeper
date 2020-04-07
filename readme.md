# agrc-sweeper [![PyPI version](https://badge.fury.io/py/agrc-sweeper.svg)](https://badge.fury.io/py/agrc-sweeper)

fix data

## Available Sweepers

### addresses

Checks that addresses have minimum required parts and optionally normalizes them.

### duplicates

Checks for duplicate features.

### empties

Checks for empty geometries.

### metadata

Checks to make sure that the metadata meets [the SGID Metadata Minimum Requirements Document](https://docs.google.com/document/d/1VkXRwfSn6MraI1VeLfei5tg6je4bd2pp_Vh1JuST9xs/edit).

## Parsing Addresses

This project contains a module that can be used as a standalone address parser, `sweeper.address_parser`. This allows developer to take advantage of sweepers advanced address parsing and normalization without having to run the entire sweeper process.

### Usage Example

```python
from sweeper.address_parser import Address

address = Address('123 South Main Street')
print(address)

'''
--> Parsed Address:
{'address_number': '123',
 'normalized': '123 S MAIN ST',
 'prefix_direction': 'S',
 'street_name': 'MAIN',
 'street_type': 'ST'}
'''
```

### Available Address class properties

All properties default to None if there is no parsed value.

`address_number`

`address_number_suffix`

`prefix_direction`

`street_name`

`street_direction`

`street_type`

`unit_type`

`unit_id`
If no `unit_type` is found, this property is prefixed with `#` (e.g. `# 3`). If `unit_type` is found, `#` is stripped from this property.

`city`

`zip_code`

`po_box`
The PO Box if a po-box-type address was entered (e.g. `po_box` would be `1` for `p.o. box 1`).

`normalized`
A normalized string representing the entire address that was passed into the constructor. PO Boxes are normalized in this format `PO BOX <number>`.

## Installation (requires Pro 2.5+)

1. create conda environment
    - `conda create --clone arcgispro-py3 --name sweeper`
1. activate environment
    - `activate sweeper`
1. install sweeper
    - `pip install agrc-sweeper`
1. run cli for docs
    - `sweeper`

## Development

1. create conda environment
   - `conda create --clone arcgispro-py3 --name sweeper`
1. activate environment
   - `activate sweeper`
1. `test_metadata.py` uses a SQL database that needs to be restored via `src/sweeper/tests/data/Sweeper.bak` to your local SQL Server.

### Installing dependencies

1. install only required dependencies to run sweeper
    - `pip install -e .`
1. install required dependencies to work on sweeper
    - `pip install -e ".[develop]"`
1. install required dependencies to run sweeper tests
    - `pip install -e ".[tests]"`
1. run tests: `pytest`

### Uploading to pypi.org

1. Bump `version` in `setup.py`
1. `python setup.py sdist bdist_wheel`
1. `twine upload dist/*` (`pip install twine`, if needed)
