from Particle.Particle import Particle
from config import MyConfig
import pprint
import time

def error_listing_tokens(resp):
    print("Can not list token")
    print(resp)

def error_listDev(resp):
    print("Con not list devices")
    print(resp)

def streamCallback_Dev1(resp):
    print("************     Device1 fires a new event     ************")
    pprint.pprint(resp)

def streamCallback_Dev2(resp):
    print("************     Device2 fires a new New event     ************")
    pprint.pprint(resp)

def main():
    print("************     Main Python Api ParticleCloud     ************")
    print("1. List all tokens in my Particle account")
    tokens = Particle.getTokenList(MyConfig.PARTICLE_USERNAME, MyConfig.PARTICLE_PASSWORD, error_listing_tokens)
    for token in tokens:
        print(token)

    print("2. Login with an existing token")
    particle = Particle.loginWithExistToken(MyConfig.PARTICLE_USERNAME, MyConfig.PARTICLE_PASSWORD)
    if(particle == False):
        print("Can not use a existing token")
        return

    print("3. List all devices in my account")
    devices = particle.listDevices(error_listDev)
    for device in devices:
        print(device)

    print("4. Make a listener of an device")
    device1 = particle.getDeviceFromId(MyConfig.PARTICLE_DEVICE1_ID)
    device1.getStreamEvent(MyConfig.PARTICLE_EVENT, streamCallback_Dev1)

    print("4. Make a second listener of an device, to probe the asynchronus proccess")
    device2 = particle.getDeviceFromId(MyConfig.PARTICLE_DEVICE2_ID)
    device2.getStreamEvent(MyConfig.PARTICLE_EVENT, streamCallback_Dev2)


if __name__ == "__main__":
    main()
    while True:
        ## TODO MAKE A PING REQUEST ALSO IN PARTICLE.PY
        time.sleep(10)

