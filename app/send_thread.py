import threading
import time

from loguru import logger

import util
from topside_position import TopsidePosition
from ugps_connection import UgpsConnection


class SendThread(threading.Thread):
    """
    Send the current heading and location to the G2 topside box at a constant rate.
    """

    TIMEOUT_S = 4.0

    def __init__(self, ugps_host: str, send_rate: float, topside_position):
        threading.Thread.__init__(self)
        self.send_rate = send_rate
        self.topside_position = topside_position
        self.lock = threading.Lock()
        self.stopping = False
        self.ugps_connection = UgpsConnection(host=ugps_host)
        self.send_time = None

    def once(self):
        json = self.topside_position.get_json()
        if json is not None:
            logger.info(f'Sending {json}')
            if self.ugps_connection.send_ugps_topside_position(json):
                with self.lock:
                    self.send_time = time.time()

    def run(self):
        # If rate is 0, don't do anything
        while self.send_rate > 0.0:
            with self.lock:
                if self.stopping:
                    break
            util.call_and_sleep(1.0 / self.send_rate, self.once)

    def ok(self):
        with self.lock:
            return self.send_time is not None and self.send_time + self.TIMEOUT_S > time.time()

    def stop(self):
        with self.lock:
            self.stopping = True


# For testing
if __name__ == '__main__':
    util.test_main(SendThread('https://demo.waterlinked.com', 1.0, TopsidePosition()))
