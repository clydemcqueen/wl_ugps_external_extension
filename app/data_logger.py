import csv
import datetime
import pathlib
import time
from typing import Optional

import requests
from loguru import logger


def get_data(url) -> Optional[dict]:
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        logger.error(f'Exception occurred {e}')
        return None

    if r.status_code != requests.codes.ok:
        logger.error(f'Got error {r.status_code}: {r.text}')
        return None

    return r.json()


def flatten_list_value(d: dict, old_key: str, new_key_format: str):
    # Add new items, one for each value in the list
    # The new key names are generated from new_key_format
    list_value = d[old_key]
    for i in range(len(list_value)):
        d[new_key_format.format(i=i)] = list_value[i]

    # Delete the list
    del d[old_key]


class LoggingConfig:
    """
    Data logs are stored in /data/logs/<date>/<date>_<time>_<log_name>.csv
    The Dockerfile maps /data to /usr/blueos/extensions/wl_ugps_external on the Pi
    Users can find the data logs in the BlueOS File Browser at /extensions/wl_ugps_external
    """

    def __init__(self, local_test=False):
        now = datetime.datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H-%M-%S')
        dir_str = '/tmp/wl_ugps_test/' + date_str if local_test else '/data/logs/' + date_str
        pathlib.Path(dir_str).mkdir(parents=True, exist_ok=True)
        self.path_prefix = dir_str + '/' + date_str + '_' + time_str + '_'


class DataLogger:
    """
    Write rows to a csv file.
    """

    def __init__(self, filename: str, fieldnames: list[str]):
        """
        :param filename: log to this file
        :param fieldnames: log these fields in this order. 'timestamp' will be added to the front of the list.
        """
        logger.info(f'Writing to {filename}')
        self.csv_file = open(filename, 'w', newline='')
        # noinspection PyTypeChecker
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=['timestamp', *fieldnames])
        self.csv_writer.writeheader()
        self.csv_file.flush()

    def log(self, row: dict):
        # Add host (Pi) time, seconds since Unix epoch
        row['timestamp'] = time.time()
        self.csv_writer.writerow(row)
        self.csv_file.flush()

    def close(self):
        self.csv_file.close()


class PollingLogger(DataLogger):
    """
    Poll an endpoint and log the results.
    """

    def __init__(self, endpoint: str, filename: str, fieldnames: list[str]):
        super().__init__(filename, fieldnames)
        self.endpoint = endpoint

    def poll(self):
        row = get_data(self.endpoint)
        if row is not None:
            self.log(row)


class AcousticLogger(PollingLogger):
    """
    Special case for /api/v1/position/acoustic/filtered.
    """

    def __init__(self, endpoint: str, filename: str):
        super().__init__(endpoint, filename, [
            'position_valid', 'x', 'y', 'z', 'std',
            'distance_r0', 'distance_r1', 'distance_r2', 'distance_r3',
            'nsd_r0', 'nsd_r1', 'nsd_r2', 'nsd_r3',
            'rssi_r0', 'rssi_r1', 'rssi_r2', 'rssi_r3',
            'valid_r0', 'valid_r1', 'valid_r2', 'valid_r3'])

    def poll(self):
        row = get_data(self.endpoint)
        if row is None:
            return

        # Flatten lists
        flatten_list_value(row, 'receiver_distance', 'distance_r{i}')
        flatten_list_value(row, 'receiver_nsd', 'nsd_r{i}')
        flatten_list_value(row, 'receiver_rssi', 'rssi_r{i}')
        flatten_list_value(row, 'receiver_valid', 'valid_r{i}')

        self.log(row)
