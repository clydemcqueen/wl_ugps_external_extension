#! /usr/bin/env python3

"""
Listen for NMEA GGA and HDT messages and send the position information to the WL UGPS G2 API.

The default arguments allow for easy dev testing, see the Dockerfile for production arguments.
"""

import argparse
from typing import Any

import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from data_logger import LoggingConfig
from listen_thread import ListenThread
from polling_thread import PollingThread
from send_thread import SendThread
from topside_position import TopsidePosition


def run(args):
    """
    There are 4 threads:
    1. The listen_thread listens for NMEA messages on a UDP socket and keeps track of the vessel position
    2. The send_thread periodically sends the vessel position to a REST API on the WL UGPS G2 box
    3. The polling_thread periodically polls the G2 box for data and logs the results
    4. The primary thread serves up the UI
    """

    # Create a FastAPI app
    app = FastAPI(
        title="WL UGPS External Extension",
        description="Listen for NMEA GGA and HDT messages and send the position information to the WL UGPS G2 API",
    )

    # Current position
    topside_position = TopsidePosition()

    # Logging configuration
    logging = args.log_nmea or args.poll_rate > 0
    config = LoggingConfig() if logging else None

    # Start listening for NMEA messages
    listen_thread = ListenThread('0.0.0.0', 6200, topside_position, args.log_nmea, config)
    listen_thread.start()

    # Start sending the vessel position to the G2 box
    send_thread = SendThread(args.ugps_host, args.send_rate, topside_position)
    send_thread.start()

    # Start polling the G2 box for acoustic and other information
    if args.poll_rate > 0.0:
        polling_thread = PollingThread(args.ugps_host, args.poll_rate, config)
        polling_thread.start()
    else:
        polling_thread = None

    # Add a FastAPI route: /status returns a dictionary
    @app.get("/status", status_code=status.HTTP_200_OK)
    async def get_status() -> Any:
        return {
            'gga_status': topside_position.location_valid(),
            'hdt_status': topside_position.heading_valid(),
            'inject_status': send_thread.ok(),
            'latitude': topside_position.latitude,
            'longitude': topside_position.longitude,
            'heading': topside_position.heading,
            'ugps_host': args.ugps_host,
            'send_rate': args.send_rate,
        }

    # Create a FastAPI sub-application: serve static files in /app/static
    # This must come after more specific routes, e.g., /status
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

    # Add a FastAPI route: / returns index.html
    # Return index.html
    @app.get("/", response_class=FileResponse)
    async def root() -> Any:
        return "index.html"

    # Start the web server
    # Run with log disabled so loguru can handle it
    logger.info('Starting web server, press Ctrl-C to stop')
    uvicorn.run(app, host="0.0.0.0", port=8080, log_config=None)

    # Clean up
    logger.info('Cleaning up')
    if polling_thread is not None:
        polling_thread.stop()
        polling_thread.join()
    send_thread.stop()
    listen_thread.stop()
    send_thread.join()
    listen_thread.join()


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__)
    parser.add_argument('--ugps_host', type=str, default='https://demo.waterlinked.com',
                        help='UGPS (G2) url, default https://demo.waterlinked.com')
    parser.add_argument('--send_rate', type=float, default='2.0',
                        help='send vessel pose to the G2 at this rate, 0 means do not send, default 2')
    parser.add_argument('--poll_rate', type=float, default='5.0',
                        help='poll G2 for data and log it at this rate, 0 means do not poll, default 5')
    parser.add_argument('--log_nmea', action='store_true',
                        help='log incoming NMEA messages')
    run(parser.parse_args())


if __name__ == "__main__":
    logger.info(f"Starting wl_ugps_external_extension")
    main()
