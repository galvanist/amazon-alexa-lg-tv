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

import fauxmo
import logging
import time
import os
from debounce_handler import debounce_handler

logging.basicConfig(level=logging.DEBUG)

APPS = {
    'netflix': 'netflix',
    'plex': 'cdp-30',
    'amazon': 'lovefilm',
}

class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """

    ACTIONS = ['tv', 'volume', 'mute', 'playback']

    TRIGGERS = {key: n+52000 for n, key in enumerate(ACTIONS+APPS.keys())}

    def act(self, client_address, state, name):
        print "State", state, "on ", name, "from client @", client_address
        if name == "tv" and state == True:
            os.system("python lgtv.py on")
            print "Magic packet sent to turn on TV!"
        elif name == "tv" and state == False:
            os.system("python lgtv.py off")
            print "TV turned off!"
        elif name == "mute" and state == True:
            os.system("python lgtv.py mute true")
            print "Muted"
        elif name == "mute" and state == False:
            os.system("python lgtv.py mute false")
            print "Unmuted"
        elif name == "volume" and state == True:
            os.system("python lgtv.py setVolume 20")
            print "Volume set to TWENTY"
        elif name == "volume" and state == False:
            os.system("python lgtv.py setVolume 0")
            print "Volume set to ZERO"
        elif name == "playback" and state == True:
            os.system("python lgtv.py inputMediaPlay")
            print "Playback set to RESUME"
        elif name == "playback" and state == False:
            os.system("python lgtv.py inputMediaPause")
            print "Playback set to PAUSE"
        elif name in APPS and state == True:
            os.system("python lgtv.py startApp {}".format(APPS[name]))
            print "Started app {}".format(name)
        elif name in APPS and state == False:
            os.system("python lgtv.py closeApp {}".format(APPS[name]))
            print "Stopped app {}".format(name)
        return True


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

