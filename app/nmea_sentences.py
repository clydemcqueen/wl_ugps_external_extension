from typing import NamedTuple, Optional

import pynmea2.types.proprietary.ash
from loguru import logger


class GGA(NamedTuple):
    utc: float
    latitude: float
    longitude: float
    fix_quality: int
    numsats: int
    hdop: float
    orthometric_height: float

    @classmethod
    def fieldnames(cls):
        return list(cls._fields)

    @staticmethod
    def from_sentence(sentence: pynmea2.GGA) -> Optional['GGA']:
        try:
            if (not sentence.data or
                    sentence.data[0] == '' or
                    sentence.data[5] in ('', '0') or
                    sentence.data[6] == '' or
                    sentence.data[7] == '' or
                    sentence.data[8] == '' or
                    sentence.latitude is None or
                    sentence.longitude is None):
                return None
            return GGA(
                float(sentence.data[0]),
                float(sentence.latitude),
                float(sentence.longitude),
                int(sentence.data[5]),
                int(sentence.data[6]),
                float(sentence.data[7]),
                float(sentence.data[8])
            )
        except (ValueError, TypeError, IndexError):
            return None

    def as_dict(self):
        return self._asdict()


class HDT(NamedTuple):
    heading: float

    @classmethod
    def fieldnames(cls):
        return list(cls._fields)

    @staticmethod
    def from_sentence(sentence: pynmea2.HDT) -> Optional['HDT']:
        try:
            if not sentence.data or sentence.data[0] == '':
                return None
            return HDT(
                float(sentence.data[0])
            )
        except (ValueError, TypeError, IndexError):
            return None

    def as_dict(self):
        return self._asdict()


class PASHR(NamedTuple):
    """
    Proprietary sentence, manufacturer=ASH, type=R
    Published by Advanced Navigation GNSS compass
    """
    heading: float
    roll: float
    pitch: float
    heave: float
    roll_sigma: float
    pitch_sigma: float
    heading_sigma: float
    aiding_status: int
    imu_status: int

    @classmethod
    def fieldnames(cls):
        return list(cls._fields)

    @staticmethod
    def from_sentence(sentence: pynmea2.types.proprietary.ash.ASHRATT) -> Optional['PASHR']:
        if not getattr(sentence, 'is_true_heading', False):
            logger.warning('Expected true heading in $PASHR, found something else')
        try:
            if getattr(sentence, 'true_heading', None) is None:
                return None
            return PASHR(
                float(sentence.true_heading),
                float(sentence.roll),
                float(sentence.pitch),
                float(sentence.heave),
                float(sentence.roll_accuracy),
                float(sentence.pitch_accuracy),
                float(sentence.heading_accuracy),
                int(sentence.aiding_status),
                int(sentence.imu_status)
            )
        except (ValueError, TypeError, AttributeError, IndexError):
            return None

    def as_dict(self):
        return self._asdict()
