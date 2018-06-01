""" pytrack_kml.py Generate kml for each glider using pykml from localuser/realtime/{glidername}/logs

    Usage: python pytrack_kml.py glidername

    Inputs:
     glidername [ramses | pelagia | modena | salacia]

     Input path for logs:
     /home/localuser/realtime/{glidername}/logs
     (NOTE:  these logs are copied or rsync'd from active dockserver)

     Output path for kml:
     /home/localuser/realtime/tracks/{glidername}_track.kml
     

"""
import os.path
import sys
import pyglider
import glob
                                                                
if __name__ == '__main__':
    glider = sys.argv[1]
    # fn = '/var/spool/mail/localuser'
    indir = '/home/localuser/realtime/'+glider+'/logs'
    try:
        # lines = pyglider.load_data(fn)
        lines = pyglider.load_glider_logs(indir, glider)
        data1 = pyglider.parse_glider_logs(lines, glider)
        kml = pyglider.generate_track_kml(data1, glider)
        ofn = '/home/localuser/realtime/tracks/'+glider+'_track.kml'
        f = open(ofn, 'w')
        f.write(kml)
        f.close()

        debug = 0
        if debug:
            for d in data1:
		print "something"
		coord_str = "";
        	if d['lat'] and d['lon']:
          		coord_str = coord_str + "%f,%f" % (d['lon'], d['lat'])
		print d['dt_str'],d['gps_dt_str'],coord_str
               

    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

                                    
