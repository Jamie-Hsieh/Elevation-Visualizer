import csv

# ======================================
# USER SETTINGS
# ======================================

INPUT_CSV = r"D:\SRTM\8899ElevationData\8899_TB1S_SLOPE.csv"
OUTPUT_CSV = r"D:\SRTM\8899ElevationData\8899_TB1S_SLOPE5s_SMOOTHED.csv"

SLOPE_COLUMN = 5

WINDOW_BACK = 2
WINDOW_FORWARD = 2

# ======================================
# LOAD FILE
# ======================================

with open(INPUT_CSV, "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    header = next(reader)

    rows = list(reader)

print(f"Loaded {len(rows):,} rows")

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

# ======================================
# REPLACE COLUMN
# ======================================

for i in range(len(rows)):
    rows[i][SLOPE_COLUMN] = smoothed_slopes[i]

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