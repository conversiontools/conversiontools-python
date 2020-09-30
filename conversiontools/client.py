import time
from .api import *

class ConversionClient:

    def __init__(self, token):
      self.token = token

    def convert(self, type, input, output, options=None):
        token = self.token
        file_id = uploadFile(token, input)
        task_id = createTask(token, type, file_id, options)
        while True:
            taskStatus = getTaskStatus(token, task_id)
            status = taskStatus['status']
            file_id = taskStatus['file_id']
            if status == 'SUCCESS':
                downloadFile(token, file_id, output)
                break
            if status == 'ERROR':
                break
            time.sleep(5)
