""" pywaypt_kml.py Generate kml for each glider using pykml from localuser/realtime/{glidername}/logs

    Usage: python pywaypt_kml.py glidername

    Inputs:
     glidername [ramses | pelagia | modena | salacia]

     Input path for mission files:
     /home/localuser/realtime/{glidername}/goto
     (NOTE:  these MA-files are copied or rsync'd from active dockserver)

     Output path for kml:
     /home/localuser/realtime/tracks/{glidername}_waypoint.kml
     

"""
import os.path
import sys
import pyglider
import glob
                                                                
if __name__ == '__main__':
    glider = sys.argv[1]
    indir = '/home/localuser/realtime/'+glider+'/goto'
    try:
        fns = glob.glob(indir + '/*goto*.ma')
        fns.sort()
        fn = fns[-1]

        #
        print fn        
        lines = pyglider.load_data(fn)
        data2 = pyglider.parse_glider_goto_ma(lines, glider, os.path.split(fn)[1])
        
        kml = pyglider.generate_waypoint_kml(data2, glider)
        ofn = '/home/localuser/realtime/tracks/'+glider+'_waypoint.kml'
        f = open(ofn, 'w')
        f.write(kml)
        f.close() 

	#           for d in data1:
	# 		print "something"
	# 		print d['dt_str'],d['gps_dt_str']
	# 		coord_str = "";
	#         	if d['lat'] and d['lon']:
	#           		coord_str = coord_str + "%f,%f" % (d['lon'], d['lat'])
	# 		print d['dt_str'],d['gps_dt_str'],coord_str
	#                

    except:
        pass
                                    
