# [Conversion Tools](https://conversiontools.io) API Python Client

[Conversion Tools](https://conversiontools.io) is an online service that offers a fast and easy way to convert documents between different formats, like XML, Excel, PDF, Word, Text, CSV and others.

This Client allows to integrate the conversion of the files into Python applications.

To convert the files Python Client uses the public [Conversion Tools REST API](https://conversiontools.io/api-documentation).

## Installation

```bash
pip install --upgrade conversiontools
```

or when building from the sources:

```bash
python setup.py install
```

## Examples

To use REST API - get API Token from the Profile page at https://conversiontools.io/profile.

See example `test.py` in the `./examples/` folder.

```python
from conversiontools import ConversionClient

# put token here from your Profile page at https://conversiontools.io/profile
token = ''

# files
fileInput = 'test.xml'
fileOutput = 'test.csv'

client = ConversionClient(token)
try:
    client.convert('convert.xml_to_csv', fileInput, fileOutput, { 'delimiter': 'tabulation' })
except Exception as error:
    print(error)
```

## API

### Create `ConversionClient` instance with a token.
```python
from conversiontools import ConversionClient
client = ConversionClient('<token>')
```

Where `<token>` is API token from the account's Profile page https://conversiontools.io/profile.

### Convert input file and download the result
```python
try:
    client.convert('<conversion type>', fileInput, fileOutput, '<options>')
except Exception as error:
    print(error)
```

Where
- `<conversion type>` is a specific type of conversion, from [API Documentation](https://conversiontools.io/api-documentation).
- `<options>` is a Python dict with options for a corresponding converter, for example:
```python
options = { 'delimiter': 'tabulation' }
```

## Documentation

List of available Conversion Types and corresponding conversion options can be found on the [Conversion Tools API Documentation](https://conversiontools.io/api-documentation) page.

## License

Licensed under [MIT](./LICENSE).

Copyright (c) 2020 [Conversion Tools](https://conversiontools.io)
