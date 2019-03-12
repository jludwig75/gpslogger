import argparse
import serial
import RPi.GPIO as GPIO  
import wiringpi
import Queue
import threading
import time
import signal
import sys


BITS_PER_BYTE = 10
MSEC_PER_SEC = 1000
USEC_PER_SEC = MSEC_PER_SEC * 1000


class DebugClass:
    def __init__(self, enable_debug):
        self.enable_debug = enable_debug

    def print_debug(self, msg):
        if self.enable_debug:
            print msg


class GpsLogWritter(DebugClass):
    def __init__(self, event_queue, log_file_name, print_to_screen, debug):
        DebugClass.__init__(self, debug)
        self.event_queue = event_queue
        self.stop_thread = False
        self.log_file_name = log_file_name
        self.print_to_screen = print_to_screen
    
    def _write_log_file(self):
        with open(self.log_file_name, 'a') as log_file:
            while not self.stop_thread:
                while not self.event_queue.empty():
                    msg = self.event_queue.get()
                    if self.print_to_screen:
                        print msg
                    log_file.write(msg + '\n')
            self.print_debug('Exiting GPS log writer thread')
    
    def start(self):
        self.print_debug('Starting GPS log writer thread')
        self.stop_thread = False
        self.thread = threading.Thread(target = self._write_log_file)
        self.thread.start()
    
    def stop(self):
        self.print_debug('Telling GPS log writer thread to stop')
        self.stop_thread = True
        self.print_debug('Waiting for log writer thread to stop...')
        self.thread.join()


class SerialPortListener(DebugClass):
    def __init__(self, event_queue, port_name, baud_rate, debug):
        DebugClass.__init__(self, debug)
        self.port_name = port_name
        self.q = event_queue
        self.baud_rate = baud_rate
        self.usec_per_bit = USEC_PER_SEC / (baud_rate / BITS_PER_BYTE)
        self.stop_thread = False

    def _run(self):
        with serial.Serial(self.port_name, self.baud_rate) as ser:
            while not self.stop_thread and ser:
                line = ser.readline()[:-1].strip()
                time_received = wiringpi.micros()
                bytes_received = len(line) + 1
                bits_received = bytes_received * BITS_PER_BYTE
                # This is at least how much time it took to reveive the string
                us_to_receive = bits_received * self.usec_per_bit
                self.q.put('%s-%s: %s' % (str(time_received - us_to_receive), str(time_received), line))
            self.print_debug('Exiting serial port listener thread')
    
    def start(self):
        self.print_debug('Starting serial port listener thread')
        self.stop_thread = False
        self.thread = threading.Thread(target = self._run)
        self.thread.start()

    def stop(self):
        self.print_debug('Telling serial port listener thread to stop')
        self.stop_thread = True
        self.print_debug('Waiting for serial port listener thread to stop...')
        self.thread.join()

class PpsPinListener(DebugClass):
    def __init__(self, event_queue, pps_pin, debug):
        DebugClass.__init__(self, debug)
        self.pps_pin = pps_pin
        self.event_queue = event_queue
        GPIO.setmode(GPIO.BCM)  
        GPIO.setup(self.pps_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def _pps_callback(self, channel):
        self.event_queue.put('%s: PPS' % str(wiringpi.micros()))

    def start(self):
        self.print_debug('Enabling PPS listener')
        GPIO.add_event_detect(self.pps_pin, GPIO.RISING, callback=self._pps_callback, bouncetime=300)

    def stop(self):
        self.print_debug('Disabling PPS listener')
        GPIO.remove_event_detect(self.pps_pin)

class GpsLogger(DebugClass):
    def __init__(self, port_name, baud_rate, pps_pin, log_file_name, print_to_screen, debug):
        DebugClass.__init__(self, debug)
        self.event_queue = Queue.Queue()
        self.log_writer = GpsLogWritter(self.event_queue, log_file_name, print_to_screen, debug)
        self.serial_port_listener = SerialPortListener(self.event_queue, port_name, baud_rate, debug)
        self.pps_listener = PpsPinListener(self.event_queue, pps_pin, debug)

    def start(self):
        wiringpi.wiringPiSetup()

        self.print_debug('Starting log writer')
        self.log_writer.start()

        self.print_debug('Starting serial port listener')
        self.serial_port_listener.start()

        self.print_debug('Starting PPS listener')
        self.pps_listener.start()

    def stop(self):
        self.print_debug('Stopping PPS listener...')
        self.pps_listener.stop()

        self.print_debug('Stopping serial port listener...')
        self.serial_port_listener.stop()

        self.print_debug('Stopping GPS log writter...')
        self.log_writer.stop()

parser = argparse.ArgumentParser(description='Capture a log of NMEA sentences and PPS pulses')
parser.add_argument('-P', '--port', type=str, default='/dev/ttyS0')
parser.add_argument('-l', '--log-file', type=str, default='gps_nmea_pps.log')
parser.add_argument('-b', '--baud-rate', type=int, default=9600)
parser.add_argument('-p', '--pps-pin', type=int, default=17)
parser.add_argument('-s', '--screen', action='store_true', default=False)
parser.add_argument('-d', '--debug', action='store_true', default=False)

args = parser.parse_args()

def sigint_handler(signum, frame):
    global logger
    print 'Ctr-C detected. Stopping logger...'
    logger.stop()
    sys.exit(0)

logger = GpsLogger(args.port, args.baud_rate, args.pps_pin, args.log_file, args.screen, args.debug)

signal.signal(signal.SIGINT, sigint_handler)

logger.start()
while True:
    time.sleep(0.01)
