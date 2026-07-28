import csv

# ======================================
# USER SETTINGS
# ======================================

INPUT_CSV = r"D:\SRTM\8899ElevationData\8899_TB1S_SLOPE.csv"
OUTPUT_CSV = r"D:\SRTM\8899ElevationData\8899_TB1S_SLOPE_LIN_SMOOTH_30M.csv"

WINDOW_SMOOTH = False
DISTANCE_SMOOTH = True

DISTANCE_SMOOTH_REQ = 30 #meters

ELEVATION_COLUMN = 3
LIN_DIST_COLUMN = 4
SLOPE_COLUMN = 5
WINDOW_BACK = 5
WINDOW_FORWARD = 5


# ======================================
# LOAD FILE
# ======================================

with open(INPUT_CSV, "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    header = next(reader)

    rows = list(reader)

print(f"Loaded {len(rows):,} rows")
    

def distSmooth():
    linDists = []
    linDistCounter = 0
    slopes = []
    elevations = []
    #add all lindists to list
    for row in rows:
        linDists.append(float(row[LIN_DIST_COLUMN]))
        elevations.append(float(row[ELEVATION_COLUMN]))
    startIndex = 0
    linDistMaxIndex = len(linDists) - 1
    mostRecentSlope = 0
    #start index at distance smooth req
    for j in range (0,DISTANCE_SMOOTH_REQ):
        slopes.append(mostRecentSlope)
    for i in range(DISTANCE_SMOOTH_REQ, len(linDists)):
        linDistCounter += linDists[i]
        slopes.append(mostRecentSlope)
        if linDistCounter >= DISTANCE_SMOOTH_REQ:
            mostRecentSlope = (
            (elevations[i] - elevations[startIndex]) /
            (linDistCounter)
            )

            startIndex = i
            print("LinDistCounter = " , linDistCounter)
            linDistCounter = 0
    print("length of return: " , len(slopes) , " length of original list: ", len(linDists))
    return slopes

def windowSmooth():
    # ======================================
    # EXTRACT SLOPES
    # ======================================

    slopes = []

    for row in rows:
        slopes.append(float(row[SLOPE_COLUMN]))

    
    # ======================================
    # SMOOTH
    # ======================================

    smoothed_slopes = []

    for i in range(len(slopes)):

        values = []

        for offset in range(-WINDOW_BACK, WINDOW_FORWARD + 1):

            idx = i + offset

            # backfill beginning
            if idx < 0:
                idx = 0

            # forward fill end
            elif idx >= len(slopes):
                idx = len(slopes) - 1

            values.append(slopes[idx])

        avg = sum(values) / len(values)

        smoothed_slopes.append(avg)

        if i % 100000 == 0:
            print(f"Smoothed: {i:,}")
    return smoothed_slopes

# ======================================
# REPLACE COLUMN
# ======================================
slopeOutput = []
if (WINDOW_SMOOTH):
    print("window smooth activated")
    slopeOutput = windowSmooth()
else:
    print("dist smooth activated")
    slopeOutput = distSmooth()

for i in range(len(rows)):
    rows[i][SLOPE_COLUMN] = slopeOutput[i]

# ======================================
# WRITE OUTPUT
# ======================================

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow(header)

    writer.writerows(rows)


    print()
    print("Done.")
    print(f"Output written to:")
    print(OUTPUT_CSV)