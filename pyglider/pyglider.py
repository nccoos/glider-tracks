"""pyglider.py A module of utilities to run on dockserver for glider operations

   parse_glider_mail
   parse_glider_logs
   generate_track_kml

   parse_glider_goto_ma
   generate_waypoint_kml
   
"""

REAL_RE_STR = '\\s*(-?\\d(\\.\\d+|)[Ee][+\\-]\\d\\d?|-?(\\d+\\.\\d*|\\d*\\.\\d+)|-?\\d+)\\s*'

import sys
import os
import re
import glob

import time
import datetime

def load_data(inFile):
    lines=None
    if os.path.exists(inFile):
        f = open(inFile, 'r')
        lines = f.readlines()
        f.close()
        if len(lines)<=0:
            print 'Empty file: '+ inFile
    else:
        print 'File does not exist: '+ inFile
    return lines

def display_time_diff(diff):
    """Display time difference in HH:MM and days (D) if necessary"""
    days = diff.days
    minutes, seconds = divmod(diff.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if (days<=1):
        if minutes<1:
            str = "%02:%02d:%02d" % (hours, minutes,seconds)
        else:
            str = "%02d:%02d" % (hours, minutes)
    elif (days>1):
        str = "%d Days %02d:%02d" % (days, hours, minutes)
    else:
        str = "%02d:%02d" % (hours, minutes)
    return str
                                                                    
def dt2es(dt):
    """Convert datetime object to epoch seconds (es) as seconds since Jan-01-1970 """
    # microseconds of timedelta object not used
    delta = dt - datetime.datetime(1970,1,1,0,0,0)
    es = delta.days*24*60*60 + delta.seconds
    return es

def es2dt(es):
    """ Convert epoch seconds (es) to datetime object"""
    dt = datetime.datetime(*time.gmtime(es)[0:6])
    return dt


def load_glider_logs(indir, glider):
    """ read all logs for glider """
    fns = glob.glob(indir+'/'+glider+'*.log')
    # logs should have filename with timestamp so can sort from youngest to oldest
    fns.sort()
    
    # Only process last 30 days of available logs
    m = re.search(r'^(.*)_(\d*T\d*)\.log', fns[-1])
    if m:
        t = time.strptime(m.group(2), "%Y%m%dT%H%M%S")
        lastdt = datetime.datetime(*t[0:6])
    
    newfns = []
    for fn in fns:
        m = re.search(r'^(.*)_(\d*T\d*)\.log', fn)
        if m:
            t = time.strptime(m.group(2), "%Y%m%dT%H%M%S")
            # the '*' operator unpacks the tuple, producing the argument list.
            dt = datetime.datetime(*t[0:6])
            diff = lastdt - dt
            if (diff.days)<31:
                # append: add arg as single element to end of list, increase len by 1
                newfns.append(fn)
    
    fns = newfns
    lines = []
    for fn in fns:
        ll = load_data(fn)
        # look for "Connection Event" 
        m = re.search(r'Connection Event', ''.join(ll))
        # extend: iterate over all elements of arg, len of list increases by num of elements in arg
        if m: 
            lines.extend(ll)
        else:
            lines.extend(['Connection Event:',])
            lines.extend(ll)
    
    return lines

def parse_glider_logs(lines, glider):
    # msg_split_patt = r'From root\@dockserver'
    msg_split_patt = r'Connection Event:'
    msgs = re.split(msg_split_patt, ''.join(lines))
    
    gms = []
    # select messages for specific glider based on "Subject:" line
    for msg in msgs:
       m = re.search(r'^(Vehicle Name:)\s+(\w*)', msg, re.MULTILINE)
       if m:
           glidername = m.group(2)
           if glidername == glider:
               gms.append(msg)

    data = []
    for msg in gms:
        #         m = re.search(r'^Subject: Glider: (\w*).*$', msg, re.MULTILINE)
        #         if m:
        #             subject_string = m.group(0)
        #             subject_glider = m.group(1)
        #             # print subject_string
        #         else:
        #             continue

        m = re.search(r'(Event)*: (.*?)\.\s.*$', msg, re.MULTILINE)
        if m:
            event = m.group(2)
        else:
            event = None

        #         m = re.search(r'\s*(Reason)*:\s*(.*)$', subject_string, re.MULTILINE)
        #         if m:
        #             subject_reason = m.group(2)
        #         else:
        #             subject_reason = None

        m = re.search(r'^(Vehicle Name:)\s+(\w*)', msg, re.MULTILINE)
        if m: glidername = m.group(2)
        else: glidername = None
        
        m = re.search(r'^(Curr Time:)\s+(.*)\s+MT:', msg, re.MULTILINE)
        if m:
            try:
                t = time.strptime(m.group(2), "%a %b %d %H:%M:%S %Y")
                # the '*' operator unpacks the tuple, producing the argument list.
                dt = datetime.datetime(*t[0:6])
                diff = datetime.datetime.utcnow() - dt
                hours_ago = display_time_diff(diff)
                dt_str = datetime.date.strftime(dt, "%Y-%m-%d %H:%M:%S UTC")
                if (diff.days)>0:
                     # dt_str_short = datetime.date.strftime(dt, "%b-%d")
                     dt_str_short = ""                     
                if (diff.days) <= 0:
                    dt_str_short = datetime.date.strftime(dt, "%H:%M")
            except ValueError, e:
                dt_str = None
                dt_str_short = None
                hours_ago = None

        m = re.search(r'^(GPS Location:)\s+(-?\d{2})(\d{2}\.\d+)\s+([NnSs])'+ \
                      r'\s+(-?\d{2})(\d{2}\.\d+)\s+([EeWw]).*$', msg, re.MULTILINE)
        if m:
            #
            lat_deg = float(m.group(2))
            lat_min = float(m.group(3))
            lat_hem = m.group(4).upper()
            #
            lon_deg = float(m.group(5))
            lon_min = float(m.group(6))
            lon_hem = m.group(7).upper()
            if lat_deg<0:
                lat = lat_deg - lat_min/60.
            else:
                lat = lat_deg + lat_min/60.
            if lon_deg<0:
                lon = lon_deg - lon_min/60.
            else:
                lon = lon_deg + lon_min/60.
            gps_str = m.group(0)
            m = re.search(r'GPS Location: (.*) measured', gps_str)
            if m: gps_posn_str = m.group(1)
            else: gps_posn_str = None
            m = re.search(r'measured\s*(\d*)\.\d* secs ago', gps_str)
            if m:
                gps_secs_ago = int(m.group(1))
                gps_dt = dt - datetime.timedelta(0,gps_secs_ago,0)
                gps_dt_str = datetime.date.strftime(gps_dt, "%Y-%m-%d %H:%M:%S UTC")
            else: gps_dt_str = None
        else:
            lat = None
            lon = None

        m = re.search(r'(MT:)\s+(.*)$', msg, re.MULTILINE)
        if m: mt = m.group(2)
        else: mt = None

        m = re.search(r'(sensor:m_battery.*?=)\s*(-?\d+\.\d*)', msg, re.MULTILINE)
        if m: batt = float(m.group(2))
        else: batt = None

        m = re.search(r'(sensor:m_leakdetect.*?=)\s*(-?\d+\.\d*)', msg, re.MULTILINE)
        if m: leak = float(m.group(2))
        else: leak = None

        m = re.search(r'(sensor:m_vacuum.*?=)\s*(-?\d+\.\d*)', msg, re.MULTILINE)
        if m: vacuum = float(m.group(2))
        else: vacuum = None
        
        m = re.search(r'^(Because:)\s*(.*)', msg, re.MULTILINE)
        if m: because = m.group(2)
        else:  because = 'Unknown'

        m = re.search(r'^(MissionName:)\s*(.*?)\s+', msg, re.MULTILINE)
        if m: mission_name = m.group(2)
        else: mission_name = 'Unknown'

        m = re.search(r'\s+(MissionNum:)(.*)', msg, re.MULTILINE)
        if m: mission_num = m.group(2)
        else: mission_num = 'Unknown'

        m = re.search(r'^(Waypoint:)\s+(\(.*\)).*$', msg, re.MULTILINE)
        if m:
            wp_str = m.group(0)
            waypoint_posn = m.group(2)
        else:
            wp_str = None
            waypoint_posn = 'Unknown'
            waypoint_range = 'Unknown'
            waypoint_bearing = 'Unknown'
            waypoint_age = 'Unknown'
            wlat=None
            wlon=None

        if wp_str:
            # parse out the next waypoint for a place mark
            m = re.search(r'\((-?\d{2})(\d{2}\.\d+),(-?\d{2})(\d{2}\.\d+)\)', waypoint_posn)
            if m:
                #
                lat_deg = float(m.group(1))
                lat_min = float(m.group(2))
                #
                lon_deg = float(m.group(3))
                lon_min = float(m.group(4))
                if lat_deg<0:
                    wlat = lat_deg - lat_min/60.
                else:
                    wlat = lat_deg + lat_min/60.
                if lon_deg<0:
                    wlon = lon_deg - lon_min/60.
                else:
                    wlon = lon_deg + lon_min/60.
            else:
                wlat = None
                wlon = None
            m = re.search(r'(Range:)\s+(.*?),', wp_str)
            if m: waypoint_range = m.group(2)
            else: waypoint_range = 'Unknown'
            m = re.search(r'(Bearing:)\s+(.*?),', wp_str)
            if m: waypoint_bearing = m.group(2)
            else: waypoint_bearing = 'Unknown'
            m = re.search(r'(Age:)\s+(.*?)$', wp_str)
            if m: waypoint_age = m.group(2)
            else: waypoint_age = 'Unknown'

        if lat and lon:    
            # generate report table for google earth
            # using ![CDATA[ {html} ]] inside of KML description tag
            html_report = [
                ' ', 
                '<div id="main">',
                '<h3>Surface Report</h3>',
                '<table>',
                '<thead>',
                '<tr><th>Glider: %s</th><th>%s</th></tr>' % (glider, dt_str,),
                '</thead>',
                '<tbody>']        
            html_report.extend(
                [
                 '<tr><td>GPS Location:</td><td>%s</td></tr>' % (gps_posn_str,),
                 '<tr><td>GPS Time:</td><td>%s</td></tr>' % (gps_dt_str,)
                 ])
            html_report.extend(
                [
                 ##### '<tr><td>Surface Event:</td><td>%s</td></tr>' % (subject_event,),
                 ##### '<tr><td>Surface Reason:</td><td>%s</td></tr>' % (subject_reason,),
                 '<tr><td>Surface Because:</td><td>%s</td></tr>' % (because,),
                 ])
            html_report.extend(
                [
                '<tr><td>Mission Name:</td><td>%s</td></tr>' % (mission_name,),
                '<tr><td>Mission Number:</td><td>%s</td></tr>' % (mission_num,),
                '<tr><td>Mission Time:</td><td>%s</td></tr>' % (mt,)
                ])

            if batt:
                if batt < 10.:
                    html_report.append('<tr><td>Battery (volts):</td><td class="red_td">%g</td></tr>' % (batt,))
                elif (batt>=10) and (batt<11):
                    html_report.append('<tr><td>Battery (volts):</td><td class="yellow_td">%g</td></tr>' % (batt,))
                else:
                    html_report.append('<tr><td>Battery (volts):</td><td>%f</td></tr>' % (batt,))
            else:
                html_report.append('<tr><td>Battery (volts):</td><td>Unknown</td></tr>')

            if vacuum:
                if (vacuum>=10) or (vacuum<6):
                    html_report.append('<tr><td>Vacuum (inHg):</td><td class="yellow_td">%g</td></tr>' % (vacuum,))
                else:
                    html_report.append('<tr><td>Vacuum (inHg):</td><td>%g</td></tr>' % (vacuum,))
            else:
                html_report.append('<tr><td>Vacuum (inHg):</td><td>Unknown</td></tr>')
            # need tolerances for flagging leak detect in report
            if leak:
                html_report.append('<tr><td>Leak Detect (volts):</td><td>%f</td></tr>' % (leak,))
            else:
                html_report.append('<tr><td>Leak Detect (Volts):</td><td>Unknown</td></tr>')
            #
            html_report.extend(
                [
                '<tr><td>Waypoint:</td><td>%s</td></tr>' % (waypoint_posn,),
                '<tr><td>Waypoint Range:</td><td>%s</td></tr>' % (waypoint_range,),
                '<tr><td>Waypoint Bearing:</td><td>%s</td></tr>' % (waypoint_bearing,),
                '<tr><td>Waypoint Age:</td><td>%s</td></tr>' % (waypoint_age,)
                ])
            # close the report tbody table div and CDATA
            html_report.extend(
                ['</tbody>',
                 '</table>',
                 '</div>',
                 ' ' 
                 ])
            # make a readable CDATA string
            html_report_str = '\n'.join(html_report)
            # can create a KML object since extracted lat and lon
            data.append({'glider': glider,
                         'dt': dt,
                         'dt_str': dt_str,
                         'datetime': dt_str, 
                         'name': dt_str_short,
                         'hours_ago': hours_ago,
                         'gps_dt': gps_dt,
                         'gps_dt_str': gps_dt_str,
                         'lat': lat,
                         'lon': lon,
                         'description': html_report_str,
                         'wlat': wlat,
                         'wlon': wlon,
                         })
        else:
            # if no lat lon, can't create a KML object without lat and lon
            # but want to append info to last known surface report
            html_report = [
                '<h2></h2>',
                '<table">',
                '<thead>',
                '<tr><th>Glider: %s</th><th>ABORT Surfacing</th></tr>' % (glider,),
                '</thead>',
                '<tbody>']        
            html_report.extend(
                [
                 ##### '<tr><td>Surface Event:</td><td class="red_td">%s</td></tr>' % (subject_event,),
                 ##### '<tr><td>Surface Event:</td><td class="red_td">%s</td></tr>' % (subject_reason,),
                 '<tr><td>Surface Reason:</td><td class="red_td">%s</td></tr>' % (because,),
                 ])
            # close the report tbody table div and CDATA
            html_report.extend(
                ['</tbody>',
                '</table>',
                 ' '
                 ])
            
            if len(data)>1:
                # have to have a least one previous report 
                html_report_str = data[-1]['description']
                html_report_str = html_report_str + '\n'.join(html_report)
                # print html_report_str
                data[-1]['description'] = html_report_str
    # close for-loop of msg in gms:
    return data


def generate_track_kml(data, glider):
    """ Use pykml to generate kml file for each glider from parsed mail data
    A glider track consists of a line and placemarks for each surfacing
    
    Usage: kml_doc_str = generate_track_kml(data, glider)
    """

    from pykml.factory import KML_ElementMaker as KML
    import lxml.etree

    # ***** append LookAt after checking that lat, lon exist in data[-1]
    d = data[-1]
    # print '(%f, %f)' % (d['lon'], d['lat'])  
    
    # start a KML file skeleton with track styles
    doc = KML.kml(
        KML.Document(
            KML.Name(glider + "_track"),
            KML.LookAt(
                KML.longitude('%f' % d['lon']),
                KML.latitude('%f' % d['lat']),
                KML.heading('0'),
                KML.tilt('0'),
                KML.range('60000'),
                KML.altitudeMode('absolute')
                )
            )
        )
    
    doc.Document.append(
        KML.Style(
            KML.IconStyle(
                # KML.scale(0.7),
                KML.color("ff00ff00"),
                KML.Icon(KML.href("icons/grn-circle.png"))
                ),
            KML.LabelStyle(
                KML.color("ff00ff00"),
                KML.scale(0.8)),
            id="lastPosnIcon")
        )
    doc.Document.append(
        KML.Style(
            KML.IconStyle(
                KML.scale(0.5),
                KML.color("ff0000ff"),
                KML.Icon(KML.href("icons/grn-square-lv.png"))),
            KML.LabelStyle(
                KML.scale(0.8)),
            id="lastWayPosnIcon")
        )    
    doc.Document.append(
        KML.Style(
            KML.IconStyle(
                KML.scale(0.5),
                KML.color("7d00ffff"),
                KML.Icon(KML.href("icons/ylw-square-lv.png"))),
            KML.LabelStyle(
                KML.color("7d00ffff"),
                KML.scale(0.8)),
            id="prevPosnIcon")
        )    
    doc.Document.append(
        KML.Style(
            KML.IconStyle(
                KML.scale(0.9),
                KML.color("ff00ff00"),
                KML.Icon(KML.href("icons/donut.png"))),
            KML.LabelStyle(
                KML.color("ff00ff00"),
                KML.scale(0.7)),
            id="histPosnIcon")
        )    
    doc.Document.append(
        KML.Style(
            KML.LineStyle(
                KML.color("7dff0000"),
                KML.width(3)
                ),  
            id="gliderBlueLine")
        )
    doc.Document.append(
        KML.Style(
            KML.LineStyle(
                KML.color("7d00ff00"),
                KML.width(3)
                ),  
            id="gliderGreenLine")
        )
    doc.Document.append(
        KML.Style(
            KML.LineStyle(
                KML.color("7d000000"),
                KML.width(3)
                ),  
            id="gliderBlackLine")
        )
    
    if glider == 'ramses':
        linestyle = "#gliderBlueLine"
    elif glider == 'modena':
        linestyle = "#gliderGreenLine"
    elif glider == 'salacia':
        linestyle = "#gliderBlackLine"
    elif glider == 'pelagia':
        linestyle = "#gliderGreenLine"
    else:
        linestyle = ""
    
    coord_str = ""
    for d in data:
        if d['lat'] and d['lon']:
            coord_str = coord_str + "%f,%f,%f\n" % (d['lon'], d['lat'], 0.)
    
    track_line = KML.Placemark(
        KML.name(glider),
        KML.description(glider),
        KML.styleUrl(linestyle),
        KML.LineString(
            KML.altitudeMode("absolute"),
            KML.coordinates(coord_str)
            )
        )
    # glider placemarks (pms)
    pms = []
    for d in data[:-1]:
        pms.append(
            KML.Placemark(
                # short time stamp
                KML.name(d['name']),
                # surface report data
                KML.description(d['description']), 
                KML.styleUrl("#prevPosnIcon"),
                KML.Point(
                    KML.altitudeMode("absolute"),
                    KML.coordinates("%f,%f,%f" % (d['lon'], d['lat'], 0.))
                    )
                )
            )
    # glider history placemarks (hpms) using timestamp tag
    histpms = []
    for idx, d in enumerate(data[:-1]):
        dt=d['dt']
        # YYYY-MM-DDTHH:MM:SS + Z for kml <timestamp>
        dt_str_begin = dt.isoformat()+'Z'
        dt_str_end = (data[idx+1]['dt']).isoformat()+'Z'

        histpms.append(
            KML.Placemark(
                # ISO time stamp to be displayed with marker
                KML.name(dt_str_begin),
                # surface report data (not for history placemarks
                # KML.description(d['description']), 
                KML.styleUrl("#histPosnIcon"),
                KML.Point(
                    KML.altitudeMode("absolute"),
                    KML.coordinates("%f,%f,%f" % (d['lon'], d['lat'], 0.))
                    ),
                KML.TimeSpan(
                    KML.begin(dt_str_begin),
                    KML.end(dt_str_end)
                    )
                )
            )
    
    
    d=data[-1]
    last_pm = KML.Placemark(
        # short time stamp
        KML.name(d['name']),
        # surface report data
        KML.description(d['description']), 
        KML.styleUrl("#lastPosnIcon"),
        KML.Point(
            KML.altitudeMode("absolute"),
            KML.coordinates("%f,%f,%f" % (d['lon'], d['lat'], 0.))
            )
        )
    if d['wlon'] and d['wlat']:
        wp_pm = KML.Placemark(
            # KML.name('Surface Report Waypoint'),
            # surface report data
            KML.description('Surface Report Waypoint'), 
            KML.styleUrl("#lastWayPosnIcon"),
            KML.Point(
               KML.altitudeMode("absolute"),
               KML.coordinates("%f,%f,%f" % (d['wlon'], d['wlat'], 0.))
               )
            )
    track_folder = KML.Folder(
        KML.name(d['glider']),
        track_line,
        )
    for pm in pms:
        track_folder.append(pm)
    ##### no history markers with time span
    # for hpm in histpms:
    #     track_folder.append(hpm)    
    track_folder.append(last_pm)
    if d['wlon'] and d['wlat']:
        track_folder.append(wp_pm)
    doc.Document.append(
        track_folder
        )
    track_kml = lxml.etree.tostring(doc, pretty_print=True)
    # prepend <?xml> tag to make it XML DOM
    track_kmldom = '<?xml version="1.0" encoding="UTF-8"?>\n'+track_kml
    return track_kmldom

def parse_glider_goto_ma(lines, glider, gotofilename):
    data = []

    # filename should have the timestamp so using this to show in description time of waypoints
    dt_str = gotofilename

    # m = re.search(r'^(# File creation time:)\s*(.*)', ''.join(lines), re.MULTILINE)
    # if m: dt_str = m.group(2)
    # else: dt_str = None
    # just for label in description -- GCCS is in local, manual is in UTC --
    # too confusing to fix in software, so no implementing the following
    # try:
    # t = time.strptime(m.group(2), "%d-%b-%Y %H:%M:%S %Z")
    # the '*' operator unpacks the tuple, producing the argument list.
    # add 5 hours for GMT 
    # dt = datetime.datetime(*t[0:6]) + datetime.timedelta(hours=5)
    # dt_str = datetime.date.strftime(dt, "%Y-%m-%d %H:%M:%S UTC")
    # except:  dt_str = None

    m = re.search(r'\<start\:waypoints\>(.*)\<end\:waypoints\>', ''.join(lines), re.MULTILINE|re.S)
    latlonstr = m.group(1)
    latlons = re.split(r'\n', latlonstr)
    for ll in latlons:
        m = re.search(r'^\s*(-?\d{2})(\d{2}\.\d+)\s*(-?\d{2})(\d{2}\.\d+).*$', ll, re.MULTILINE)
        if m:
            #
            lat_deg = float(m.group(3))
            lat_min = float(m.group(4))
            # lat_hem = m.group(4).upper()
            #
            lon_deg = float(m.group(1))
            lon_min = float(m.group(2))
            # lon_hem = m.group(7).upper()
            if lat_deg<0:
                lat = lat_deg - lat_min/60.
            else:
                lat = lat_deg + lat_min/60.
            if lon_deg<0:
                lon = lon_deg - lon_min/60.
            else:
                lon = lon_deg + lon_min/60.
        else:
            lat = None
            lon = None
        html_str = '<div>'+glider+' goto position at</br> '+ dt_str + '</br>' + \
                   ll+'</div>'
        if lat and lon:
            data.append({'glider': glider, 
                         'name': '',
                         'description': html_str,
                         'lon': lon,
                         'lat': lat})
    # close for-loop
    return data

def generate_waypoint_kml(data, glider):
    """
    Use pykml 

    Usage: kml_doc_str = generate_waypoint_kml(data, glider)
    """
    from pykml.factory import KML_ElementMaker as KML
    import lxml.etree

    doc = KML.kml(
        KML.Document(
            KML.Name(glider + "_waypoint")
            )
        )
    doc.Document.append(
        KML.Style(
        KML.IconStyle(
          KML.scale(0.5),
          # KML.color("7dff00ff"),
          KML.Icon(KML.href("icons/wht-blank-lv.png"))
          ),
        KML.LabelStyle(
          KML.scale(0.7)
          ),
        id="gotoPosnIcon")
        )


    doc.Document.append(
        KML.Style(
            KML.LineStyle(
                KML.color("7dff0000"),
                KML.width(2)
                ),  
            id="gliderBlueLine")
        )
    doc.Document.append(
        KML.Style(
            KML.LineStyle(
                KML.color("7d00ff00"),
                KML.width(2)
                ),  
            id="gliderGreenLine")
        )

    doc.Document.append(
        KML.Style(
            KML.LineStyle(
                KML.color("7d000000"),
                KML.width(2)
                ),  
            id="gliderBlackLine")
        )
    
    if glider == 'ramses':
        linestyle = "#gliderBlueLine"
    elif glider == 'modena':
        linestyle = "#gliderGreenLine"
    elif glider == 'salacia':
        linestyle = "#gliderBlackLine"
    elif glider == 'pelagia':
        linestyle = "#gliderGreenLine"
    else:
        linestyle = ""
    
    coord_str = ""
    for d in data:
        if d['lat'] and d['lon']:
            coord_str = coord_str + "%f,%f,%f\n" % (d['lon'], d['lat'], 0.)
    
    waypoint_line = KML.Placemark(
        KML.name(glider),
        KML.description(glider+' latest goto waypoints'),
        KML.styleUrl(linestyle),
        KML.LineString(
            KML.altitudeMode("absolute"),
            KML.coordinates(coord_str)
            )
        )
    # glider placemarks (pms)
    pms = []
    for d in data[:-1]:
        pms.append(
            KML.Placemark(
                # short time stamp
                KML.description(d['description']),
                KML.styleUrl("#gotoPosnIcon"),
                KML.Point(
                    KML.altitudeMode("absolute"),
                    KML.coordinates("%f,%f,%f" % (d['lon'], d['lat'], 0.))
                    )
                )
            )

    d = data[-1]
    wp_folder = KML.Folder(
        KML.name(d['glider']),
        waypoint_line,
        )
    for pm in pms:
        wp_folder.append(pm)
    doc.Document.append(
        wp_folder
        )
    track_kml = lxml.etree.tostring(doc, pretty_print=True)
    # prepend <?xml> tag to make it XML DOM
    track_kmldom = '<?xml version="1.0" encoding="UTF-8"?>\n'+track_kml
    return track_kmldom

# -------------------------------------------------------------------    
# playground
# glider='modena'
# indir = '/home/localuser/realtime/'+glider+'/logs'
# lines = load_glider_logs(indir, glider)
# data1 = parse_glider_logs(lines, glider)
# kml = generate_track_kml(data1, glider)

# fn = '/var/spool/mail/localuser'
# from pyglider import *
# fn = '/home/localuser/realtime/ramses/logs/ramses_network_20170922T221152.log'
# lines = load_data(fn)
# glider = 'ramses'
# indir = '/home/localuser/realtime/ramses/logs'
# lines = load_glider_logs(indir, glider)
# data = parse_glider_logs(lines, glider)

#
# fn = '/home/localuser/realtime/ramses/goto/20170922T014256_goto_l30.ma'
# lines = load_data(fn)
# glider = 'ramses'
# basefilename = os.path.split(fn)[1]
# data = parse_glider_goto_ma(lines, glider, basefilename)

# -------------------------------------------------------------------
