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
