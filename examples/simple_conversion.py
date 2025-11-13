"""
Simple conversion example
"""

from conversiontools import ConversionToolsClient

# Initialize client with API token
# Get your token from https://conversiontools.io/profile
client = ConversionToolsClient({
    'api_token': 'your-api-token'
})

# Convert XML to Excel
print("Converting XML to Excel...")
client.convert(
    'convert.xml_to_excel',
    'test.xml',
    'result.xlsx'
)
print("Conversion complete! Result saved to result.xlsx")

# Convert JSON to CSV with options
print("\nConverting JSON to CSV...")
client.convert(
    'convert.json_to_csv',
    'data.json',
    'data.csv',
    options={
        'delimiter': 'comma',
        'quote': True
    }
)
print("Conversion complete! Result saved to data.csv")
