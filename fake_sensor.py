import time
import random


def fake_sensor(selected_frequency=20.0, queue=None, signal=None):
    # Computing the sleeping time
    sleep_time = 1 / selected_frequency
    # Keep a reference to the first timestamp of the series
    start_time = -1

    while signal.is_set():
        # Computing the elapsed time
        current_time = time.time()
        if start_time == -1:
            start_time = current_time
        time_elapsed = current_time - start_time

        # Generate a random float number in [0, 10)
        fake_value = random.random() * 10

        # Insert data in the queue
        queue.put([time_elapsed, fake_value])

        # Simulating the sampling frequency
        time.sleep(sleep_time)
