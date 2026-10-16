import socket
import threading

import pynmea2
from loguru import logger

import nmea_sentences
import util
from data_logger import DataLogger, LoggingConfig
from topside_position import TopsidePosition


class ListenThread(threading.Thread):
    """
    Listen to a UDP port and send packets to topside_position.
    """

    def __init__(self, ip: str, port: int, topside_position, log_nmea: bool, config: LoggingConfig):
        super().__init__()
        self.ip = ip
        self.port = port
        self.topside_position = topside_position
        self.nmea_messages_received = []

        # Create a socket, but do not bind to a port quite yet
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if log_nmea:
            self.gga_logger = DataLogger(config.path_prefix + 'nmea_GGA.csv', nmea_sentences.GGA.fieldnames())
            self.hdt_logger = DataLogger(config.path_prefix + 'nmea_HDT.csv', nmea_sentences.HDT.fieldnames())
            self.pashr_logger = DataLogger(config.path_prefix + 'nmea_PASHR.csv', nmea_sentences.PASHR.fieldnames())
            self.messages_logged = False
        else:
            self.gga_logger = None
            self.hdt_logger = None
            self.pashr_logger = None

    def run(self):
        # Set a timeout, this makes it easy to handle Ctrl-C
        self.sock.settimeout(0.1)

        # Bind to ip:port and listen
        logger.info(f'Listening for NMEA messages on {self.ip}:{self.port}')
        self.sock.bind((self.ip, self.port))

        while True:
            try:
                packet, _ = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
                self.recv_packet(packet)

            except socket.timeout:
                continue

            except socket.error:
                break

            except Exception as e:
                logger.error(f'Unexpected error in listen thread: {e}')

    def recv_packet(self, packet):
        """
        Packet format is:
        <sentence><cr><lf><sentence><cr><lf><sentence><cr><lf>...
        """
        try:
            decoded = packet.decode()
        except UnicodeDecodeError as e:
            logger.warning(f'Could not decode NMEA packet: {e}')
            return

        sentence_strs = decoded.split('\r\n')
        for sentence_str in sentence_strs:
            if sentence_str == '':
                continue

            try:
                sentence = pynmea2.parse(sentence_str)
            except Exception as e:
                logger.warning(f'Could not parse NMEA sentence "{sentence_str}": {e}')
                continue

            try:
                if hasattr(sentence, 'sentence_type'):
                    # This is a standard message
                    if sentence.sentence_type not in self.nmea_messages_received:
                        self.nmea_messages_received.append(sentence.sentence_type)
                        logger.info(f'Receiving {sentence.sentence_type} messages')

                    if sentence.sentence_type == 'GGA':
                        self.recv_gga(sentence)
                    elif sentence.sentence_type == 'HDT':
                        self.recv_hdt(sentence)

                elif hasattr(sentence, 'manufacturer'):
                    # This is a proprietary message
                    if sentence.manufacturer not in self.nmea_messages_received:
                        self.nmea_messages_received.append(sentence.manufacturer)
                        logger.info(f'Receiving {sentence.manufacturer} messages (proprietary)')

                    if sentence.manufacturer == 'ASH' and getattr(sentence, 'data', None) and sentence.data[0] == 'R':
                        self.recv_pashr(sentence)
            except Exception as e:
                logger.warning(f'Error processing NMEA sentence "{sentence_str}": {e}')

    def recv_gga(self, sentence):
        gga = nmea_sentences.GGA.from_sentence(sentence)
        if gga is None:
            logger.warning(f'Bad GGA: {sentence}')
            return

        self.topside_position.put_gga(gga)
        if self.gga_logger is not None:
            self.gga_logger.log(gga.as_dict())
            self.messages_logged = True

    # Hmmm... we could get the heading from PASHR, and stop listening to HDT
    def recv_hdt(self, sentence):
        hdt = nmea_sentences.HDT.from_sentence(sentence)
        if hdt is None:
            logger.warning(f'Bad HDT: {sentence}')
            return

        self.topside_position.put_hdt(hdt)
        if self.hdt_logger is not None:
            self.hdt_logger.log(hdt.as_dict())
            self.messages_logged = True

    def recv_pashr(self, sentence):
        if self.pashr_logger is not None:
            pashr = nmea_sentences.PASHR.from_sentence(sentence)
            if pashr is None:
                logger.warning(f'Bad PASHR: {sentence}')
                return

            self.pashr_logger.log(pashr.as_dict())

    def stop(self):
        # Close socket, this will raise an exception in the run loop
        self.sock.close()

    def logging_status(self) -> str:
        if self.gga_logger is None:
            return 'disabled'
        elif self.messages_logged:
            return 'logging'
        else:
            return 'waiting'


# For testing
if __name__ == '__main__':
    util.test_main(ListenThread('127.0.0.1', 10110, TopsidePosition(), True, LoggingConfig(local_test=True)))
