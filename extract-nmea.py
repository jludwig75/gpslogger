#!/usr/bin/env python

"""
After extracting an NMEA log fie, use this command to create a GPX file:

gpsbabel -i nmea -f gps_nmea.log -x discard,hdop=10 -o gpx -F gps_track.gpx
"""

import argparse
import sys

def extract_nmealog(gpslogger_file_name, nmea_file_name):
    if gpslogger_file_name == nmea_file_name:
        print 'Error: Input and output file names match!'
        return -1
    with open(gpslogger_file_name, 'r') as gps_file:
        with open(nmea_file_name, 'w') as nmea_file:
            for line in gps_file:
                parts = line.split(': ')
                if len(parts) != 2:
                    continue
                trace_data = parts[1]
                if trace_data.startswith('$GP'):
                    nmea_file.write(trace_data)
    return 0

parser = argparse.ArgumentParser(description='Extract an NMEA log file from a gpslogger log file')
parser.add_argument('-g', '--gpslogger-file', type=str, required=True)
parser.add_argument('-n', '--nmea-file', type=str, required=True)

args = parser.parse_args()

sys.exit(extract_nmealog(args.gpslogger_file, args.nmea_file))