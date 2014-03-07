sunlight-rfid-doorman
=====================

This code secures Sunlight's office door with an RFID system built out of an Arduino, Raspberry Pi and a 13.56 GHz RFID reader component. 

Installation
------------
1. Program the Arduino with the included .ino file
2. Flash a stock Raspbian image to an SD card
3. Clone [this repository](https://github.com/sbma44/rpi) and run `sudo bootstraph.sh`
4. Use virtualenv's `mkproject` to create a viable clone of this repo.
5. `pip install -r requirements.txt`
6. Customize config files; hook doorman.py's allow() routine to code that actually opens the door!
7. `sudo apt-get install redis-server`
8. Copy sunlight_rfid_doorman.conf to /etc/supervisor/conf.d/ and customize as appropriate.
9. sudo service supervisor stop && sudo service supervisor start

Hardware Setup
--------------
Raspberry Pis and Arduinos are easy to find. The RFID component is based on a  ~$10 breakout, like the one found at this link. Compatible key fobs can be found easily on eBay, too (search for 13.56 and "MiFare").

http://www.ebay.com/itm/13-56MHz-14443A-MIFARE-RC522-RF-RFID-Writer-Reader-IC-Card-with-S50-for-Arduino-/200944960003?pt=LH_DefaultDomain_0&hash=item2ec940c203

Its pin mappings are based on an Arduino Uno and [this post](http://www.grantgibson.co.uk/2012/04/how-to-get-started-with-the-mifare-mf522-an-and-arduino/):

* Reset > Pin 5
* SS > Pin 10
* MOSI > Pin 11
* MISO > Pin 12
* SCK > Pin 13
* Ground > Ground
* 3.3v > 3.3v

Additionally, the code expects a common anode RGB status LED with the R, G, and B channels connected to pins 3, 6 and 9, respectively. Sorry, no PCB layout files -- I just used perfboard. This could easily be implemented with multiple LEDs, or omitted entirely.

Access Control & Logging
------------------------
Access is controlled and logged in a Google spreadsheet like the one found here:

https://docs.google.com/spreadsheet/ccc?key=0Ao2x9OwoRgcCdE9icnBad2FESkZCSFNDdWdPYWNHTGc&usp=sharing

The access control list is refreshed in three ways:

1. At boot
2. Every five minutes
3. The first time an unrecognized RFID fob is seen. To avoid hammering the Google Drive API, subsequent scans of that fob will *not* force a refresh until a valid fob has been scanned.

Logs are stored in memory and dumped to monthly worksheets in the same spreadsheet every five minutes.

Wait, How Does This Unlock Anything?
------------------------------------
The unlocking is achieved by firing off a command via SSH on a remote server. We already built something to handle this:

https://sunlightfoundation.com/blog/2010/02/16/our-door-opener-science-project/

In truth, this system doesn't use RFIDs to open a door: it uses RFIDs to fire off a command via SSH on a remove system. Sorry, I know it's kind of a letdown. Making your door open electronically is a whole other issue, though if you have a system installed (by a security professional!), connecting a relay circuit to a Raspberry Pi is pretty easy. The [PiFace](http://www.piface.org.uk/) is a good place to start. 





