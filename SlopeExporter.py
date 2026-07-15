import math
import csv
import statistics
import sys
import pandas as pd
import random
import datetime as time

CSV_NAME = r"C:\Users\jamie.hsieh\Downloads\decemberelevationtest.csv"

#config
TIMESTAMP_COLUMN = 0
LON_COLUMN = 1
LAT_COLUMN = 2
ELEVATION_COLUMN = 3
SLOPE_AVERAGE_WINDOW_REVERSE = 2
SLOPE_AVERAGE_WINDOW_FORWARD = 2

#debug
HAVERDISTS_LENGTH = 0
ELEVDIFFS_LENGTH = 0

#Available user functions: haversine, saveElevations, saveLonLats, findElevationStdDev, findSlopes, 

#master list of elevations, lons, lats (support for multiple CSVs can be added easily)
TIMESTAMPS = []
ELEVATIONS = []
LONGITUDES = []
LATITUDES = []
LINEAR_DISTS = []
ELEV_DIFFS = []
SLOPES = []

def saveTimestamps(csv_filename):

    #in-function elevation list (in case multiple CSVs need to be supported)
    timeList = []
    with open(csv_filename, 'r', newline = '', encoding = 'utf-8') as f:
        reader = csv.reader(f)

        #skip header
        next(reader)

        timeProg = 0

        #parse all rows if there is more than 4 columns (check is technically not needed for timestamps)
        for row in reader:
            if len(row)>=4:
                try:
                    
                    timeList.append(str(row[TIMESTAMP_COLUMN]))
                    print("appending " , str(row[TIMESTAMP_COLUMN]), "   PROGRESS:" , timeProg)
                    timeProg +=1

                except ValueError:
                    pass

        if len(timeList) < 2:
            raise ValueError("need at least two numeric values in the fourth column.")
    return timeList

def saveElevations(csv_filename):

    #in-function elevation list (in case multiple CSVs need to be supported)
    elevList = []
    with open(csv_filename, 'r', newline = '', encoding = 'utf-8') as f:
        reader = csv.reader(f)

        #skip header
        next(reader)

        elevProg = 0

        #parse all rows if there is more than 4 columns
        for row in reader:
            if len(row)>=4:
                try:
                    
                    elevList.append(float(row[ELEVATION_COLUMN]))
                    print("appending " , float(row[ELEVATION_COLUMN]), "   PROGRESS:" , elevProg)
                    elevProg +=1

                except ValueError:
                    pass

        if len(elevList) < 2:
            raise ValueError("need at least two numeric values in the fourth column.")
    return elevList


def saveLons(csv_filename):
    lons = []
    with open(csv_filename, 'r', newline = '', encoding = 'utf-8') as f:

        reader = csv.reader(f)

        #progress indicator
        coordProg = 0

        #skip header
        next(reader)

        for row in reader:

            if len(row)>=4:

                lons.append(float(row[LON_COLUMN]))

                print("LONS appended " , float(row[LON_COLUMN]))

                coordProg+=1
    return lons

def saveLats(csv_filename):
    lats = []
    with open(csv_filename, 'r', newline = '', encoding = 'utf-8') as f:

        reader = csv.reader(f)

        #progress indicator
        coordProg = 0

        #skip header
        next(reader)

        for row in reader:

            if len(row)>=4:

                lats.append(float(row[LAT_COLUMN]))

                print("LATS appended " , float(row[LAT_COLUMN]), coordProg)

                coordProg+=1
    return lats

#find standard deviation of list
def findStdDev(listOfSomething):
    std_dev = statistics.pstdev(listOfSomething)
    return std_dev


#find haversines and save haversines to list
def findHaversines(lons, lats):

    haverDists = []

    #start haverDists with a value so slope diff calcs can happen
    haverDists.append(0)
    i = 1

    #create list of haversine distances bewteen points in meters
    for coord in lons:

        if (i<len(lons)):
            haverDists.append(haversine(lats[i-1], lons[i-1], lats[i],lons[i]))
            print("haversine " , f"{haversine(lats[i-1], lons[i-1], lats[i],lons[i])}")
            i+=1

    #return list of distances from previous point
    print("length: ", len(haverDists))
    return haverDists

def findElevDiffs(elevations):
    elevDiffs = []
    elevDiffs.append(0)
    for i in range (1, len(elevations)):
        elevDiffs.append(elevations[i] - elevations [i-1])
        print("appended ", elevations[i] - elevations [i-1])
    print("length: ", len(elevDiffs))
    return elevDiffs


def haversine(lat1, lon1, lat2, lon2):

    #given two coordinates, find distance in meters

    #Earth radius in km
    R = 6371.0

    #convert degrees to radians
    radLat1 = math.radians(lat1)
    radLat2 = math.radians(lat2)
    radLon1 = math.radians(lon1)
    radLon2 = math.radians(lon2)

    #diff between points
    diffLat = radLat1 - radLat2
    diffLon = radLon1 - radLon2

    #jamie don't know what this math do but this is the magic
    a = (
        math.sin(diffLat/2) **2
        +
        math.cos(radLat1) * math.cos(radLat2)
        *
        math.sin(diffLon/2) **2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # earth radius times c, converted to meters
    return R * c * 1000

def findSlopes(dists, elevDiffs):
    slopes = []
    if len(dists) == len(elevDiffs):
        for i in range (0, len(dists)):
            if dists[i] == 0:
                slopes.append(0)
            else:
                print("SLOPE ", elevDiffs[i]/dists[i])
                slopes.append(elevDiffs[i]/dists[i])
    else:
        print("the lists are different length!")
    return slopes

TIMESTAMPS = saveTimestamps(CSV_NAME)
ELEVATIONS = saveElevations(CSV_NAME)
LONGITUDES = saveLons(CSV_NAME)
LATITUDES = saveLats(CSV_NAME)
LINEAR_DISTS = findHaversines(LONGITUDES, LATITUDES)
ELEV_DIFFS = findElevDiffs(ELEVATIONS)
SLOPES = findSlopes(LINEAR_DISTS, ELEV_DIFFS)
print("lengths")
print(len(ELEVATIONS))
print(len(LATITUDES))
print(len(LONGITUDES))
print(len(TIMESTAMPS))
print(len(SLOPES))
print("elevation diffs length: " , f"{len(ELEV_DIFFS)}")
print("linear dists length: " ,f"{len(LINEAR_DISTS)}")

with open("output.csv", "w", newline = "") as f:
    writer = csv.writer(f)

    writer.writerow(["Timestamp", "Latitude", "Longitude", "Elevation", "LinearDistance", "Slope"])

data = pd.DataFrame({
    "Timestamp" : TIMESTAMPS,
    "Latitude" : LATITUDES,
    "Longitude" : LONGITUDES,
    "Elevation" : ELEVATIONS,
    "Linear Distance" : LINEAR_DISTS,
    "Slope" : SLOPES
})
currentTime = time.datetime.now().strftime("%Y%m%d_%H%M%S")
outputName = f"{currentTime}_SlopeOutput.csv"
data.to_csv(outputName, index = False)




    



