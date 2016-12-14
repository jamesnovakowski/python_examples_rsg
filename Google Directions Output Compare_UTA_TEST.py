# -*- coding: cp1252 -*-

"""
The goals of this code are:
    1. Determine if a reported transit path makese "sense"
    2. Assess a variety of metrics for whether the reported transit path "makes sense"
    3. Provide those assessments in a format that can be used to organize files for manual
       transit path cleaning.
"""

"""
Notes for further development:
We need to determine the format in which the route name and route short name are provided.
We will need to provide some sort of code, or some sort of transformation of the survey data
so that the Directions Routes can be compared to the Reported Routes.
"""

"""Instructions:

Please copy this syntax file into a folder containing the csv files you will be using to
perform transit path assessment.  This should include:
    1. Survey data records file
        a. Should include:
            i.      Surveyed Route
            ii.     Reported Routes
            iii.    Password
    2. Google Directions output file(s)
        a. Rows in this file should be identified by password, along with other output parameters.

Once all files are in place, please fill in the parameters indicated below.

After parameters have been filled in, you need to save this file.  Then, either run the syntax by selecting
"Run" from the options menu, or by double-clicking on the syntax file.
"""

survey_file = "UTA Phase1 Good from Round1 1-100.csv"     #Provide file name for Google Directions Output
directions_file = "UTA Phase1 Good from Round1_Output.csv"         #Provide file name for Survey Data
shapes_file = "Shapefiles\UTA_Routes_Phase1.shp"

"C:\Users\James.Novakowski\Desktop\Google Directions API Testing\UTA Phase1 Good from Round1 1-100.csv"

"""Import necessary extensions"""
import csv
import transitfeed.shapelib as shapelib
from math import radians, sqrt, sin, cos, atan2
import arcpy





""" Import necessary files
    Organize resulting data structures for ease of comparison"""

#This reads the routes shapefile into something we can use in assessments below.
##rows = arcpy.SearchCursor(shapes_file) #Update this line with the shapefile that you will be assessing the data against.
##shapes = {}
##for row in rows:
##    route_num = row.getValue('LineAbbr')                #Make sure you have a field named LineAbbr
##    routes_shapes = shapes.setdefault(route_num, [])
##    feat = row.getValue('Shape')
##    
##    for part in feat:
##        poly = shapelib.Poly()
##        
##        for pnt in part:
##            x = pnt.X
##            y = pnt.Y
##            point = shapelib.Point.FromLatLng(y,x)
##            poly.AddPoint(point)
##        routes_shapes.append(poly)


#open file
d_file = open(directions_file)
s_file = open(survey_file)

#read file into dictionary
d_dict = csv.DictReader(d_file)
s_dict = csv.DictReader(s_file)


#Organize Survey Data for Assessment
survey = {}
for row in s_dict:
    password = row["passcode"]
    route = row["ROUTE"][6:]
    routes = [row["R_TRNLIN1"][6:],
              row["R_TRNLIN2"][6:],
              row["R_TRNLIN3"][6:],
              row["R_TRNLIN4"][6:]]
    o = [row["oLat"],
         row["oLon"]]
    b = [row["bLat"],
         row["bLon"]]
    a = [row["aLat"],
         row["aLon"]]
    d = [row["dLat"],
         row["dLon"]]
    access = row["GETTO"]
    egress = row["GETFROM"]

    survey[password] = {"password":password, "route":route, "routes": routes,
                        "o":o, "b":b, "a":a, "d":d, "access":access, "egress":egress} 

s_file.close()

directions = {}

#should read all values as values? as opposed to strings? maybe... can figure out later...
for row in d_dict:
    password = row["passcode"]
    origin = row["origin"]
    dest = row["destination"]
    travel_mode = row["travel_mode"]
    route = row["route"]              #This represents which alternative route is being discussed.
    step = row["step"]
    step_start = [row["step_start_lat"],
                  row["step_start_lng"]]
    step_end = [row["step_end_lat"],
                row["step_end_lng"]]
    transitline = row["line_short_name"]
    transitline_long = row["line_name"]
    agency = row["agency_name"]
    
    leg_distance = row["leg_distance_value"] #I think this is in yards?
    leg_duration = row["leg_duration_value"] #This is in seconds.


##    directions[password] = {"password":password, "origin":origin, "destination":dest, "travel_mode":travel_mode,
##                            "route":[route],"transit_short_steps":[transitline], "transit_long_steps":[transitline_long],
##                            "step_start":[step_start],"step_end":[step_end]}
    

    if password in directions.keys():
        
        if route in directions[password]["route"]:
            if travel_mode == "TRANSIT":
                alt = int(route) - 1
                directions[password]["transit_short_steps"][alt].append(transitline)
                directions[password]["transit_long_steps"][alt].append(transitline_long)
                directions[password]["step_start"][alt].append(step_start)
                directions[password]["step_end"][alt].append(step_end)
        else:
            if travel_mode == "TRANSIT":
                alt = int(route) - 1
                directions[password]["route"].append(route)
                directions[password]["transit_short_steps"].append([transitline])
                directions[password]["transit_long_steps"].append([transitline_long])
                directions[password]["step_start"].append([step_start])
                directions[password]["step_end"].append([step_end])
    else:
        if travel_mode == "TRANSIT":
            directions[password] = {"password":password, "origin":origin, "destination":dest, "travel_mode":travel_mode,
                                    "route":[route],"transit_short_steps":[[transitline]], "transit_long_steps":[[transitline_long]],
                                    "step_start":[[step_start]],"step_end":[[step_end]]}
        if travel_mode == "NULL":
            directions[password] = {"password":password, "origin":origin, "destination":dest, "travel_mode":travel_mode,
                                    "route":[route],"transit_short_steps":[[transitline]], "transit_long_steps":[[transitline_long]],
                                    "step_start":[[step_start]],"step_end":[[step_end]]}
        
d_file.close()    


""" Define functions for assessment and comparison of transit path cleaning"""

#Surveyed route in reported routes
def check_surveyed_route_in_surveyroutes (route,transitlines):
    if route in transitlines:
        check = 1
    else:
        check = 0
    return check
    

#Surveyed route in Directions output
def check_surveyed_route_in_google_routes (route,google_routes):
    for routes in google_routes:
        if route in routes:
            check = 1
            return check    #will this exit the function?  If not, logic in code below should make it run properly.
                            #Multiple return statements are OK, they help with control flow
        else:
            check = 0
    return check


#All reported routes in at at least 1 of the Directions Alternatives
def check_routes_in_output (routes,output):
    #routes is the list of routes reported by the respondent
    #output is the list of lists of routes returned by google directions

    checks = [2, 2, 2, 2]
    nums = [0,1,2,3]
   
    for num in nums:
        if len(routes) > num and routes[num] != '':
            checks[num] = check_surveyed_route_in_google_routes(routes[num], output)
            
    return checks


#Determines whether order of reported transit steps agrees with google output
"""Potential Issues with this Assessment:
    - Would miss trips that need another route to complete the trip
    - Drive/Drive trips often marked as bad
    - If drove long distance to system access, likly indicates invalid trip."""
def check_route_order (routes, short_steps):
    #routes is the list of routes reported by the respondent
    #short_steps is the list of lists of routes returned by google directions
    return_value = 0
    for trip in short_steps:
        i = 0
        while i <= 3 and routes[i] != '' and len(trip) >= (i+1):
            if routes[i] == trip[i]:
                i = i+1
                if routes[i] == '':
                    return 1
            else:
                break
    return return_value

#This is the haversine distance function for two latitude/longitude pairs.
def geocalc(lat1, lon1, lat2, lon2):
    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlon = lon1 - lon2

    EARTH_R = 6372.8

    y = sqrt(
        (cos(lat2) * sin(dlon)) ** 2
        + (cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)) ** 2
        )
    x = sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(dlon)
    c = atan2(y, x)
    return EARTH_R * c

def check_OB_AD_dist(o_pt, b_pt, a_pt, d_pt):
    ob_dist = geocalc(o_pt[0],o_pt[1],b_pt[0],b_pt[1])
    da_dist = geocalc(a_pt[0],a_pt[1],d_pt[0],d_pt[1])
    oa_dist = geocalc(o_pt[0],o_pt[1],a_pt[0],a_pt[1])
    db_dist = geocalc(d_pt[0],d_pt[1],b_pt[0],b_pt[1])

    if ob_dist > oa_dist or da_dist > db_dist:
        return 0
    return 1

#Checks the distance from the board location to the board locations for the Surveyed
#route in the google output
#If within a certain threshold, 1, else, 0
def check_board_loc(password):
    line = survey[password]['route']
    board_loc = survey[password]['b']
    out_routes = directions[password]['transit_short_steps']
    out_boards = directions[password]['step_start']

    for alt in out_routes:
        for route in alt:
            if line == route:
                out_board = out_boards[out_routes.index(alt)][alt.index(route)]
                dist = geocalc(out_board[0],out_board[1],board_loc[0],board_loc[1])
                if dist < .5:
                    return 1
    return 0            
                
#Checks the distance from the alight location to the alight locations for the Surveyed
#route in the google output.
#If within a certain threshold, 1, else, 0
def check_alight_loc(password):
    line = survey[password]['route']
    alight_loc = survey[password]['a']
    out_routes = directions[password]['transit_short_steps']
    out_alights = directions[password]['step_end']

    for alt in out_routes:
        for route in alt:
            if line == route:
                out_alight = out_alights[out_routes.index(alt)][alt.index(route)]
                dist = geocalc(out_alight[0],out_alight[1],alight_loc[0],alight_loc[1])
                if dist < .5:
                    return 1
    return 0

def check_origin_destination_dist(password):
    origin = survey[password]['o']
    destination = survey[password]['d']
    dist = geocalc(origin[0],origin[1],destination[0],destination[1])
    if dist > .5:
        return 1
    return 0

def check_board_alight_dist(password):
    board = survey[password]['b']
    alight = survey[password]['a']
    dist = geocalc(board[0],board[1],alight[0],alight[1])
    if dist > .5:
        return 1
    return 0

def check_access_dist(password):
    line = survey[password]['routes'][0]
    origin = survey[password]['o']
    out_routes = directions[password]['transit_short_steps']
    out_boards = directions[password]['step_start']
    amode = survey[password]["access"]

    good_access_dist = 0
    for alt in out_routes:
        for route in alt:
            if line == route:
                out_board = out_boards[out_routes.index(alt)][alt.index(route)]
                dist = geocalc(out_board[0],out_board[1],origin[0],origin[1])
                if amode == "walk": 
                    if dist < 2:
                        return 1
                elif amode == "bike":
                    if dist < 10:
                        return 1
                else:
                    good_access_dist = 1             
    return good_access_dist


def check_egress_dist(password):
    i = 3
    while survey[password]['routes'][i] == '':
        i = i-1
    line = survey[password]['routes'][i]
    dest = survey[password]['d']
    out_routes = directions[password]['transit_short_steps']
    out_alights = directions[password]['step_end']
    dmode = survey[password]["egress"]

    good_egress_dist = 0
    for alt in out_routes:
        for route in alt:
            if line == route:
                out_alight = out_alights[out_routes.index(alt)][alt.index(route)]
                dist = geocalc(out_alight[0],out_alight[1],dest[0],dest[1])
                if dmode == "walk": 
                    if dist < 2:
                        return 1
                elif dmode == "bike":
                    if dist < 10:
                        return 1
                else:
                    good_access_dist = 1             
    return good_egress_dist


#Any reported routes unncessary?

#No timestamp, cannot assess

#Any reported routes redundant? (As in, are they alternatives to each other?)  - Maybe don't do this

#Others?


"""The following syntax runs through the various assessments, and creates an output file
   that records this information linked to each record.""" 

filename = "UTA Phase1 Good from Round1 - Auto Assess.csv"

outfile = open(filename, 'w')

#header = ["Password","route_in_routes","route_in_output","routes_in_output"]
header2 = ["Password","route_in_routes",
           "route_in_output",
           "routes_in_output1","routes_in_output2","routes_in_output3","routes_in_output4",
           "all_routes_in_output",
           "routes_in_order",
           "ob_ad_distances",
           "board_good",
           "alight_good",
           "origin_dest_dist_good",
           "board_alight_dist_good",
           "access_mode_good",
           "egress_mode_good"]

outfile.write(','.join(header2) + '\n')

""" Call functions to run assessments """
for password in survey:
    surveyed = survey[password]
    google = directions[password]

    #Auto-check using google directions output
    route_in_routes = check_surveyed_route_in_surveyroutes(surveyed["route"], surveyed["routes"])
    route_in_output = check_surveyed_route_in_google_routes(surveyed["route"], google["transit_short_steps"])
    routes_in_output = check_routes_in_output(surveyed["routes"], google["transit_short_steps"]) # 0 = no, 1 = Yes, 2 = Could not test
    all_routes_in_output = 1

    for route in routes_in_output:
        if route == 0 or all_routes_in_output < 1:
            all_routes_in_output = 0

    routes_in_order = check_route_order(surveyed["routes"], google["transit_short_steps"])
    stops_ob_ad = check_OB_AD_dist(surveyed["o"], surveyed["b"], surveyed["a"], surveyed["d"])
    board_loc_good = check_board_loc(password)
    alight_loc_good = check_alight_loc(password)
    origin_destination_dist = check_origin_destination_dist(password)
    board_alight_dist = check_board_alight_dist(password)
    

    access_good = check_access_dist(password)
    egress_good = check_egress_dist(password)
    


    #Check locations against each other.  
            
    
    outfile.write(','.join([password,
                            str(route_in_routes),
                            str(route_in_output),
                            str(routes_in_output[0]),
                            str(routes_in_output[1]),
                            str(routes_in_output[2]),
                            str(routes_in_output[3]),
                            str(all_routes_in_output),
                            str(routes_in_order),
                            str(stops_ob_ad),
                            str(board_loc_good),
                            str(alight_loc_good),
                            str(origin_destination_dist),
                            str(board_alight_dist),
                            str(access_good),
                            str(egress_good)]) + '\n')

outfile.close()

""" Output file files, with assessments, to be used for Transit Path cleaning """


