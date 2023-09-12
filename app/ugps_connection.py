import time

import requests
from loguru import logger


class UgpsConnection:
    """
    Copied from https://github.com/waterlinked/blueos-ugps-extension and modified.
    """

    def __init__(self, host="https://demo.waterlinked.com"):
        self.host = host

    def put(self, path, json):
        """
        Helper to request with POST from ugps
        Returns if request was successful
        """
        full_url = self.host + path
        logger.info(f"Request url: {full_url} json: {json}")
        try:
            response = requests.put(full_url, json=json, timeout=1)
            if response.status_code == 200:
                logger.info(f"Got response: {response.reason}")
                return True
            else:
                logger.error(f"Got HTTP Error: {response.status_code} {response.reason} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Got exception: {e}")
            return False

    def wait_for_connection(self):
        """
        Waits until the Underwater GPS system is available
        Returns when it is found
        """
        while True:
            logger.info("Scanning for Water Linked underwater GPS...")
            try:
                requests.get(self.host + "/api/v1/about/", timeout=1)
                break
            except Exception as e:
                logger.info(f"Got {e}")
            time.sleep(5)

    def send_ugps_topside_position(self, json):
        return self.put("/api/v1/external/master", json)
