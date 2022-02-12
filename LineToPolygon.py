import time
import geopandas as gp
import pandas as pd, numpy as np, matplotlib.pyplot as plt


def processing(regionShape, datafilename):
    pd.set_option('display.max_columns', None)

    # data = pd.read_csv('DATA/yellow_tripdata_2014-01.csv',low_memory=False,nrows=1000)
    data = pd.read_csv(datafilename, encoding='utf-8')

    data[['longitude', 'latitude']] = data[['longitude', 'latitude']].apply(pd.to_numeric)
    gdata = gp.GeoDataFrame(data, geometry=gp.points_from_xy(data['longitude'], data['latitude']), crs='EPSG:4326')
    Result = gp.sjoin(gdata, regionShape, how='left')
    return Result


def lToP(geoJson, fromData, toData):
    region = gp.read_file(geoJson)
    region = region.to_crs(crs='EPSG:4326')
    region['center'] = region.centroid
    p = processing(region, fromData)
    d = processing(region, toData)

    result = pd.merge(p, d, left_index=True, right_index=True)
    result = result.dropna()
    result = result.reset_index(drop=True)

    tmp = pd.DataFrame(result)
    tmp2 = tmp.groupby(['index_right_x', 'index_right_y'], as_index=False).count()[
        ['index_right_x', 'index_right_y', 'time_x']]
    region = region['center']
    return region, tmp2


# a, b = lToP('./region2.geojson', './pickUpSmall.csv', 'dropOffSmall.csv')
# a, b = pTOl2('pickUp', 'dropOff')
