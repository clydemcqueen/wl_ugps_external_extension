#!/usr/bin/env python3

"""
Send fake NMEA 0183 GGA, HDM and HDT sentences to a UDP port.
"""

import argparse
import socket
import time
from datetime import datetime

from nmeasim.models import TZ_LOCAL
from nmeasim.simulator import Simulator


def sentences_to_packet(sentences: list[str]) -> bytes:
    """
    Packet format should be:
    <sentence><cr><lf><sentence><cr><lf><sentence><cr><lf>...
    Reference: https://stripydog.blogspot.com/2015/03/nmea-0183-over-ip-unwritten-rules-for.html
    """
    return ('\r\n'.join(sentences) + '\r\n').encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='target IP address')
    parser.add_argument('--port', type=int, default='10110', help='target port')
    args = parser.parse_args()

    print(f'Sending packets to {args.ip}:{args.port}')
    print('Press Ctrl-C to stop')

    # Initialize NMEA simulator
    sim = Simulator()
    with sim.lock:
        # Can re-order or drop some
        sim.gps.output = ('GGA', 'HDM', 'HDT')
        sim.gps.num_sats = 14
        sim.gps.lat = 47.6075779801547
        sim.gps.lon = -122.34390446166833
        sim.gps.altitude = 0
        sim.gps.kph = 1.0
        sim.gps.orientation = 90.0
        sim.gps.mag_heading = 105.33
        sim.gps.date_time = datetime.now(TZ_LOCAL)  # PC current time, local time zone
        sim.gps.hdop = 3.1
        sim.gps.vdop = 5.0
        sim.gps.pdop = (sim.gps.hdop ** 2 + sim.gps.vdop ** 2) ** 0.5
        # Precision decimal points for various measurements
        sim.gps.horizontal_dp = 4
        sim.gps.vertical_dp = 1
        sim.gps.speed_dp = 1
        sim.gps.time_dp = 2
        sim.gps.angle_dp = 1
        # Heading variation affects the lat/lon, but not the compass heading
        sim.heading_variation = 10

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:

        while True:
            gga_str, hdm_str, hdt_str = list(sim.get_output(1))
            pashr1_str = '$PASHR,163029.000,158.09,T,-0.30,+0.31,+0.01,0.029,0.029,0.059,1,1*3B'
            pashr2_str = '$PASHR,130533.620,0.311,T,-80.467,-1.395,0.25,0.066,0.067,0.215,2,3*12'
            print(f'Sending "{gga_str}", "{hdm_str}", "{hdt_str}", "{pashr1_str}", "{pashr2_str}"')
            packet = sentences_to_packet([gga_str, hdm_str, hdt_str, pashr1_str, pashr2_str])
            sock.sendto(packet, (args.ip, args.port))
            time.sleep(1)

    except KeyboardInterrupt:
        print('Ctrl-C detected, stopping')


if __name__ == '__main__':
    main()