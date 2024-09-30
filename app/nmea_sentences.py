from typing import NamedTuple

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
    def from_sentence(sentence: pynmea2.GGA):
        return GGA(
            float(sentence.data[0]),
            sentence.latitude,
            sentence.longitude,
            int(sentence.data[5]),
            int(sentence.data[6]),
            float(sentence.data[7]),
            float(sentence.data[8])
        )

    def as_dict(self):
        return self._asdict()


class HDT(NamedTuple):
    heading: float

    @classmethod
    def fieldnames(cls):
        return list(cls._fields)

    @staticmethod
    def from_sentence(sentence: pynmea2.HDT):
        return HDT(
            float(sentence.data[0])
        )

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
    def from_sentence(sentence: pynmea2.types.proprietary.ash.ASHRATT):
        if not sentence.is_true_heading:
            logger.warning('Expected true heading in $PASHR, found something else')
        return PASHR(
            sentence.true_heading,
            sentence.roll,
            sentence.pitch,
            sentence.heave,
            sentence.roll_accuracy,
            sentence.pitch_accuracy,
            sentence.heading_accuracy,
            sentence.aiding_status,
            sentence.imu_status
        )

    def as_dict(self):
        return self._asdict()
