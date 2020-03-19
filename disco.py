import os
import sys
from hashlib import md5
from base64 import b64encode

import requests
import magic
from dotenv import load_dotenv
from pypresence import Presence

from gi.repository import Playerctl, GLib


def encFile(filename):
    with open(filename, 'rb') as f:
        return b64encode(f.read()).decode('ascii')


def login(username, password):
    r = requests.post(
        'https://discordapp.com/api/v6/auth/login', json={
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


def imgStr(filename):
    return 'data:{};base64,{}'.format(
        magic.from_file(filename, True),
        encFile(filename)
    )


def uploadImage(token, appID, filename, imageName):
    img = imgStr(filename)

    r = requests.post(
        'https://discordapp.com/api/v6/oauth2/applications/{}/assets'.format(
            appID
        ),
        json={
            'name': imageName,
            'type': '1',
            'image': img
        },
        headers={
            'Authorization': token,
        }
    )

    return r.json()['id']


def deleteImage(token, appID, imgID):
    requests.delete(
        'https://discordapp.com/api/v6/oauth2/applications/{}/assets/{}'.format(
            appID,
            imgID
        ),
        headers={
            'Authorization': token,
        }
    )


# The data of the previous playing song
prevData = None


def updateMusic():
    metadata = player.props.metadata
    playing = player.props.playback_status == Playerctl.PlaybackStatus.PLAYING

    data = {
        'title': metadata['xesam:title'],
        'artist': ', '.join(metadata['xesam:artist']),
        'album': metadata['xesam:album'],
        'artPath': metadata['mpris:artUrl'].replace('file://', '', 1),
        'artName': md5(metadata['xesam:album'].encode()).hexdigest(),
        'artID': 0
    }

    global prevData

    # if prevData == None or prevData['artName'] != data['artName']:
    print(uploadImage(token, appID, data['artPath'], data['artName']))

    print(data['artName'])
    presence.update(
        large_image=data['artName'],
        state=data['artist'],
        large_text=data['album'],
        details=data['title'],
    )

    prevData = data


# Initialize config
load_dotenv()

token = login(
    os.getenv('username'),
    os.getenv('password')
)

if not token:
    print('Login attempt failed. Exiting...')
    sys.exit(1)

appID = os.getenv('appid')

presence = Presence(appID)
presence.connect()

player = Playerctl.Player()
player.connect('metadata', lambda p, m: updateMusic())

updateMusic()

# wait for events
main = GLib.MainLoop()
main.run()
