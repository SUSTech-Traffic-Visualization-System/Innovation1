import json

import pandas as pd, numpy as np, matplotlib.pyplot as plt, time
import pydeck as pdk
import time
import geopandas as gp


def color_scale(val, maxVal, color_idx):
    per = 1.0 * val / maxVal
    if color_idx % 2 == 0:
        R = 255
        G = int((1 - per) * (244 - 31) + 31)
        B = 30
    elif color_idx % 2 == 1:
        R = 31
        G = int((1 - per) * (255 - 34) + 34)
        B = 255
    else:
        R = 125
        G = 125
        B = 125
    return [R, G, B]


def getCoord(a, b):
    ans = []
    b['index'].apply(pd.to_numeric)
    for i in a:
        for j in b['index']:
            if int(i) == int(j['index']):
                ans.append(j['geometry']["coordinates"])
    return ans


def Point2Polygon(file, pointFile):
    latitude = 'latitude'
    longitude = 'longitude'
    stack = []
    regionShape = gp.read_file(file).reset_index(inplace=False)  # .to_crs('EPSG:4326')
    # for each in regionShape['geometry']:
    #     print(each.is_valid)
    idx = 0
    d = json.load(open(file))
    region = pd.DataFrame(d["features"]).reset_index(inplace=False)
    for i in range(region.shape[0]):
        stack.append(0)
    length = regionShape.shape[0]
    result = []
    # data = pd.read_csv('DATA/yellow_tripdata_2014-01.csv',low_memory=False,nrows=1000)

    data = pd.read_csv(pointFile, encoding='utf-8', parse_dates=['time'])
    data[[longitude, latitude]] = data[[longitude, latitude]].apply(
        pd.to_numeric)
    data = data[['time', longitude, latitude]].copy()
    gdata = gp.GeoDataFrame(data, geometry=gp.points_from_xy(data[longitude], data[latitude]),
                            crs='EPSG:4326')
        # print(regionShape.head())
        # print('\n\n\n\n\n')
    tmp = gp.sjoin(gdata, regionShape, how='right').reset_index(inplace=False)
    tmp1 = pd.DataFrame(tmp).groupby(['index'], as_index=False).count()[['index', 'time']]
    maxVal = tmp1['time'].max()
    tmp1['color'] = tmp1.apply((lambda row: color_scale(int(row['time']), maxVal, idx)), axis=1)
    color = tmp1['color'].to_list()
    # tmp['geometry'] = regionShape['geometry']
    tmp1['geometry'] = region['geometry'].apply(lambda row: returnCoor(row))
    scale = 5000.0 / maxVal
    tmp1['time'] = tmp1.apply((lambda row: int(row['time']) * scale + 10), axis=1)
    for j in range(len(stack)):
        stack[j] += int(tmp1.iloc[j, 1])
    tmp1['count'] = tmp1.apply((lambda row: stack[int(row['index'])]), axis=1)
    ptr = 0
    for each in d['features']:
        each['count'] = stack[ptr]
        each['color'] = color[ptr]
        ptr += 1
    idx += 1
    result.append(
        tmp1
    )
    print(0)
    return d


def returnCoor(row):
    if row is not None:
        return row['coordinates']
    else:
        return [[[0, 0]]]
# Point2Polygon('./DataUploadStorage/geojson/region2.geojson', ['./pickUpSmall.csv'])
