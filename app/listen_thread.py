import socket
import threading

from loguru import logger


class ListenThread(threading.Thread):
    """
    Listen to a UDP port and send packets to topside_position.
    """

    def __init__(self, ip: str, port: int, topside_position):
        threading.Thread.__init__(self)

        self.ip = ip
        self.port = port
        self.topside_position = topside_position

        self.lock = threading.Lock()
        self.stopping = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        # Set timeout, this makes it easy to handle Ctrl-C
        self.sock.settimeout(0.1)

        # Bind to ip:port
        logger.info(f'Listening for NMEA messages on {self.ip}:{self.port}')
        self.sock.bind((self.ip, self.port))

        while True:
            try:
                packet, _ = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
                self.topside_position.recv_packet(packet)

            except socket.timeout:
                continue

            except socket.error:
                break

    def stop(self):
        with self.lock:
            self.stopping = True

            # Close socket, this will raise an exception in the run loop
            self.sock.close()
