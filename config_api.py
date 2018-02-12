import requests
import json

class ConfigApi:
    def __init__(self, url, login, password):
        self.url = url
        self.login = login
        self.password = password

    def get_token(self):
        login_request = requests.get(self.url + '/login', auth=(self.login, self.password))
        return login_request.json()

    def get_config(self, file_output=None):
        r = requests.get(self.url + '/config', headers={'Token': self.get_token()})
        json_result = r.json()
        json_txt = json.dumps(json_result, ensure_ascii=False, indent=4)
        if file_output:
            with open(file_output, 'w', encoding='utf8') as fsock:
                fsock.write(json_txt)
        else:
            print(json_txt)