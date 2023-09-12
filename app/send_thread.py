import threading
import time

from loguru import logger

from ugps_connection import UgpsConnection


class SendThread(threading.Thread):
    """
    Send the current heading and location to the G2 topside box at a constant rate.
    """

    TIMEOUT_S = 4.0

    def __init__(self, ugps_host: str, send_rate: float, topside_position):
        threading.Thread.__init__(self)

        self.ugps_host = ugps_host
        self.send_rate = send_rate
        self.topside_position = topside_position

        self.lock = threading.Lock()
        self.stopping = False
        self.ugps_connection = UgpsConnection(host=self.ugps_host)
        self.send_time = None

    def run(self):
        # If rate is 0, don't do anything
        while self.send_rate > 0.0:
            with self.lock:
                if self.stopping:
                    break

            json = self.topside_position.get_json()

            if json is not None:
                logger.info(f'Sending {json}')
                if self.ugps_connection.send_ugps_topside_position(json):
                    # Note the success
                    with self.lock:
                        self.send_time = time.time()

            time.sleep(1.0 / self.send_rate)

    def ok(self):
        with self.lock:
            return self.send_time is not None and self.send_time + self.TIMEOUT_S > time.time()

    def stop(self):
        with self.lock:
            self.stopping = True
