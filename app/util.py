import time
from typing import Callable

from loguru import logger


def call_and_sleep(period: float, func: Callable):
    """
    Call a function, then sleep long enough to fill the period
    :param period: seconds to consume
    :param func: function to call
    """
    start = time.time()
    func()
    elapsed = time.time() - start
    remainder = period - elapsed
    if remainder > 0:
        time.sleep(remainder)


def test_main(thread):
    thread.start()
    logger.info('Press Ctrl-C to stop')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Ctrl-C detected')
    finally:
        thread.stop()
        thread.join()
