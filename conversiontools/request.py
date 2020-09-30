import conversiontools
import requests

user_agent = 'conversiontools-python/' + conversiontools.__version__

def prepareHeaders(token):
    headers = {
        'Authorization': 'Bearer ' + token,
        'User-Agent': user_agent
    }
    return headers

def requestAPI(method, url, token, data=None):
    headers = prepareHeaders(token)
    response = requests.request(method, url, headers=headers, json=data)
    data = response.json()
    return data

def uploadAPI(url, token, files):
    headers = prepareHeaders(token)
    response = requests.request('POST', url, headers=headers, files=files)
    data = response.json()
    return data

def downloadAPI(url, token):
    headers = prepareHeaders(token)
    response = requests.request('GET', url, headers=headers)
    return response.content
