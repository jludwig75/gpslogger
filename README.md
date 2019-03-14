# gpslogger

Raspberry Pi GPS Device Logger

gpslogger.py: Captures serial output and PPS interrupts and writes the output to a log file with microsecond timing

extract-nmea.py: Extracts and NMEA log file form a gpslogger log file.

An NMEA log can be converted to a GPX file with gpsbabel with this command:

gpsbabel -i nmea -f gps_nmea.log -x discard,hdop=10 -o gpx -F gps_track.gpx
