import json

import geopandas

# encoding:utf-8
import pandas as pd
import numpy as np
import geopandas as gp
from matplotlib import pyplot as plt
import time
import shpToJson as stj

import pyproj

def color_scale(val, maxVal, color_idx):
    per = 1.0 * val / maxVal
    if color_idx == 0:
        R = 255
        G = int((1 - per) * (244 - 31) + 31)
        B = 30
    elif color_idx == 1:
        R = 31
        G = int((1 - per) * (255 - 34) + 34)
        B = 255
    else:
        R = 125
        G = 125
        B = 125
    return [R, G, B]


def bufferSHP(r, baseData, inData):

    latitude = 'latitude'
    longitude = 'longitude'

    radius = r * 360.0/31544206

    # df = geopandas.read_file(r'E:\NEW TRY\DATA\extra data\Hotels_Properties_Citywide.csv', rows=10, encoding='utf-8')
    df = baseData
    df[['longitude', 'latitude']] = df[['longitude', 'latitude']].apply(pd.to_numeric)
    gdf = geopandas.GeoDataFrame(df, crs='EPSG:4326', geometry=geopandas.points_from_xy(df.longitude, df.latitude))

    gdf['centroid'] = gdf.centroid
    gdf = gdf.drop(['geometry'], axis=1)
    gdf['geometry'] = gdf['centroid'].buffer(distance=radius)
    gdf = gdf.drop(['centroid'], axis=1)

    gdf.to_file(r'./shp/Polygon/buffer.shp', driver='ESRI Shapefile', encoding='utf-8', crs='EPSG:4326')
    gdf.to_file(r'./shp/Geojson/buffer.geojson', driver='GeoJSON', encoding='utf-8', crs='EPSG:4326')

    start = time.perf_counter()
    pd.set_option('display.max_columns', None)
    regionShape = gp.read_file(r'./shp/Polygon/buffer.shp')  # .to_crs('EPSG:4326')
    # stj.trans('./shp/Polygon/buffer.shp', 'buffer')  # .to_crs('EPSG:4326')
    # print(regionShape.head)
    # regionShape.to_file('./region2.geojson', driver='GeoJSON')
    # print(regionShape)

    # data = pd.read_csv('DATA/yellow_tripdata_2014-01.csv',low_memory=False,nrows=1000)
    # data = pd.read_csv('./DATA./yellow_tripdata_2014-01.csv', nrows=100, encoding='utf-8')
    data = inData

    data[[longitude, latitude]] = data[[longitude, latitude]].apply(
        pd.to_numeric)
    gdata = gp.GeoDataFrame(data, geometry=gp.points_from_xy(data[longitude], data[latitude]),
                            crs='EPSG:4326')
    # print(regionShape.head())
    # print('\n\n\n\n\n')
    Result = gp.sjoin(gdata, regionShape, how='left')
    d = json.load(open('./shp/Geojson/buffer.geojson', encoding='utf-8'))
    bufferPolygon = pd.DataFrame(d["features"])
    length = regionShape.shape[0]
    Result = Result.dropna()
    raw_count = Result['index_right']
    count = []
    for j in range(length):
        count.append(0)
    for i in raw_count:
        count[int(i)] += 1

    # regionShape['count'] = count
    res = pd.DataFrame()
    res['count'] = count
    print(Result.head())
    end = time.perf_counter()
    print('\n\nRunning Time for 2.2Gb Data: %s Seconds' % (end - start))
    bufferPolygon['geometry'].apply(lambda row: returnCoor(row))
    res['coordinates'] = bufferPolygon['geometry'].apply(lambda row: returnCoor(row))
    maxVal = res['count'].max()
    maxVal = int(maxVal)
    res['color'] = res.apply(lambda row: color_scale(int(row['count']), maxVal, 0), axis=1)
    return res


def returnCoor(row):
    if row is not None:
        return row['coordinates']
    else:
        return [[[0, 0]]]


# bufferSHP(0.04,"Drop")
