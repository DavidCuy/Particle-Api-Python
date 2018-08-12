from Particle.Defaults import defualt
import requests
from requests.auth import HTTPBasicAuth
import pprint
import sseclient
import json
import threading

class Particle:
    def __init__(self, token = None):
        self.defualt = defualt
        self.Token = token

    def _uriAppend(self, append):
        return self.defualt.baseUrl + append

    @classmethod
    def login(cls, username, password, callbacks = {'success': None, 'error': None}):
        payload = {
            'username': username,
            'password': password,
            'grant_type': 'password',
            'client_id': defualt.clientId,
            'client_secret': defualt.clientSecret,
            'expires_in': defualt.tokenDuration
        }
        r = requests.post(defualt.baseUrl + "/oauth/token", payload)
        resp = r.json()
        if('error' in resp):
            if(callbacks['error'] is None):
                print("ERROR:\n" + r.text)
                return False
            else:
                callbacks['error'](resp)
                return False
        else:
            particle = cls(resp["access_token"])
            if (callbacks['success'] is None):
                print("SUCCESS:\n" + r.text)
                return particle
            else:
                callbacks['success'](resp)
                return particle

    @staticmethod
    def getTokenList(username, password, error_callback = None):
        r = requests.get(defualt.baseUrl + "/v1/access_tokens", auth=HTTPBasicAuth(username, password))
        resp = r.json()
        if ('error' in resp):
            if (error_callback is None):
                print("ERROR:\n" + r.text)
                return False
            else:
                error_callback(resp)
                return False
        else:
            return resp


    @classmethod
    def loginWithExistToken(cls, username, password):
        tokens = Particle.getTokenList(username, password)
        if tokens == False:
            return False
        for token in tokens:
            if token['client'] == '__PASSWORD_ONLY__':
                particle = cls(token["token"])
                return particle
        return False

    def logout_DeleteToken(self, username, password, error_callback=None):
        r = requests.delete(self._uriAppend('/v1/access_tokens/' + self.Token), auth=HTTPBasicAuth(username, password))
        resp = r.json()
        if ('error' in resp):
            if (error_callback is None):
                print("ERROR:\n" + r.text)
                return False
            else:
                error_callback(resp)
                return False
        else:
            return True

    def listDevices(self, error_callback = None):
        headers = {'Authorization': "Bearer " + self.Token}
        r = requests.get(self._uriAppend('/v1/devices'), headers=headers)
        resp = r.json()
        if ('error' in resp):
            if (error_callback is None):
                print(r.text)
                return False
            else:
                error_callback(resp)
                return False
        else:
            arrayDev = []
            for dev in resp:
                device = ParticleDevice.from_JSON(self.Token, dev)
                arrayDev.append(device)
            return arrayDev

    def getDeviceFromId(self, deviceId, error_callback=None):
        headers = {'Authorization': "Bearer " + self.Token}
        r = requests.get(self._uriAppend('/v1/devices/' + deviceId), headers=headers)
        resp = r.json()
        if ('error' in resp):
            if (error_callback is None):
                print(r.text)
                return False
            else:
                error_callback(resp)
                return False
        else:
            return ParticleDevice.from_JSON(self.Token, resp)

    def getEventStreamEvent(self, eventName, streamCallback = None):
        url = self._uriAppend('/v1/devices/events/' + eventName)
        headers = {'Authorization': "Bearer " + self.Token}
        t = threading.Thread(target=self._event_loop, args=(streamCallback, url, headers))
        t.daemon = True
        t.start()

    def getDeviceStreamEvent(self, deviceId, eventName, streamCallback = None):
        url = self._uriAppend('/v1/devices/' + deviceId + '/events/' + eventName)
        headers = {'Authorization': "Bearer " + self.Token}
        t = threading.Thread(target=self._event_loop, args=(streamCallback, url, headers))
        t.daemon = True
        t.start()

    def _event_loop(self, callback, url, headers):
        response = requests.get(url, stream=True, headers=headers)
        client = sseclient.SSEClient(response)
        for event in client.events():
            if (callback is None):
                pprint.pprint(json.loads(event.data))
            else:
                callback(json.loads(event.data))

class ParticleDevice(Particle):
    def __init__(self, token, id, name, last_app, last_ip_address, last_heard, product_id, connected, platform_id, cellular, notes, status, current_build_target, system_firmware_version, default_build_target):
        Particle.__init__(self, token=token)
        self.id = id
        self.name = name
        self.last_app = last_app
        self.last_ip_address = last_ip_address
        self.last_heard = last_heard
        self.product_id = product_id
        self.connected = connected
        self.platform_id = platform_id
        self.cellular = cellular
        self.notes = notes
        self.status = status
        self.current_build_target = current_build_target
        self.system_firmware_version = system_firmware_version
        self.default_build_target = default_build_target

    def __str__(self):
        try:
            return "ParticleDevice[Id]:" + self.id + "-" + self.name
        except TypeError:
            return "ParticleDevice[Id]:" + self.id + "-" + "[NO_NAME]"

    @classmethod
    def from_JSON(cls, token, jsonObj):
        id = jsonObj["id"]
        name = jsonObj["name"]
        last_app = jsonObj["last_app"]
        last_ip_address = jsonObj["last_ip_address"]
        last_heard = jsonObj["last_heard"]
        product_id = jsonObj["product_id"]
        connected = jsonObj["connected"]
        platform_id = jsonObj["platform_id"]
        cellular = jsonObj["cellular"]
        notes = jsonObj["notes"]
        status = jsonObj["status"]
        current_build_target = jsonObj["current_build_target"]
        system_firmware_version = jsonObj["system_firmware_version"]
        default_build_target = jsonObj["default_build_target"]

        device = cls(token, id, name, last_app, last_ip_address, last_heard, product_id, connected, platform_id, cellular, notes, status, current_build_target, system_firmware_version, default_build_target)
        return device

    def getDeviceInfo(self, error_callback = None):
        headers = {'Authorization': "Bearer " + self.Token}
        r = requests.get(Particle._uriAppend(self, '/v1/devices/' + self.id), headers=headers)
        resp = r.json()
        if ('error' in resp):
            if (error_callback is None):
                print(r.text)
                return False
            else:
                error_callback(resp)
                return False
        else:
            return resp

    def getStreamEvent(self, eventName, streamCallback = None):
        url = self._uriAppend('/v1/devices/' + self.id + '/events/' + eventName)
        headers = {'Authorization': "Bearer " + self.Token}
        t = threading.Thread(target=self._event_loop, args=(streamCallback, url, headers))
        t.daemon = True
        t.start()