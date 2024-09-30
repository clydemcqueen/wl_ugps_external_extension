import threading
import time

import nmea_sentences


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

    def put_gga(self, gga: nmea_sentences.GGA):
        with self.lock:
            self.location_time = time.time()
            self.fix_quality = gga.fix_quality
            self.hdop = gga.hdop
            self.latitude = gga.latitude
            self.longitude = gga.longitude
            self.numsats = gga.numsats

    def put_hdt(self, hdt: nmea_sentences.HDT):
        with self.lock:
            self.heading_time = time.time()
            self.heading = hdt.heading

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
