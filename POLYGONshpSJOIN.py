import json

import geopandas
import pandas as pd, numpy as np, matplotlib.pyplot as plt, time
import shapefile
from scipy.spatial import ConvexHull
from sklearn.cluster import DBSCAN
from sklearn import metrics
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
import CreatSHP as creatShp
import time
import geopandas as gp

import mapFrontCSV
import shpToJson as stj
import random


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


def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)


def plotFeature(data, labels_):
    clusterNum = len(set(labels_))
    fig = plt.figure()
    scatterColors = ['black', 'blue', 'green', 'yellow', 'red', 'purple', 'orange', 'brown']
    ax = fig.add_subplot(111)

    linelist = []

    for i in range(-1, clusterNum):
        colorSytle = scatterColors[i % len(scatterColors)]
        subCluster = data[np.where(labels_ == i)]
        ax.scatter(subCluster[:, 0], subCluster[:, 1], c=colorSytle, s=12)

        #凸包函数计算聚类完成的点集的边界，并将直线画出
        if i != -1 and len(subCluster) >= 3:
            point = np.array(subCluster)
            hull = ConvexHull(point)
            lll = []
            # for simplex in hull.simplices:
            #     plt.plot(point[simplex, 0], point[simplex, 1], 'k-', color=colorSytle, linewidth=1.5)
            #     lll.append([point[simplex, 0][0], point[simplex, 1][0], point[simplex, 0][1], point[simplex, 1][1]])
            for vertices in hull.vertices:
                lll.append([point[vertices][1], point[vertices][0]])
            linelist.append(lll)
    # plt.show()
    return linelist


def shp(data, l1):
    # path = "E:\\NEW TRY\\shp\\TaxiDBSCAN\\" + DoP  # 指定位置
    # if not os.path.exists(path):  # 如果目标位置 不存在该文件夹“任务集” ，则执行下面命令
    #     os.mkdir(path + str(hour))  # 创建一个新的文件夹 “任务集”，

    filename1 = 'Point'
    filename2 = 'Polygon'
    creatShp.point("./shp/Point/" + filename1 + ".shp", data)
    # 旧版本，未生成区域而是生成了线，用线围成了区域
    # for i in range(len(l1)):
    # path = "E:\\NEW TRY\\shp\\TaxiDBSCAN\\" + DoP + "\\line" + str(i) + ".shp"
    # creatShp.line(path, l1[i])

    # 新版本

    w = shapefile.Writer("./shp/Polygon/" + filename2 + ".shp")
    w.autoBalance = 1
    # w = shapefile.Writer(shapefile.POLYGON)
    w.field('FIRST_FLD', 'C', '40')
    w.field('SECOND_FLD', 'C', '40')
    for i in range(len(l1)):
        w.poly([l1[i]])
        w.record(i, 'Polygon')

    # w.poly([l1[0]])
    # w.field('FIRST_FLD', 'C', '40')
    # w.field('SECOND_FLD', 'C', '40')
    # w.record(0, 'Polygon')


# 加载数据

# data = np.loadtxt("test.csv", delimiter=",")
def run(data, labels):
    l1 = plotFeature(data, labels)
    shp(data, l1)


def Cluster(radius, min_samples, baseDataSamp, baseData, inData):
    filename1 = 'Point'
    filename2 = 'Polygon'
    latitude = 'latitude'
    longitude = 'longitude'
    # %matplotlib inline
    # define the number of kilometers in one radian
    global len
    kms_per_radian = 6371.0088
    # load the data set
    df = baseDataSamp
    # df.head()
    x = df.loc[(df[latitude] <= 40)].index
    df = df.drop(index=x)
    # represent points consistently as (lat, lon)
    # coords = df.as_matrix(columns=[' pickup_latitude', ' pickup_longitude'])
    coords = df[[latitude, longitude]]
    coords = coords.values

    # for i in coords:
    #     x = random.randint(40, 42)
    #     i[0] = x
    #     y = random.randint(-72, -70)
    #     i[1] = y
    # index = []
    # for i in range(len(coords1)):
    #     if coords1[i][0] == 0 or coords1[i][1] == 0:
    #         index.append(i)
    # coords = np.delete(coords1, index, 0)
    # for i in range(len(index)):

    # define epsilon as 1.5 kilometers, converted to radians for use by haversine
    epsilon = radius / kms_per_radian

    start_time = time.time()
    
    #通过DBSCAN算法对基数据进行聚类，生成对应点集
    db = DBSCAN(eps=epsilon, min_samples=min_samples, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    cluster_labels = db.labels_

    # get the number of clusters
    num_clusters = len(set(cluster_labels))

    # all done, print the outcome
    message = 'Clustered {:,} points down to {:,} clusters, for {:.1f}% compression in {:,.2f} seconds'
    print(message.format(len(df), num_clusters, 100 * (1 - float(num_clusters) / len(df)), time.time() - start_time))
    print('Silhouette coefficient: {:0.03f}'.format(metrics.silhouette_score(coords, cluster_labels)))

    x = [coords[cluster_labels == n] for n in range(num_clusters)]
    for i in x:
        print(i)
    # turn the clusters in to a pandas series, where each element is a cluster of points
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])

    # pull row from original data set where lat/lon match the lat/lon of each row of representative points
    # that way we get the full details like city, country, and date from the original dataframe
    run(coords, cluster_labels)

    # -------------------dataProcess2--------------------
    start = time.perf_counter()
    pd.set_option('display.max_columns', None)
    regionShape = gp.read_file('./shp/Polygon/' + filename2 + '.shp', crs='EPSG:4326')  # .to_crs('EPSG:4326')
    stj.trans('./shp/Polygon/' + filename2 + '.shp', 'cluster')
    # regionShape = gp.read_file('./POLYGON.shp', crs='EPSG:4326')

    length = regionShape.shape[0]

    # data = pd.read_csv('DATA/yellow_tripdata_2014-01.csv',low_memory=False,nrows=1000)
    # data = pd.read_csv('./DATA./yellow_tripdata_2014-01.csv', nrows=1000, encoding='utf-8')
    data = baseData

    data[[longitude, latitude]] = data[[longitude, latitude]].apply(
        pd.to_numeric)
    gdata = gp.GeoDataFrame(data, geometry=gp.points_from_xy(data[longitude], data[latitude]),
                            crs='EPSG:4326')
    # print(regionShape.head())
    # print('\n\n\n\n\n')
    Result = gp.sjoin(gdata, regionShape, how='left')

    Result = Result.dropna()
    raw_count = Result['index_right']
    count = []
    for j in range(length):
        count.append(0)
    for i in raw_count:
        count[int(i)] += 1
    resBase = pd.DataFrame()
    resBase['count'] = count
    # polygon = regionShape.geometry.to_json()
    # polygonDict = json.loads(polygon)
    # d = pd.DataFrame.from_dict(polygonDict, orient='index')
    # clusterShape = d.T
    # json_str = json.dumps(polygonDict, indent=2)
    # with open('./shp/Geojson/POLYGON.geojson', 'w') as json_file:
    #     json_file.write(json_str)
    clusterShape = pd.read_json('./shp/Geojson/cluster.geojson')
    resBase['coordinates'] = clusterShape['features'].apply(lambda row: row['geometry']['coordinates'])
    maxVal = resBase['count'].max()
    maxVal = int(maxVal)
    resBase['color'] = resBase.apply(lambda row: color_scale(int(row['count']), maxVal, 0), axis=1)
    scale = 5000.0 / maxVal
    resBase['count'] = resBase.apply(lambda row: int(row['count']) * scale + 10, axis=1)
    print(Result.head())
    #
    # ----------------------------------------------------------------------------------------
    # stj.trans('./shp/Polygon/' + filename2 + '.shp', 'cluster')
    # regionShape = gp.read_file('./POLYGON.shp', crs='EPSG:4326')

    length = regionShape.shape[0]

    # data = pd.read_csv('DATA/yellow_tripdata_2014-01.csv',low_memory=False,nrows=1000)
    # data = pd.read_csv('./DATA./yellow_tripdata_2014-01.csv', nrows=1000, encoding='utf-8')
    data = inData
    
    # 将聚类完成的结果数据转换为GeoDataFrame形式
    data[[longitude, latitude]] = data[[longitude, latitude]].apply(
        pd.to_numeric)
    gdata = gp.GeoDataFrame(data, geometry=gp.points_from_xy(data[longitude], data[latitude]),
                            crs='EPSG:4326')
    
    # 利用sjoin方法统计gdata中各个点分别属于哪个聚类当中，并将结果储存在Result中
    Result = gp.sjoin(gdata, regionShape, how='left')

    Result = Result.dropna()#将不属于聚类的点去除
    raw_count = Result['index_right']
    count = []
    for j in range(length):
        count.append(0)
    for i in raw_count:
        count[int(i)] += 1
    resIn = pd.DataFrame()
    resIn['count'] = count
    # polygon = regionShape.geometry.to_json()
    # polygonDict = json.loads(polygon)
    # d = pd.DataFrame.from_dict(polygonDict, orient='index')
    # clusterShape = d.T
    # json_str = json.dumps(polygonDict, indent=2)
    # with open('./shp/Geojson/POLYGON.geojson', 'w') as json_file:
    #     json_file.write(json_str)
    clusterShape = pd.read_json('./shp/Geojson/cluster.geojson')
    resIn['coordinates'] = clusterShape['features'].apply(lambda row: row['geometry']['coordinates'])
    maxVal = resIn['count'].max()
    maxVal = int(maxVal)
    resIn['color'] = resIn.apply(lambda row: color_scale(int(row['count']), maxVal, 1), axis=1)
    scale = 5000.0 / maxVal
    resIn['count'] = resIn.apply(lambda row: int(row['count']) * scale + 10, axis=1)
    resIn['count'] = resIn['count'] + resBase['count']
    print(Result.head())
    end = time.perf_counter()
    print('\n\nRunning Time for 2.2Gb Data: %s Seconds' % (end - start))
    return resBase, resIn

# Cluster(1.5, 1, "Pick")
