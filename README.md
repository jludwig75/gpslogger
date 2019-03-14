# gpslogger

Raspberry Pi GPS Device Logger

![alt text](https://github.com/jludwig75/gpslogger/blob/master/20190314_124921.jpg)

gpslogger.py: Captures serial output and PPS interrupts and writes the output to a log file with microsecond timing

extract-nmea.py: Extracts and NMEA log file form a gpslogger log file.

An NMEA log can be converted to a GPX file with gpsbabel with this command:

gpsbabel -i nmea -f gps_nmea.log -x discard,hdop=10 -o gpx -F gps_track.gpx

I implemented this to work with a Raspberry Pi Zero W.

Setup:
1. Use raspi-config to disable the console on the serial port and enable the pins as a serial port
2. Shutdown Pi
3. Connect GPS TX to Pi RX
4. Connect GPS RX to Pi TX
5. Connect GPS VIN to 3.3V
6. Connect GPS ground to Pi ground
7. Connect GPS PPS pin to Pi pin 17
8. clone sketch to Pi in /home/pi
9. Run ./gpslogger.py to collect trace data
10. Press ctrl-c to stop trace collection

![alt text](https://github.com/jludwig75/gpslogger/blob/master/20190314_124840.jpg)
![alt text](https://github.com/jludwig75/gpslogger/blob/master/20190314_124631.jpg)

The log file has milisecond time stamps with PPS pules traces. To extract an NMEA log, run:

./extract-nmea.py -g gps_nmea_pps.log -n gps_nmea.log

You can convert the NMEA log to a GPX file with this gpsbabel command:

gpsbabel -i nmea -f gps_nmea.log -x discard,hdop=10 -o gpx -F gps_track.gpx

the hdop=10 option filters out poor GPS data.

TODO: Add script and instructions to setup as a service that starts at boot.
