# sweeper

fix data

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

`city`

`zip_code`

`normalized`
A normalized string representing the entire address that was passed into the constructor.

## development

1. create conda environment
   - `conda create --clone arcgispro-py3 --name sweeper`
1. activate environment
   - `activate sweeper`
1. install dependencies
   - `conda install -y -f --file requirements.dev.txt`
1. run tests: `pytest`
