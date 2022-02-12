# Created by zyd on 2021/12/5 15:32.
import dash
import numpy as np
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash_extensions.enrich import MultiplexerTransform, DashProxy, Input, Output
import pydeck
import dash_deck as dd
import dash_uploader as du
import pandas as pd
# import geopandas as gpd
import json
import os
import threePoint as tp
import math

# import threePoint as tp
from preprocessing import gps2grid


if __name__ == '__main__':
    # lat = []
    # lon = []
    # xBNum = 1
    # yBNum = 1
    # fileUp = []
    # layerList = []
    # gridLayer = []
    # barLayer = []
    # barMap = []
    # csvData = []
    # barNP = []
    # has_changed = True
    # clickTime = -1
    # color_idx = 0
    # data_out = pd.read_csv('./data/pickUp.csv', parse_dates=['time'])
    # data_in = pd.read_csv('./data/dropOff.csv', parse_dates=['time'])
    # csvData.append(data_out[['time', 'longitude', 'latitude']].copy())
    # csvData.append(data_in[['time', 'longitude', 'latitude']].copy())
    # lat.append(40.7062855)
    # lon.append(-74.0315102)
    # lat.append(40.6937655)
    # lon.append(-73.9871323)
    # lat.append(40.7738362)
    # lon.append(-73.998595)
    # for data in csvData:
    #     Flow = gps2grid(data, lon[0], lat[0], lon[1], lat[1], lon[2], lat[2], xBNum, yBNum)
    #     Flow = Flow.flatten()
    #     print(Flow)
    # lst = np.zeros(31)
    # for i in range(31):
    #     lst[i] = i+1
    # print(lst)
    # options = [[(x, y) for y in range(0, 4)] for x in range(0, 5)]
    # arr = np.asarray(options)
    # print(options)
    # print(arr)
    # lst = []
    # for i in range(0,5):
    #     # temp = []
    #     for j in range(0,3):
    #         lst.append((i, j))
    #     # lst.append()
    # print(lst)
    # lst_new = [("("+str(x[0])+","+str(x[1])+")") for x in lst]
    # print(lst_new)
    # print(lst_new[0], type(lst_new[0]))
    # options = '231,234'
    # length = len(options)
    # value = options[1:length-1]
    # print(value)
    # val = value.split(',')
    # print(val)
    # a = int(val[0])
    # b = int(val[1])
    # print(a, b)
    # print(a+b)
    # lst = []
    # for i in range(1,32):
    #     for j in range(0, 24):
    #         lst.append('2014-1-'+str(i)+' '+str(j)+':00')
    # print(np.array(lst))
    data = pd.read_csv('./DataUploadStorage/csv/Hotels_Properties_Citywide.csv', encoding='gbk')
    print(data)
