import threading
import time

import util
from data_logger import AcousticLogger, LoggingConfig, PollingLogger


class PollingThread(threading.Thread):
    """
    Poll G2 endpoints and log the results.
    """

    TIMEOUT_S = 4.0

    def __init__(self, ugps_host: str, poll_rate: float, config: LoggingConfig):
        super().__init__()
        self.poll_rate = poll_rate
        self.lock = threading.Lock()
        self.stopping = False
        self.poll_time = None
        self.polling_loggers = [
            AcousticLogger(ugps_host + '/api/v1/position/acoustic/filtered', config.path_prefix + 'g2_acoustic.csv'),
            PollingLogger(ugps_host + '/api/v1/position/master', config.path_prefix + 'g2_position.csv', [
                'lat', 'lon', 'orientation', 'fix_quality', 'hdop', 'numsats', 'cog', 'sog']),
            PollingLogger(ugps_host + '/api/v1/imu/calibrate', config.path_prefix + 'g2_orientation.csv', [
                'roll', 'pitch', 'yaw', 'state', 'progress']),
        ]

    def once(self):
        for polling_logger in self.polling_loggers:
            polling_logger.poll()
        with self.lock:
            self.poll_time = time.time()

    def run(self):
        # If rate is 0, don't do anything
        while self.poll_rate > 0.0:
            with self.lock:
                if self.stopping:
                    break
            util.call_and_sleep(1.0 / self.poll_rate, self.once)

        for polling_logger in self.polling_loggers:
            polling_logger.close()

    def ok(self):
        with self.lock:
            return self.poll_time is not None and self.poll_time + self.TIMEOUT_S > time.time()

    def stop(self):
        with self.lock:
            self.stopping = True


# For testing
if __name__ == '__main__':
    util.test_main(PollingThread('https://demo.waterlinked.com', 1.0, LoggingConfig(local_test=True)))