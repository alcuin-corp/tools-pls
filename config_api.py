import requests
import json
import logger


def is_success(result):
    return 200 <= result.status_code < 300


class ConfigApi(logger.Logger):
    def __init__(self, url, login, password):
        self.url = url
        self.login = login
        self.password = password

    def get_token(self):
        login_request = requests.get(self.url + '/login', auth=(self.login, self.password))
        return login_request.json()

    def get_config(self, file_output=None):
        r = requests.get(self.url + '/config', headers={'Token': self.get_token()})
        if not is_success(r):
            self.error(f'Export failure')
            print(r.json())
        json_result = r.json()
        json_txt = json.dumps(json_result, ensure_ascii=False, indent=4)
        if file_output:
            with open(file_output, 'w', encoding='utf8') as fsock:
                fsock.write(json_txt)
                self.ok(f'Application exported to {file_output}')
        else:
            print(json_txt)

    def fixguid(self):
        r = requests.post(self.url + '/fixguid', headers={'Token': self.get_token()})
        if is_success(r):
            self.ok(f'GUID fixed (http status {r.status_code})')
        else:
            self.error(f'Problem occured while fixing GUID (http status {r.status_code}), please check logs')
