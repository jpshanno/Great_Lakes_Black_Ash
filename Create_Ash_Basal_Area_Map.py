# Create a unified map of 250m resolution kNN-estimated F. nigra basal area
# estimates in square feet per acre from US and Canadian datasets

# Joe Shannon
# Sept. 5, 2017
# Requires ArcMap and the Spatial Analyst Extension

# 
# https://www.fs.fed.us/ne/newtown_square/publications/technical_reports/pdfs/2004/ne_gtr319.pdf
# https://www.fs.fed.us/ne/global/pubs/books/dia_biomass/index.shtml
# https://www.fs.fed.us/nrs/pubs/jrnl/2014/nrs_2014_chojnacky_001.pdf

import os  
import arcpy
import arcpy.sa
from numpy import pi

# Set data paths
envPath = os.path.dirname(os.path.realpath(__file__))
usMap = r'.\Data_Raw\US_BasalArea_kNN_Maps\s543.img'
caMap = r'.\Data_Raw\CA_Biomass_kNN_Maps\NFI_MODIS250m_kNN_Species_Frax_Nig_reproj.tif'
greatLakesWatersheds = r'..\Great_Lakes\Great_Lakes_Watersheds.shp'
greatLakesSubwatersheds = r'..\Great_Lakes\Great_Lakes_Subwatersheds.shp'
lakeSuperiorWatershed = r'..\Great_Lakes\Lake_Superior_Watershed.shp'

# Set coefficients for black ash biomass equation. DBH in cm, AGB in kg, and a
# conversion factor to go from AGB (kg/ha) to basal area in (ft^2 ac^-1)
#                   BA (ft^2 ac^-1) = 10.31443 * AGB (kg/ha)
# The AGB value is adjusted by the ratio of the US mean and max to the CA mean and max AGBs
m = 10.31443

# Set options
arcpy.env.overwriteOutput = True  
arcpy.CheckOutExtension('Spatial')
arcpy.env.workspace = envPath

# To match US and CA formats set all zero cells with NoData in the CA dataset
caMapNoZero = arcpy.sa.SetNull(caMap, caMap, "VALUE = 0")

# Calculate the mean and max AGB for each dataset
caMeanAGB = float(arcpy.GetRasterProperties_management(caMapNoZero, "MEAN").getOutput(0))
usMeanBA = float(arcpy.GetRasterProperties_management(usMap, "MEAN").getOutput(0))
caMaxAGB = float(arcpy.GetRasterProperties_management(caMapNoZero, "MAXIMUM").getOutput(0))
usMaxBA = float(arcpy.GetRasterProperties_management(usMap, "MAXIMUM").getOutput(0))

usMeanAGB = usMeanBA/m
usMaxAGB = usMaxBA/m

adjustValue = ((usMeanAGB/caMeanAGB) + (usMaxAGB/caMaxAGB))/2

# Convert Canadian data from kg/ha to ft^2/ac^-1
caBasalAreaMap = m*(caMapNoZero*adjustValue)

# Combine US and CA maps
arcpy.MosaicToNewRaster_management([caBasalAreaMap, usMap], \
                                   ".\Data_Output", \
                                   "Fraxinus_nigra_Basal_Area_sqft_acre_Full_Range.img", \
                                   usMap, \
                                   pixel_type = "32_BIT_FLOAT", \
                                   number_of_bands = 1, \
                                   mosaic_method = "MEAN")
ashFullRange = arcpy.Raster(".\Data_Output\Fraxinus_nigra_Basal_Area_sqft_acre_Full_Range.img")
ashGreatLakes = arcpy.sa.ExtractByMask(ashFullRange, greatLakesWatersheds)
ashGreatLakes.save(".\Data_Output\Fraxinus_nigra_Basal_Area_sqft_acre_Great_Lakes.img")
