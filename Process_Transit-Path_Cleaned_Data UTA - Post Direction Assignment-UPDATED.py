#James, review this and update to make it clean. There are some large chunks of commented code down below.

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

first check to see if the "Part" field is needed
"Part" is not in the survey data set, so it would be nice if
we don't need it
'''
#Note: We cannot match the trips by direction, so we will disambiguate at a later time.
                                                                


#import csv         #import already performed
                                                                
#This code i think is unnecessary for what we are doing.                                                                
##f = open('GTFS Data with Stop and Route Matching 7.18.13.csv')
##d = csv.DictReader(f)
##temp = {}
##for row in d:
##    temp.setdefault((row['route_short_name'],row['direction_id'],row['E/L']),set()).add(row['Part'])
##f.close()
##for k,v in temp.items():
##    if len(v) > 1:
##        print k, v
##
##f.close

                                                    
'''
nothing prints, so we don't need the "Part" field.
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

for now we'll skip the link, sodo, and ''  surveys
we'll need to come back and figure out what to do
with the link and sodo surveys
'''


f = open(Survey_Data)
d = csv.DictReader(f)
respondent_legs = set()

for row in d:
    if row['ROUTE'].strip() not in ['Sodo','']:        

        passcode = row['PASSWORD']

        surveyed_route = row['ROUTE'].strip()

        number = row['ROUTE']

        #unfortunately, we don't have direction in the survey data
        direction = row['direction']
##        
##        assert direction in 'IO'
##        assert type_ in 'EL'


        
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
Ignoring the Link, Sodo, and '' respodents, every respondent's leg is
in the the legs dictionary

The following are legs that respondents were surveyed on, that have a missing stop
(the stop appears in the zone sequence file, but not in the stops shape file):


I'm going to add the missing stops into the stops dictionary
I'm using cross streets information from the ZoneRidership file
It seems like the two sets of intersections are referring to the same place:
thus the identical lat/lngs
'''


##stops[52221] = shapelib.Point.FromLatLng(47.470452,-122.333901)
##stops[52222] = shapelib.Point.FromLatLng(47.470452,-122.333901)



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
    leg = LegKey(number, direction)
  

#Update time field according to UTA times.  Not currently needed.
##"""
##    if time != '':
##        time = datetime.datetime.strptime(time,'%H:%M:%S').time()
##        if surveyed_route == 'Link':
##            
##            if time < datetime.time(3,0):
##                time_period = 'Link After 24:00'                
##            elif time < datetime.time(6,0):
##                time_period = 'Link Before 6:00'
##            elif time < datetime.time(9,0):
##                time_period = 'Link 6:00 - 9:00'
##            elif time < datetime.time(12,00):
##                time_period = 'Link 9:00 - 12:00'
##            elif time < datetime.time(15,00):
##                time_period = 'Link 12:00 - 15:00'
##            elif time < datetime.time(18,00):
##                time_period = 'Link 15:00 - 18:00'
##            elif time < datetime.time(21,00):
##                time_period = 'Link 18:00 - 21:00'
##            else:
##                time_period = 'Link 21:00 - 24:00'
##
##               
##        else:
##            
##            if time < datetime.time(6,0):
##                time_period = 'AAM'
##            elif time < datetime.time(9,0):
##                time_period = 'AM'
##            elif time < datetime.time(15,15):
##                time_period = 'MID'
##            elif time < datetime.time(18,15):
##                time_period = 'PM'
##            elif time < datetime.time(21,30):
##                time_period = 'XEV'
##            else:
##                time_period = 'XNT'    
##    else:
##        time_period = None
##"""
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






##This will be done later.
 

'''
need to read the ridership in
ridership is for busses only
keyed by leg(number, direction, type), time period, and stop id
'''

##f = open('Fall2011-ZoneRidership-STLyerla.csv')
##d = csv.DictReader(f)
##
##ridership = {}
##
##for row in d:
##    number = int(row['SignRt']) # an integer
##    direction = row['InOut'].strip() # either "I" or "O"
##    type_ = row['E/L'].strip() # either "E" or "L"
##    assert direction in 'IO'
##    assert type_ in 'EL'
##
##    stop_id = int(row['Zone#'])
##    time_period = row['Period']
##
##    boardings = float(row['OnsObs'])
##
##    leg = LegKey(number, direction, type_)
##
##    ridership.setdefault((leg,stop_id),{})[time_period] = boardings
##
##f.close()


'''
now divide legs up into segments
'''
##leg_stop_segment = {}
##import math
##f = open('20120515_leg_stop.csv','w')
##f.write('route,direction,type,stop,segment\n')
##for leg_key, leg in legs.items():
##    segment_size = len(leg) / 4.
##    max_cum = segment_size
##    segment_id = 1
##    cum = 0
##    for stop_id in leg:
##        cum += 1
##        if cum > max_cum:
##            max_cum += segment_size
##            segment_id += 1     
##        row = [leg_key.number, leg_key.direction, leg_key.type_, stop_id, segment_id]
##        row = [str(x) for x in row]
##        row = ','.join(row) + '\n'
##        f.write(row)
##        leg_stop_segment[leg_key,stop_id] = segment_id
##  
##f.close()   


'''
now aggregate ridership by segment

here we bring together two data sets: zone sequence and zone ridership

there may be a possibility that they don't agree

the approach here 


'''
##ridership_aggregated_to_segment = {}
##for leg_key, leg in legs.items():
##    if leg_key.number != 'Link':
##        for stop_id in leg:
##            if (leg_key, stop_id) not in ridership.keys():
##                print (leg_key, stop_id)
##            else:
##                for time_period in ridership[(leg_key, stop_id)].keys():
##
##                    boardings = ridership[leg_key, stop_id][time_period] #assumes that all legs in sequence exist ridership
##                    segment_id = leg_stop_segment[leg_key,stop_id]
##
##                    ridership_aggregated_to_segment.setdefault((leg_key, time_period, segment_id), 0.)
##                    ridership_aggregated_to_segment[(leg_key, time_period, segment_id)] += boardings                    
##
##    
##f = open('20120515_segment_timeperiod_ridership.csv','w')
##f.write('route,direction,type,time_period,segment_id,boardings\n')
##
##for k, boardings in ridership_aggregated_to_segment.iteritems():
##    leg, time_period, segment_id = k
##
##    row = [leg.number, leg.direction, leg.type_,
##           time_period, segment_id, boardings]
##
##    row = [str(x) for x in row]
##    row = ','.join(row) + '\n'
##    f.write(row)
##
##f.close()
##



""" We need to define a function that better assesses direction.  Implement later"""







    
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
    






