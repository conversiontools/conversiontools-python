from .request import requestAPI, uploadAPI, downloadAPI

base_url = 'https://api.conversiontools.io/v1'

def uploadFile(token, name):
    fd = open(name, 'rb')
    file = { 'file': fd }
    result = uploadAPI(base_url + '/files', token, file)
    if result['error'] != None:
        raise Exception(result['error'])
    return result['file_id']

def createTask(token, type, file_id, options=None):
    data = {
        'type': type,
        'options': {
            'file_id': file_id
        }
    }
    data['options'].update(options)

    result = requestAPI('POST', base_url + '/tasks', token, data)
    if result['error'] != None:
        raise Exception(result['error'])
    return result['task_id']

def getTaskStatus(token, task_id):
    result = requestAPI('GET', base_url + '/tasks/' + task_id, token)
    errorMessage = result['error']
    status = result['status']
    file_id = result['file_id']
    if errorMessage != None:
        raise Exception(errorMessage)
    return { "status": status, "file_id": file_id }

def downloadFile(token, file_id, filename):
    result = downloadAPI(base_url + '/files/' + file_id, token)
    fd = open(filename, 'wb')
    fd.write(result)
    fd.close()
