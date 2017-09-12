# Estimate water use by black ash in the Great Lakes Basin

# Joe Shannon
# Sept. 5, 2017
# Requires ArcMap and the Spatial Analyst Extension

import os  
import arcpy
import arcpy.sa
from numpy import pi

# Set data paths
envPath = os.path.dirname(os.path.realpath(__file__))
greatLakesWatersheds = r'..\Great_Lakes\Great_Lakes_Watersheds.shp'
greatLakesSubwatersheds = r'..\Great_Lakes\Great_Lakes_Subwatersheds.shp'
lakeSuperiorWatershed = r'..\Great_Lakes\Lake_Superior_Watershed.shp'
ashGreatLakes = arcpy.Raster(".\Data_Output\Fraxinus_nigra_Basal_Area_sqft_acre_Great_Lakes.img")

# Set options
arcpy.env.overwriteOutput = True  
arcpy.CheckOutExtension('Spatial')
arcpy.env.workspace = envPath

# Calculate water use for the Great Lakes Watershed and set all cells with less than
# 20 ft^2 ac^-1 of basal area equal to zero. Each cell is ~15.5 acres, so a BA
# of 20 ft^2 ac^-1 within a cell is equivalent to ~3.875 acres of black ash with a
# basal area of 80 ft^2 ac^-1, which is the average of our 9 study sites
minimumBA = "20" #str(pi*1**2)

ashGreatLakesTrimmed = arcpy.sa.Con(ashGreatLakes,
                                    ashGreatLakes,
                                    0,
                                    "VALUE > " + minimumBA)
ashGreatLakesTrimmed.save(".\Data_Output\Fraxinus_nigra_Basal_Area_sqft_acre_Great_Lakes_BA_Trimmed_"+ minimumBA + ".img")

# For reference these are the basal areas found in our inventory work (averaged plot BA ft^2/ac)
#
#   site basalArea_ft2_acre sapwoodArea_ft2_acre
#   009           69.77861            12.964199
#   077           60.41590            11.823875
#   119           90.47634            15.309882
#   135           27.11200             5.363406
#   140           88.75519            15.647365
#   151           66.81438            12.492229
#   152          119.82141            20.375210
#   156          119.83735            22.025969
#   157          104.34534            18.504743


# Calculate basin water use. Basal area is converted to sapwood area using my 
# data and our inventory data to generate the equation: 
#              SA (ft^2/ac) = 1.2500370 + 0.1648406*BA (ft^2/ac)
# The sapwood area was then used to calculate water use in cubic feet for each 
# cell. Water use was calcualted using summary statistics from modeled sap flux 
# that was predicted using transformed VPD and water level (see inundation project).
# 
saIntercept = 1.2500370
saSlope = 0.1648406

acresPerCell = 250*250*0.000247105
medianFlux_ft3_ft2d = 8.3619
meanFlux_ft3_ft2d = 8.7361
maxFlux_ft3_ft2d = 20.3371



medianFluxGreatLakes = arcpy.sa.Con(ashGreatLakesTrimmed,
                                    medianFlux_ft3_ft2d*(saIntercept + saSlope*ashGreatLakesTrimmed)*acresPerCell,
                                    0,
                                    "VALUE > 0")
maximumFluxGreatLakes = arcpy.sa.Con(ashGreatLakesTrimmed,
                                    maxFlux_ft3_ft2d*(saIntercept + saSlope*ashGreatLakesTrimmed)*acresPerCell,
                                    0,
                                    "VALUE > 0")


# Save the water use outputs
medianFluxGreatLakes.save(".\Data_Output\Fraxinus_nigra_Median_Water_Use_cubicft_Great_Lakes_BA_Trimmed_" + minimumBA + ".img")
maximumFluxGreatLakes.save(".\Data_Output\Fraxinus_nigra_Maximum_Water_Use_cubicft_Great_Lakes_BA_Trimmed_" + minimumBA + ".img")

# Convert to gallons and calculate zonal statistics

medianFluxGreatLakes_gallons = medianFluxGreatLakes * 7.48052

subwatershedMedian_ft3 = arcpy.sa.ZonalStatistics(greatLakesSubwatersheds, \
                                                  "Watershed", \
                                                  medianFluxGreatLakes, \
                                                  "SUM", \
                                                  "DATA")
subwatershedMedian_gal = arcpy.sa.ZonalStatistics(greatLakesSubwatersheds, \
                                                      "Watershed", \
                                                      medianFluxGreatLakes_gallons, \
                                                      "SUM", \
                                                      "DATA")
lakeBasinMedian_ft3 = arcpy.sa.ZonalStatistics(greatLakesWatersheds, \
                                               "LAKEBASIN", \
                                               medianFluxGreatLakes, \
                                               "SUM", \
                                               "DATA")
lakeBasinMedian_ft3_Int = arcpy.sa.Int(lakeBasinMedian_ft3)


subwatershedMedian_ft3.save(".\Data_Output\Zonal\Fraxinus_nigra_Median_Water_Use_cubicft_by_Subwatershed_BA_Trimmed_" + minimumBA + ".img")
subwatershedMedian_gal.save(".\Data_Output\Zonal\Fraxinus_nigra_Median_Water_Use_gallons_by_Subwatershed_BA_Trimmed_" + minimumBA + ".img")
lakeBasinMedian_ft3_Int.save(".\Data_Output\Zonal\Fraxinus_nigra_Median_Water_Use_cubicft_by_Lake_Basin_BA_Trimmed_" + minimumBA + ".img")

arcpy.BuildRasterAttributeTable_management(".\Data_Output\Zonal\Fraxinus_nigra_Median_Water_Use_cubicft_by_Lake_Basin_BA_Trimmed_" + minimumBA + ".img", "Overwrite")
