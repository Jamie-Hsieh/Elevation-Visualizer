import time
from datetime import datetime

import pandas as pd
import rasterio
from rasterio.transform import rowcol


# =====================================================
# USER SETTINGS
# =====================================================

CSV_PATH = r"D:\SRTM\8899ElevationData\8899_tb1s_LON_LAT_ORDERED.csv"

TIF_PATH = r"D:\SRTM\8899ElevationData\merged_srtm.tif"

PROGRESS_INTERVAL = 10000

currentTime = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_CSV = f"{currentTime}_LonLatOutput.csv"


# =====================================================
# ELEVATION LOOKUP
# =====================================================

class ElevationLookup:

    def __init__(self, tif_path):

        print("\n========== GEO TIFF LOAD ==========")
        print(f"Opening: {tif_path}")

        self.src = rasterio.open(tif_path)

        print("Reading raster band into memory...")

        self.band = self.src.read(1)

        print("Raster loaded successfully")

        print(
            f"Dimensions: "
            f"{self.band.shape[1]} cols x "
            f"{self.band.shape[0]} rows"
        )

    def get_elevation(self, lon, lat):

        try:

            row, col = rowcol(
                self.src.transform,
                lon,
                lat
            )

            if (
                row < 0
                or row >= self.band.shape[0]
                or col < 0
                or col >= self.band.shape[1]
            ):
                return -1

            return float(self.band[row, col])

        except Exception:
            return -1


# =====================================================
# PROCESS CSV
# =====================================================

def process_csv(csv_path, tif_path, output_path):

    overall_start = time.time()

    print("\n========== CSV LOAD ==========")
    print(f"Reading CSV: {csv_path}")

    csv_start = time.time()

    df = pd.read_csv(csv_path)

    print(
        f"CSV loaded in "
        f"{time.time() - csv_start:.2f}s"
    )

    print(f"Rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")

    if len(df.columns) < 3:
        raise ValueError(
            "CSV must contain at least 3 columns."
        )

    lon_col = df.columns[1]
    lat_col = df.columns[2]

    print(f"Longitude column: {lon_col}")
    print(f"Latitude column : {lat_col}")

    lookup = ElevationLookup(tif_path)

    print("\n========== PROCESSING ==========")

    total = len(df)

    elevations = []

    start_time = time.time()

    for idx, row in enumerate(df.itertuples(index=False), start=1):

        lon = row[1]
        lat = row[2]

        elevation = lookup.get_elevation(
            lon,
            lat
        )

        elevations.append(elevation)

        if elevation == -1:
            print("LON: ", lon, "LAT: " , lat, "     Elevation -1")



        if idx % PROGRESS_INTERVAL == 0:

            elapsed = time.time() - start_time

            rate = idx / elapsed

            remaining = (total - idx) / rate

            print(
                f"{idx:,}/{total:,} "
                f"({100 * idx / total:.2f}%) | "
                f"{rate:,.0f} rows/sec | "
                f"ETA {remaining / 60:.1f} min"
            )

    print("\nAssigning elevation column...")

    df["elevation"] = elevations

    print(f"Writing output: {output_path}")

    write_start = time.time()

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Output written in "
        f"{time.time() - write_start:.2f}s"
    )

    print("\n========== COMPLETE ==========")

    print(
        f"Total runtime: "
        f"{time.time() - overall_start:.2f}s"
    )

    print(
        f"Rows processed: "
        f"{total:,}"
    )

    print(
        f"Output file: "
        f"{output_path}"
    )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    process_csv(
        csv_path=CSV_PATH,
        tif_path=TIF_PATH,
        output_path=OUTPUT_CSV
    )