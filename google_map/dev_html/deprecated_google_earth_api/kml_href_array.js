//<!--

var kmlUrl = 'http://dockserver.marine.unc.edu/realtime/tracks/';

// store the object loaded for the given name ... initially none of the objects
// are loaded, so initialize these to null
var currentKmlObjects = {
	'ramses': null,
	'pelagia': null,
	'hfrhr': null,
	'hfr25hr': null,
	'ndbc': null,
	'moorings': null
};

//KML ARRAY (based on array example at http://www.cec.org/atlas/ge/)
// 0: layer name (text) matches currentKmlObjects
// 1: url (text)	
var kmlArray = {
	'ramses': Array('ramses', kmlUrl+'ramses_track.kml'),
	'ramses_goto': Array('ramses_goto', kmlUrl+'ramses_waypoint.kml'),
	'pelagia': Array('pelagia', kmlUrl+'pelagia_track.kml'),
	'pelagia_goto': Array('pelagia_goto', kmlUrl+'pelagia_waypoint.kml'),
	'hfrhr': Array('hfrhr', 'http://hfrnet.ucsd.edu/rtv/networkKml.php?res=6km&pfx=h&rng=0,50&bbox=34,34,-82,-82'),
	'hfr25hr': Array('hfr25hr', 'http://hfrnet.ucsd.edu/rtv/networkKml.php?res=6km&pfx=a&rng=0,50&bbox=34,34,-82,-82'),
	'ndbc': Array('ndbc', 'http://www.ndbc.noaa.gov/kml/marineobs_by_pgm.kml'),
	'moorings': Array('moorings', kmlUrl+'moorings.kml')
};
	
//-->