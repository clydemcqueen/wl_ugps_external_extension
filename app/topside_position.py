import threading
import time

import pynmea2
from loguru import logger


class TopsidePosition:
    """
    Current topside position.
    """

    TIMEOUT_S = 4.0

    def __init__(self):
        self.lock = threading.Lock()
        self.location_time = None
        self.heading_time = None

        # Fields required to call /api/v/external/master
        self.cog = 0
        self.fix_quality = 0
        self.hdop = 0
        self.latitude = 0
        self.longitude = 0
        self.numsats = 0
        self.heading = 0
        self.sog = 0

    def recv_packet(self, packet):
        """
        Packet format is:
        <sentence><cr><lf><sentence><cr><lf><sentence><cr><lf>...
        """
        sentence_strs = packet.decode().split('\r\n')
        for sentence_str in sentence_strs:
            if sentence_str == '':
                continue

            sentence = pynmea2.parse(sentence_str)
            logger.info(sentence)

            if sentence.sentence_type == 'GGA':
                self.recv_gga(sentence)
            elif sentence.sentence_type == 'HDT':
                self.recv_hdt(sentence)

    def recv_gga(self, sentence):
        with self.lock:
            self.location_time = time.time()
            self.fix_quality = int(sentence.data[5])
            self.hdop = float(sentence.data[7])
            self.latitude = sentence.latitude
            self.longitude = sentence.longitude
            self.numsats = int(sentence.data[6])

    def recv_hdt(self, sentence):
        with self.lock:
            self.heading_time = time.time()
            self.heading = float(sentence.data[0])

    def location_valid(self):
        return self.location_time is not None and self.location_time + self.TIMEOUT_S > time.time()

    def heading_valid(self):
        return self.heading_time is not None and self.heading_time + self.TIMEOUT_S > time.time()

    def position_valid(self):
        return self.location_valid() and self.heading_valid()

    def get_json(self):
        with self.lock:
            if self.position_valid():
                return {
                    'cog': self.cog,
                    'fix_quality': self.fix_quality,
                    'hdop': self.hdop,
                    'lat': self.latitude,
                    'lon': self.longitude,
                    'numsats': self.numsats,
                    'orientation': self.heading,
                    'sog': self.sog,
                }
            else:
                return None
