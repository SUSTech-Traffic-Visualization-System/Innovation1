# -*- coding: utf-8 -*-
'''
@Time    : 2021/10/4 15:39
@Author  : Zekun Cai
@File    : preprocessing.py
@Software: PyCharm
'''
import pandas as pd
import numpy as np
import scipy.sparse as ss

origin_longitude = -73.9985950
origin_latitude = 40.7738362
top_right_longitude = -73.9541783
top_right_latitude = 40.7613036
bottom_left_longitude = -74.0315102
bottom_left_latitude = 40.7062855
dlat = 1 / 8
dlon = 1 / 16


def coordinate_conversion(coor,
                          orlon=origin_longitude,
                          orlat=origin_latitude,
                          xlon=top_right_longitude,
                          xlat=top_right_latitude,
                          ylon=bottom_left_longitude,
                          ylat=bottom_left_latitude):
    origin = np.array((orlat, orlon))
    b1 = np.array([xlat, xlon]) - origin
    b2 = np.array([ylat, ylon]) - origin
    B = np.array([b1, b2])

    vec = coor - origin
    result = np.matmul(vec, np.linalg.inv(B))
    return result[:, 0], result[:, 1]


def gps2grid(d: pd.DataFrame, orlon, orlat, rblon, rblat, lulon, lulat, dx, dy):
    data = d.copy()
    data.columns = ['time', 'longitude', 'latitude']
    print(dx, dy)
    data = data[(data['time'] >= '2014-01-01 00:00:00') & (data['time'] < '2014-02-01 00:00:00')]

    data['date'] = data['time'].dt.day - 1

    data['hour'] = data['time'].dt.hour

    data['time'] = data['date'] * 24 + data['hour']

    data['lat_tr'], data['lon_tr'] = coordinate_conversion(data[['latitude', 'longitude']].values, orlon, orlat, rblon,
                                                           rblat, lulon, lulat)

    data['lat_tr'] //= (1.0 / dx)

    data['lon_tr'] //= (1.0 / dy)

    data = data[(data['lat_tr'] >= 0) & (data['lat_tr'] < dx) &

                (data['lon_tr'] >= 0) & (data['lon_tr'] < dy)]

    data['grid'] = data['lat_tr'] + data['lon_tr'] * dx

    # Flow = data.groupby(['time', 'grid']).size().reset_index(name='Flow')
    return data
    # print('Flow:  ', Flow)
    #
    # Flow_np = ss.csr_matrix((Flow['Flow'], (Flow['time'], Flow['grid'].astype(int))),
    #                         shape=(744, (dx * dy))).toarray().reshape((744, dy, dx))
    #
    # np.save('inflow.npy', Flow_np)
    #
    # print("shape\n", Flow_np.shape)
    # return Flow_np



def preprocessingB(origin,up,down,dx,dy,file1, file2):
    # dx = 8
    # dy = 16
    global length
    Dx = 1 / dx
    Dy = 1 / dy
    #
    # origin = (40.7062855, -74.0315102)
    # up = (40.6937655, -73.9871323)
    # down = (40.7738362, -73.9985950)

    # dx = 4
    # dy = 2
    # Dx = 1 / 4
    # Dy = 1 / 2

    # origin = (0, 0)
    # up = (0, 4)
    # down = (8, 0)

    data = pd.read_csv(file1, encoding='utf-8', parse_dates=['time'])
    df = data[['time', 'longitude', 'latitude']].copy()
    pFlow = gps2grid(df, -74.0315102, 40.7062855, -73.9871323, 40.6937655, -73.9985950, 40.7738362, 8, 16)
    data = pd.read_csv(file2, encoding='utf-8', parse_dates=['time'])
    df = data[['time', 'longitude', 'latitude']].copy()
    dFlow = gps2grid(df, -74.0315102, 40.7062855, -73.9871323, 40.6937655, -73.9985950, 40.7738362, 8, 16)

    #res = pFlow.append(dFlow)
    result = pd.merge(pFlow,dFlow,left_index=True,right_index=True)
    result = result.reset_index(drop=True)

    ans = []
    for i in range(dy):
        for j in range(dx):

            vertices1 = [origin[0] + (down[0] - origin[0]) * Dx * j + (up[0] - origin[0]) * Dy * i,
                         origin[1] + (down[1] - origin[1]) * Dx * j + (up[1] - origin[1]) * Dy * i]

            vertices2 = [origin[0] + (down[0] - origin[0]) * Dx * (j + 1) + (up[0] - origin[0]) * Dy * (i + 1),
                         origin[1] + (down[1] - origin[1]) * Dx * (j + 1) + (up[1] - origin[1]) * Dy * (i + 1)]

            center = [(vertices2[0] + vertices1[0])/2, (vertices2[1] + vertices1[1])/2]
            ans.append(center)

    length = len(ans)

    result = result.dropna()
    result = result.reset_index(drop=True)
    #
    # indexFrom = result['grid_x']
    # indexTo = result['grid_y']
    #
    # count = np.zeros((len, len))
    #
    # for i in range(indexTo.shape[0]):
    #     x = int(indexFrom[i])
    #     y = int(indexTo[i])
    #     count[x][y] += 1
    #
    # DF = pd.DataFrame(count)

    tmp = pd.DataFrame(result)
    tmp2 = tmp.groupby(['grid_x', 'grid_y'], as_index=False).count()[['grid_x', 'grid_y', 'time_x']]
    return ans, tmp2


# a, b = preprocessingB((40.7062855, -74.0315102),(40.6937655, -73.9871323),(40.7738362, -73.9985950),8,16)
print()

