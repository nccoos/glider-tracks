# glider-tracks
This README documents how the whole Glider Map API works on the IMS Dockserver so you can understand where to install the code to get it running on your own web server.  There are two parts.  One is the generation of kml from glider logs and waypoint files.  Second is the custom Google Map API code under an Apache webserver and access to files it needs.  

The crontab on the IMS Dockserver sequences getting necessary data files (logs and waypoint files) and then running code to generate the kml output. 

```
[localuser@ims-dockserver ~]$ crontab -l
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin:/home/localuser/bin:/home/localuser/gliderbin
MAILTO=''
HOME=/home/localuser
#
# sync all realtime data from skio dockserver
00,10,20,30,40,50 * * * * /home/localuser/software/run_rsync2skio.sh
# 
# 
# Run pytrack_kml
01,11,21,31,41,51 * * * * /usr/bin/python /home/localuser/software/pytrack_kml.py ramses 
01,11,21,31,41,51 * * * * /usr/bin/python /home/localuser/software/pytrack_kml.py modena
01,11,21,31,41,51 * * * * /usr/bin/python /home/localuser/software/pytrack_kml.py salacia
#
# Run pywaypt_kml
01,11,21,31,41,51 * * * * /usr/bin/python /home/localuser/software/pywaypt_kml.py ramses 
01,11,21,31,41,51 * * * * /usr/bin/python /home/localuser/software/pywaypt_kml.py modena
01,11,21,31,41,51 * * * * /usr/bin/python /home/localuser/software/pywaypt_kml.py salacia
```

Since the IMS Dockserver is a backup to the one at SKIO, it grabs the data from SKIO dockserver and populates /home/localuser/realtime/{glider}/logs using the "run_rsync2skio.sh" script.   It also syncs other glider data such as tbd and sbd files.   

###	1. Generate kml files

The main programs pytrack_kml.py and pywaypt_kml.py are the entry points for reading, parsing input files and generating the kml output for a specified glider. The pyglider module (pyglider.py) contains the customized functions that do all the heavy lifting.  It uses pykml.factory KML_ElementMaker to build the objects that can then be serialized into an KML (Keyhole Markup Language) which is just an XML document designed for organizing map objects.  

The KML_ElementMaker might be tricky to run under Python3.  The code running here runs under Python2 (2.5.4).  It may be necessary to setup virtualenv and install older python under that virtualenv to run pykml.factory if porting to a newer machine.  Not sure what highest version python this will run under so some testing will be necessary.

Python Code (pytrack_kml.py and pywaypt_kml.py):
```
Input files: /home/localuser/realtime/{glider}/logs
Output kml: /home/localuser/realtime/tracks/
  {glider}_track.kml
  {glider}_waypoint.kml
```
The kml output files can be linked or loaded directly into Google Earth to display. However, Google Earth is bit cumbersome so we developed a light-weight Google Map API called Glider Map API.  

### 2. Glider Map API Setup

The Glider Map API uses the Google Map Javascript API (V3). It dynamically displays glider positions on a familiar map interface.  It augments the experience by visualizing each glider's current surface location relative to its past positions creating a track as the mission proceeds.  Detailed information from each surface report can be displayed providing vital glider health information by clicking or hovering over the position icons.  The Glider Map API is also built for responsive web design (RWD) so it can be utilized on phones, tablets and regular computer screens. 

Each kml file is loaded and converted to GeoJson using jquery.js and togeojson.js for display in its own layer on the map.  This allows the user to turn on and off each glider layer.   layerkml() was not used because it does not support some essential kml elements.  While converting to geojson is a performance hit,  its flexibility and functionality under Google Map API without re-inventing the pyglider was an important decision.  As more glider layers are added, and hence converting more kml to geojson, the performance may become more of an issue.  

Google Maps Javascript API Code and RWD:
```
Code files: /home/localuser/realtime/tracks
 html/
   index.html
   jquery.js
   togeojson.js
   styles.css
   styles_rwd.css
Input Files: /home/localuser/realtime/tracks/
  {glider}_track.kml
  {glider}_waypoint.kml
Icon Files: /home/localuser/realtime/tracks/
  icons/*.png
```

An important element to how the API functions is where to find the kml files and icons it needs under the Apache webserver configuration.  Coded within the API are specific http addresses to the setup on IMS Dockserver.  Configure the "realtime" directory under Apache so that the API has it is own address and it can find the necessary input files.  

The main landing page for this machine (http://imsdockserver.dyndns.org) is /var/www/html defined by  the default configuration (see /etc/httpd/conf/httpd.conf).

To add "realtime" to the document root which points to /home/localuser/realtime/, the following conf needs to be added to the default script or placed in its own conf.d script (e.g. /etc/httpd/conf.d/realtime.conf).  Now the Glider Map API can be accessed by the link http://imsdockserver.dyndns.org/realtime/tracks/html/

```
[localuser@ims-v118-dhcp00051 html]$ more /etc/httpd/conf.d/realtime.conf 
#
# This configuration file allows acces to 
# http://localhost/realtime
#
Alias /realtime /home/localuser/realtime

<Directory "/home/localuser/realtime">
    Options Indexes
    AllowOverride None
    Order allow,deny
    Allow from all
</Directory>
```
