# gpslogger

Raspberry Pi GPS Device Logger

gpslogger.py: Captures serial output and PPS interrupts and writes the output to a log file with microsecond timing

extract-nmea.py: Extracts and NMEA log file form a gpslogger log file.

An NMEA log can be converted to a GPX file with gpsbabel with this command:

gpsbabel -i nmea -f gps_nmea.log -x discard,hdop=10 -o gpx -F gps_track.gpx

I implemented this to work with a Raspberry Pi Zero W.

Setup:
1. Use raspi-config to disable the console on the serial port and enable the pins as a serial port
2. Connect GPS TX to Pi RX
3. Connect GPS RX to Pi TX
4. Connect GPS VIN to 3.3V
5. Connect GPS ground to Pi ground
6. Connect GPS PPS pin to Pi pin 17
7. clone sketch to Pi in /home/pi
8. Run ./gpslogger.py to collect trace data
9. Press ctrl-c to stop trace collection

The log file has milisecond time stamps with PPS pules traces. To extract an NMEA log, run:

./extract-nmea.py -g gps_nmea_pps.log -n gps_nmea.log

You can convert the NMEA log to a GPX file with this gpsbabel command:

gpsbabel -i nmea -f gps_nmea.log -x discard,hdop=10 -o gpx -F gps_track.gpx

the hdop=10 option filters out poor GPS data.

TODO: Add script and instructions to setup as a service that starts at boot.
