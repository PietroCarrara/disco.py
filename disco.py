import requests
from base64 import b64encode

def encFile(fileName):
    with open(fileName, 'rb') as f:
        return b64encode(f.read())

def login(username, password):
    r = requests.post(
        'https://discordapp.com/api/v6/auth/login', json = {
            'email': username,
            'password': password,
            'undelete': False,
            'captcha_key': None,
            'login_source': None,
            'gift_code_sku_id': None
    })
    json = r.json()

    if 'token' in json:
        return json['token']
    else:
        return None