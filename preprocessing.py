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
    # data = pd.read_csv(file, usecols=[2,3,6,7,10,11])
    data = d.copy()
    data.columns = ['time', 'longitude', 'latitude']
    print(dx, dy)
    data = data[(data['time'] >= '2014-01-01 00:00:00') & (data['time'] < '2014-02-01 00:00:00')]
    # data = data[(data['do_time'] >= '2014-01-01 00:00:00') & (data['do_time'] < '2014-02-01 00:00:00')]
    data['date'] = data['time'].dt.day - 1
    # data['d_date'] = data['do_time'].dt.day - 1
    data['hour'] = data['time'].dt.hour
    # data['d_hour'] = data['do_time'].dt.hour
    data['time'] = data['date'] * 24 + data['hour']
    # data['d_time'] = data['d_date'] * 24 + data['d_hour']
    data['lat_tr'], data['lon_tr'] = coordinate_conversion(data[['latitude', 'longitude']].values, orlon, orlat, rblon,
                                                           rblat, lulon, lulat)
    # data['do_lat_tr'], data['do_lon_tr'] = coordinate_conversion(data[['do_lat', 'do_lon']].values, orlon, orlat, rblon,
    #                                                              rblat, lulon, lulat)
    data['lat_tr'] //= (1.0 / dx)
    # data['lat_tr'] //= (1.0 / dx)
    data['lon_tr'] //= (1.0 / dy)
    # data['do_lon_tr'] //= (1.0 / dy)
    data = data[(data['lat_tr'] >= 0) & (data['lat_tr'] < dx) &
                # (data['do_lat_tr'] >= 0) & (data['do_lat_tr'] < dx) &
                (data['lon_tr'] >= 0) & (data['lon_tr'] < dy)]
    # (data['do_lon_tr'] >= 0) & (data['do_lon_tr'] < dy)]
    data['grid'] = data['lat_tr'] + data['lon_tr'] * dx
    # data['d_grid'] = data['do_lat_tr'] + data['do_lon_tr'] * dx
    # inflow = data.groupby(['d_time', 'd_grid']).size().reset_index(name='inflow')
    # print('inflow:  ', inflow)
    Flow = data.groupby(['time', 'grid']).size().reset_index(name='Flow')
    print('Flow:  ', Flow)
    # od = data.groupby(['time', 'grid', 'grid']).size().reset_index(name='od')
    # od['ss_id'] = (od['o_grid'] * dx * dy) + od['d_grid']

    # inflow_np = ss.csr_matrix((inflow['inflow'], (inflow['d_time'], inflow['d_grid'].astype(int))),
    #                           shape=(744, (dx * dy))).toarray().reshape((744, dy, dx))
    Flow_np = ss.csr_matrix((Flow['Flow'], (Flow['time'], Flow['grid'].astype(int))),
                            shape=(744, (dx * dy))).toarray().reshape((744, dy, dx))
    # od_np = ss.csr_matrix((od['od'], (od['o_time'], od['ss_id'].astype(int))),
    #                       shape=(744, (dx * dy) * (dx * dy))).toarray().reshape((744, (dx * dy), (dx * dy)))

    # inflow_np_ = ss.csr_matrix((inflow['inflow'], (inflow['d_time'], inflow['d_grid'].astype(int))),
    #                            shape=(744, (dx * dy))).toarray()
    # Flow_np_ = ss.csr_matrix((Flow['outflow'], (Flow['time'], Flow['grid'].astype(int))),
    #                          shape=(744, (dx * dy))).toarray()

    np.save('inflow.npy', Flow_np)
    # np.save('outflow.npy', outflow_np)
    # np.save('od.npy', od_np)

    # np.savetxt('inflow.csv', Flow_np_, delimiter=",")
    # np.savetxt('outflow.csv', outflow_np_, delimiter=",")
    # np.savetxt('od.csv', od_np, delimiter=",")
    print("shape\n", Flow_np.shape)
    return Flow_np



