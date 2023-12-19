import time
import random


def simulate(code, callback, stop_event, delay):
    while True:
        if stop_event.is_set():
            break
        time.sleep(delay)
        humidity = random.uniform(40, 70)
        temperature = random.uniform(20, 30)
        callback(code, humidity, temperature)
