import os
import glob
import rasterio
from rasterio.merge import merge

# =====================================================
# USER SETTINGS
# =====================================================

TIF_FOLDER = r"D:\SRTM\8899ElevationData"

OUTPUT_FILE = os.path.join(
    TIF_FOLDER,
    "merged_srtm.tif"
)

# =====================================================
# FIND TILES
# =====================================================

tiles = glob.glob(
    os.path.join(TIF_FOLDER, "N*.tif")
)

if len(tiles) == 0:
    raise ValueError(
        f"No TIFF files found in:\n{TIF_FOLDER}"
    )

print("\nTiles found:")
for tile in sorted(tiles):
    print(f"  {os.path.basename(tile)}")

# =====================================================
# OPEN TILES
# =====================================================

src_files = []

for tile in tiles:

    src = rasterio.open(tile)

    src_files.append(src)

    print(
        f"\n{os.path.basename(tile)}"
    )

    print(
        f"Bounds: {src.bounds}"
    )

# =====================================================
# MERGE
# =====================================================

print("\nMerging tiles...")

mosaic, out_transform = merge(src_files)

print("Merge complete.")

# =====================================================
# OUTPUT METADATA
# =====================================================

out_meta = src_files[0].meta.copy()

out_meta.update({
    "driver": "GTiff",
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": out_transform
})

# =====================================================
# WRITE OUTPUT
# =====================================================

print(f"\nWriting output:\n{OUTPUT_FILE}")

with rasterio.open(
    OUTPUT_FILE,
    "w",
    **out_meta
) as dest:

    dest.write(mosaic)

# =====================================================
# CLEANUP
# =====================================================

for src in src_files:
    src.close()

# =====================================================
# VERIFY OUTPUT
# =====================================================

print("\nVerifying merged file...")

with rasterio.open(OUTPUT_FILE) as merged:

    print("\nMerged Raster Information")

    print(f"Width  : {merged.width}")
    print(f"Height : {merged.height}")
    print(f"CRS    : {merged.crs}")

    print(
        f"Bounds : {merged.bounds}"
    )

print(
    f"\nSuccessfully created:\n{OUTPUT_FILE}"
)