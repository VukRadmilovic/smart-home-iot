import threading
import time

from broker_config.broker_settings import HOSTNAME, PORT
from components import uds
from helpers.printer import print_status
from value_queue import value_queue

import paho.mqtt.publish as publish


def motion(code, settings):
    print_status(code, "MOTION DETECTED")
    val = {
        "measurementName": "PIRStatus",
        "timestamp": round(time.time()*1000),
        "value": "MOTION",
        "deviceId": code,
        "deviceType": "PIR",
        "isSimulated": settings["simulated"]
    }
    value_queue.put(val)
    if code == "DPIR1":
        publish.single("DL", "ON", hostname=HOSTNAME, port=PORT)
    if code[0] == "D":
        print_status(code, "Last distance: " + str(uds.last_distance) + " cm, second last distance: " +
                     str(uds.second_last_distance) + " cm")
        if uds.last_distance < uds.second_last_distance:
            print_status(code, "Distance is decreasing, someone is entering")
            publish.single("tracker", "ENTER", hostname=HOSTNAME, port=PORT)
        else:
            print_status(code, "Distance is increasing, someone is leaving")
            publish.single("tracker", "EXIT", hostname=HOSTNAME, port=PORT)


def run(code, settings, threads, stop_event):
    if settings['simulated']:
        from simulators.pir import simulate
        thread = threading.Thread(target=simulate,
                                  args=(lambda: motion(code, settings), stop_event))
        thread.start()
        threads.append(thread)
    else:
        from sensors.pir import register
        thread = threading.Thread(target=register,
                                  args=(settings["pins"][0], lambda: motion(code, settings)))
        thread.start()
        threads.append(thread)
