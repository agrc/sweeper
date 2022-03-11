# agrc-sweeper [![PyPI version](https://badge.fury.io/py/agrc-sweeper.svg)](https://badge.fury.io/py/agrc-sweeper)[![Publish on tag](https://github.com/agrc/sweeper/actions/workflows/python.yml/badge.svg)](https://github.com/agrc/sweeper/actions/workflows/python.yml)

The data cleaning service.

![sweeper_sm](https://user-images.githubusercontent.com/325813/90411835-91c4c080-e069-11ea-9d03-f3e60421b835.png)

## Available Sweepers

### Addresses

Checks that addresses have minimum required parts and optionally normalizes them.

### Duplicates

Checks for duplicate features.

### Empties

Checks for empty geometries.

### Metadata

Checks to make sure that the metadata meets [the Basic SGID Metadata Requirements](https://gis.utah.gov/about/policy/metadata/#basic-sgid-metadata).

#### Tags

Checks to make sure that existing tags are cased appropriately. This mean that the are title-cased other than known abbreviations (e.g. AGRC, BLM) and articles (e.g. a, the, of).

This check also verifies that the data set contains a tag that matches the database name (e.g. `SGID`) and the schema (e.g. `Cadastre`).

`--try-fix` adds missing required tags and title-cases any existing tags.

#### Summary

Checks to make sure that the summary is less than 2048 characters (a limitation of AGOL) and that it is shorter than the description.

#### Description

Checks to make sure that the description contains a link to a data page on gis.utah.gov.

#### Use Limitations

Checks to make sure that the text in this section matches the [official text for AGRC](src/sweeper/sweepers/UseLimitations.html).

`--try-fix` updates the text to match the official text.

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

## Installation (requires Pro 2.7+)

1. create conda environment
    - `conda create --name sweeper python=3.7`
1. activate environment
    - `activate sweeper`
1. install arcpy
    - `conda install arcpy -c esri`
1. install sweeper
    - `pip install agrc-sweeper`

## Development

1. create conda environment
    - `conda create --name sweeper python=3.7`
1. activate environment
    - `activate sweeper`
1. `test_metadata.py` uses a SQL database that needs to be restored via `src/sweeper/tests/data/Sweeper.bak` to your local SQL Server.

### Installing dependencies

1. install arcpy
    - `conda install -c esri arcpy`
1. install only required dependencies to run sweeper
    - `pip install -e .`
1. install required dependencies to work on sweeper
    - `pip install -e ".[develop]"`
1. install required dependencies to run sweeper tests
    - `pip install -e ".[tests]"`
1. run tests: `pytest`

### Uploading to pypi.org

Packaging is managed through GitHub Actions by publishing a release.

1. Bump `version` in `setup.py`
1. `git commit -am "chore: bump version"`
1. `git tag v1.2.1`
1. `git push && git push --tags`
1. `python setup.py sdist bdist_wheel`
1. `twine upload dist/*` (`pip install twine`, if needed)
