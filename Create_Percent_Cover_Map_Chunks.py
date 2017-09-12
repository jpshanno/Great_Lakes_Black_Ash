import os  
import arcpy  
from arcpy.sa import Con
from arcpy.sa import IsNull
from numpy import isinf

#Define the function 'chunks' to break a list into sublists of size n
def chunks(l, n):  
    """ Yield successive n-sized chunks from l."""  
    for i in xrange(0, len(l), n):  
        yield l[i:i+n]  

##Set data paths
rasterPath = r'G:\Drive\Mapping\GIS\Ash_Cover\US_BasalArea_kNN_Maps'
ashMap = r'G:\Drive\Mapping\GIS\Ash_Cover\US_BasalArea_kNN_Maps\s543.img'
chunkPath = r'G:\Drive\Mapping\GIS\Ash_Cover\Chunk_Maps'
outPath = r'G:\Drive\Mapping\GIS\Ash_Cover'

##Set options
arcpy.env.overwriteOutput = True  
arcpy.CheckOutExtension('Spatial')
arcpy.env.workspace = rasterPath

##create a list of rasters in the workspace  
rasters = arcpy.ListRasters()

##Create sum maps in chunks of 50
i = 0
lst_cellstat = []  
for rasters_chunk in chunks(rasters, 50):  
    i += 1  
    cellstat = arcpy.sa.CellStatistics(rasters_chunk, "SUM", "DATA")  
    outname = os.path.join(chunkPath, "cellstat{0}".format(i))  
    cellstat.save(outname)  
    lst_cellstat.append(outname)  

####Sum the 50-species maps into one map
cellstat = arcpy.sa.CellStatistics(lst_cellstat, "SUM", "DATA")  
outname = os.path.join(rasterPath, "All_Species")  
cellstat.save(outname)

##Caluclate the percent of ash on the landscape
decimalAsh = arcpy.sa.Divide(ashMap, cellstat)
percentAsh = decimalAsh * 100

##Save the new output
outname = os.path.join(outPath, "Ash_Percent_kNN_250m_US.tif")
percentAsh.save(outname)



##From https://geonet.esri.com/thread/171685
##Original Code
##def main():  
##    import os  
##    import arcpy  
##  
##    data_path = r'E:\BOM\daily-temperature\daily-maximum-temperature\max_temp_1971_2000_grids'  
##    # out_path = r'E:\BOM\daily-temperature\daily-maximum-temperature'  
##    res_ws = r'E:\BOM\daily-temperature\daily-maximum-temperature\yourGDB.gdb' # I prefer gdb over folder  
##  
##    arcpy.env.overwriteOutput = True  
##    arcpy.CheckOutExtension('Spatial')  
##    arcpy.env.workspace = data_path  
##  
##    # create fgdb res_ws  
##    path, name = os.path.split(res_ws)  
##    arcpy.CreateFileGDB_management(path, name)  
##  
##    #create a list of rasters in the workspace  
##    rasters = arcpy.ListRasters()  
##  
##    i = 0  
##    lst_cellstat = []  
##    for rasters_chunk in chunks(rasters, 500):  
##        i += 1  
##        cellstat = arcpy.sa.CellStatistics(rasters_chunk, "SUM", "DATA")  
##        outname = os.path.join(res_ws, "cellstat{0}".format(i))  
##        cellstat.save(outname)  
##        lst_cellstat.append(outname)  
##  
##    # create the final raster  
##    cellstat = arcpy.sa.CellStatistics(lst_cellstat, "SUM", "DATA")  
##    outname = os.path.join(res_ws, "total_sum")  
##    cellstat.save(outname)  
##  
##    # eliminate intermediate results  
##    for ras in lst_cellstat:  
##        arcpy.Delete_management(ras)  
##  
##def chunks(l, n):  
##    """ Yield successive n-sized chunks from l."""  
##    for i in xrange(0, len(l), n):  
##        yield l[i:i+n]  
##  
##if __name__ == '__main__':  
##    main() 
