import threading
import time

from helpers.printer import print_status
from simulators.buzzer import run_buzzer_simulator
from value_queue import value_queue
import paho.mqtt.client as mqtt
from broker_config.broker_settings import HOSTNAME,PORT

alarm_clock_buzz_event = None
alarm_clock_stop_event = None

def on_connect(client, userdata, flags, rc):
    client.subscribe("alarm_clock_buzz")

def on_message(client, userdata, msg):
    status = msg.payload.decode('utf-8')
    if status == "START":
        alarm_clock_buzz_event.trigger()
    else:
        alarm_clock_stop_event.trigger()


def buzzer_callback(code, settings, status):
    print_status(code, status)
    val = {
        "measurementName": "buzzerStatus",
        "timestamp": round(time.time() * 1000),
        "value": status,
        "deviceId": code,
        "deviceType": "BUZZER",
        "isSimulated": settings["simulated"],
        "pi": settings["pi"]

    }
    value_queue.put(val)


def run_buzzer(code, settings, threads, buzzer_press_event, buzzer_release_event, alarm_clock_on_event, alarm_clock_off_event, stop_event):
    global alarm_clock_buzz_event, alarm_clock_stop_event
    alarm_clock_buzz_event = alarm_clock_on_event
    alarm_clock_stop_event = alarm_clock_off_event
    if code == "BB":
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(HOSTNAME, PORT)
        client.loop_start()
    if settings['simulated']:
        buzzer_thread = threading.Thread(target=run_buzzer_simulator,
                                         args=(lambda status: buzzer_callback(code, settings, status),
                                               buzzer_press_event, buzzer_release_event, alarm_clock_buzz_event, alarm_clock_stop_event, stop_event))
        buzzer_thread.start()
        threads.append(buzzer_thread)
    else:
        from actuators.buzzer import buzzer_register
        buzzer_thread = threading.Thread(target=buzzer_register, args=(settings["pins"][0], 440,
                                                                       lambda status: buzzer_callback(code, settings,
                                                                                                      status),
                                                                       buzzer_press_event, buzzer_release_event, alarm_clock_buzz_event, alarm_clock_stop_event, stop_event))
        buzzer_thread.start()
        threads.append(buzzer_thread)
