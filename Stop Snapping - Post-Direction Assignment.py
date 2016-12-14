#This file originally developed by Eric Talbot for the Seattle Sound Transit OD 2011-2012
#Filepath: "Q:\Projects\WA\Sound Transit\11166 Sound Transit 2011-2012 OD\9. Analysis\Weighting\python\weight_data.py"
#Referring to this folder may help figure out different pieces of code.

'''
We have a shape file called "busstop.shp"
It has points for bus stops, along with a field called busstop_id
I think we can use this for bus stop locations
we'll open the shape file, and read the contents
stop locations will be stored as transitfeed points
in a dictionary called "stops" keyed by stop id
'''
import csv

import traceback
import arcpy
import transitfeed.shapelib as shapelib

GTFS_Stops = "stops.csv"
GTFS_Stop_Route_Match = "cleaned Dec GTFS data de-duped.csv"
Survey_Data = "stop snapping data w direction final(2).csv"
Output_File = "stop snapping final wo 217.csv"


stops = {}
f = open(GTFS_Stops)
d = csv.DictReader(f)

for row in d:
    my_pnt = shapelib.Point.FromLatLng(float(row["stop_lat"]), float(row["stop_lon"]))
    stops[int(row["stop_id"])] = my_pnt #stop id is an integer
##except:
##    print row["stop_id"]
##    print "James says there's an error here"

f.close()


'''    
now we need to assemble a dataset with legs,
where a leg is a sequence of stops associated with a
certain route, direction, and express status
we get the trips from the file "Fall2011-ZoneSequence-STLyerla.xls"
which I've saved as a .csv

Let's read the legs into a dictionary
'''
f = open(GTFS_Stop_Route_Match)
d = csv.DictReader(f)
legs = {}
import collections
class LegKey(collections.namedtuple('LegKey','number, direction')): #for Phase2, include "direction" in legkey
    pass
for row in d:
    number = row['route_short_name'] # an integer
    direction = row['direction_id'].strip() # either "1" or "0"
    #type_ = row['E/L'].strip() # either "E" or "L"
    assert direction in '01'
    #assert type_ in 'EL'

    seq = int(row['stop_sequence'])
    stop_id = int(row['stop_id'])
    legs.setdefault(LegKey(number, direction),[]).append((seq,stop_id))

for v in legs.values():
    v.sort()

#not sure exactly what this does, we'll see how it plays out.
for k,v in legs.items():
    legs[k] = map(lambda x: x[1], v)



f.close()


'''

Let's read in the survey data now
This is not a final version, so we'll need to come back to this to make sure
every thing works out still.

First we need to check that every respondent's leg is in the
legs dictionary, and that every stop in every respondent's leg is
in the stops dictionary

'''


f = open(Survey_Data)
d = csv.DictReader(f)
respondent_legs = set()

for row in d:
    if row['ROUTE'].strip() not in ['Sodo','']:        

        passcode = row['PASSWORD']

        surveyed_route = row['ROUTE'].strip()

        number = row['ROUTE']

        direction = row['direction']
##        
##        assert direction in 'IO'
        
        leg = LegKey(number, direction)

        respondent_legs.add(leg)


missing_legs = set()
missing_stops = set()
for leg in respondent_legs:
    if leg not in legs.keys():
        missing_legs.add(leg)
    else:
        for stop_id in legs[leg]:
            if stop_id not in stops.keys():
                missing_stops.add((leg, stop_id)) 

print missing_legs
print missing_stops





f.close()                                


'''
so now let's create the respondents dictionary
each respondent will have:
a passcode
a leg
a time period (may be missing) (should somehow align with the time period from the ridership data)
a boarding lat/lng (maybe missing)
an alighting lat/lng (may be missing)


'''

    
import datetime
f = open(Survey_Data)
d = csv.DictReader(f)
respondents = {}
for row in d:
     
    passcode = row['PASSWORD']

    surveyed_route = row['ROUTE'].strip()

    number = row['ROUTE']
    
    direction = row['direction']
##    assert direction in 'IO'
    leg = LegKey(number, direction)
##    time = row['TripStartTime'].strip()       #should add this in later
  
    time_period = None


    
    b_lat = row['bLat'].strip()
    b_lon = row['bLon'].strip()
    if b_lat != '' and b_lon != '':
        b_lat = float(b_lat)
        b_lon = float(b_lon)
        boarding = shapelib.Point.FromLatLng(b_lat, b_lon)
    else:
        boarding = None

    a_lat = row['aLat'].strip()
    a_lon = row['aLon'].strip()
    if a_lat != '' and a_lon != '':
        a_lat = float(a_lat)
        a_lon = float(a_lon)
        alighting = shapelib.Point.FromLatLng(a_lat, a_lon)
    else:
        alighting = None

    respondents[passcode] = dict(time_period = time_period,
                                 leg = leg,
                                 b_pnt = boarding,
                                 a_pnt = alighting,
                                 direction = direction)


f.close()                                

'''
now, need to assign each respondent to a boarding stop and an alighting stop in its leg

'''

def findClosestStop(pnt, leg_stop_ids):
    min_dist = 99999999999999999999999
    min_dist_stop_id = None

    for stop_id in leg_stop_ids:
        stop_point = stops[stop_id]
        dist = stop_point.GetDistanceMeters(pnt)
        if dist < min_dist:
            min_dist = dist
            min_dist_stop_id = stop_id                                               
                                                                

    return min_dist_stop_id


for passcode, r in respondents.items():
    b_pnt = r['b_pnt']
    a_pnt = r['a_pnt']
    r['b_stop_id'] = None
    r['a_stop_id'] = None
    if not (r['leg'] == LegKey(number='', direction='0') or r['leg'] == LegKey(number='', direction='#N/A')
            or r['leg'] == LegKey(number='', direction='1')
            or r['leg'] == LegKey(number='NULL', direction='#N/A')
            or r['leg'] == LegKey(number='NULL', direction='0')
            or r['leg'] == LegKey(number='NULL', direction='1')
            or r['leg'] == LegKey(number='', direction='')
            or a_pnt is None or b_pnt is None):
        if not (b_pnt is None):
            r['b_stop_id'] = findClosestStop(b_pnt, legs[r['leg']])
        if not(a_pnt is None):
            r['a_stop_id'] = findClosestStop(a_pnt, legs[r['leg']])




    
f = open(Output_File,'w')
f.write('passcode,route,direction,time_period,b_stop_id,a_stop_id,segment_id\n')
for passcode, r in respondents.items():
    #segment_id = leg_stop_segment.get((r['leg'],r['b_stop_id']))
    row = [passcode, r['leg'].number, r['leg'].direction, r['time_period'],
           r['b_stop_id'],r['a_stop_id']]#,segment_id]

    row = [str(x) for x in row]
    row = ','.join(row) + '\n'
    f.write(row)

f.close()
    






