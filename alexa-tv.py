""" fauxmo_minimal.py - Fabricate.IO

    This is a demo python file showing what can be done with the debounce_handler.
    The handler prints True when you say "Alexa, device on" and False when you say
    "Alexa, device off".

    If you have two or more Echos, it only handles the one that hears you more clearly.
    You can have an Echo per room and not worry about your handlers triggering for
    those other rooms.

    The IP of the triggering Echo is also passed into the act() function, so you can
    do different things based on which Echo triggered the handler.
"""

import logging
import time

import fauxmo
from lgtv import LGTVClient

from debounce_handler import debounce_handler

logging.basicConfig(level=logging.INFO)

APPS = {
    'netflix': 'netflix',
    'amazon': 'lovefilm',
    'now tv': 'now.tv',
    'iplayer': 'bbc.iplayer.3.0',
    'itv': 'com.fvp.itv',
    'four': 'com.fvp.ch4',
}

class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """

    ACTIONS = ['tv', 'volume', 'mute', 'playback']

    TRIGGERS = {key: n+52000 for n, key in enumerate(ACTIONS+APPS.keys())}

    def act(self, client_address, state, name):
        print "State {} on {} from client @ {}".format(state, name, client_address)
        ws = LGTVClient()
        if name == "tv" and state == True:
            ws.on()
        else:
            ws.connect() # for any following command
        if name == "tv" and state == False:
            ws.exec_command('off', {})
        elif name == "mute" and state == True:
            ws.exec_command('mute', {'muted': True})
        elif name == "mute" and state == False:
            ws.exec_command('mute', {'muted': False})
        elif name == "volume" and state == True:
            ws.exec_command('setVolume', {'level': 10})
        elif name == "volume" and state == False:
            ws.exec_command('setVolume', {'level': 0})
        elif name == "playback" and state == True:
            ws.exec_command('inputMediaPlay', {})
        elif name == "playback" and state == False:
            ws.exec_command('inputMediaPause', {})
        elif name in APPS and state == True:
            ws.exec_command('startApp', {'appid': APPS[name]})
        elif name in APPS and state == False:
            ws.exec_command('closeApp', {'appid': APPS[name]})
        return True
        ws.run_forever()

if __name__ == "__main__":
    # Startup the fauxmo server
    fauxmo.DEBUG = True
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    # Register the device callback as a fauxmo handler
    d = device_handler()
    for trig, port in d.TRIGGERS.items():
        fauxmo.fauxmo(trig, u, p, None, port, d)

    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    while True:
        try:
            # Allow time for a ctrl-c to stop the process
            p.poll(100)
            time.sleep(0.1)
        except Exception, e:
            logging.critical("Critical exception: " + str(e))
            break

