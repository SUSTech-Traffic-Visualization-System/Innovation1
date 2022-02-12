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
import random


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

    creatShp.point("./shp/Point/point.shp", data)
    # 旧版本，未生成区域而是生成了线，用线围成了区域
    # for i in range(len(l1)):
    # path = "E:\\NEW TRY\\shp\\TaxiDBSCAN\\" + DoP + "\\line" + str(i) + ".shp"
    # creatShp.line(path, l1[i])

    # 新版本

    w = shapefile.Writer("./shp/Polygon/polygon.shp")
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
def run(data, labels):
    l1 = plotFeature(data, labels)
    shp(data, l1)


def creat_Shp(filename, radius, min_samples):
    # define the number of kilometers in one radian
    kms_per_radian = 6371.0088
    # load the data set
    df = pd.read_csv(filename, encoding='utf-8')
    df = df.sample(2500)
    df.head()
    x = df.loc[(df['latitude'] <= 40)].index
    df = df.drop(index=x)
    # represent points consistently as (lat, lon)
    coords = df[['latitude', 'longitude']]
    coords = coords.values

    # define epsilon as 1.5 kilometers, converted to radians for use by haversine
    epsilon = radius / kms_per_radian

    start_time = time.time()
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


def processing(pointfilename, datafilename):
    pd.set_option('display.max_columns', None)
    regionShape = gp.read_file('./shp/Polygon/Polygon.shp')  # .to_crs('EPSG:4326')
    regionShape['center'] = regionShape.centroid

    # data = pd.read_csv('DATA/yellow_tripdata_2014-01.csv',low_memory=False,nrows=1000)
    data = pd.read_csv(datafilename, encoding='utf-8')

    data[['longitude', 'latitude']] = data[['longitude', 'latitude']].apply(pd.to_numeric)
    gdata = gp.GeoDataFrame(data, geometry=gp.points_from_xy(data['longitude'], data['latitude']), crs='EPSG:4326')
    Result = gp.sjoin(gdata, regionShape, how='left')
    return Result, regionShape


def pTOl2(clusterFileName, PICKdatafilename, DROPdatafilename, radius, min_samples):
    creat_Shp(clusterFileName, radius=radius, min_samples=min_samples)
    p, region = processing(clusterFileName, PICKdatafilename)
    d, region = processing(clusterFileName, DROPdatafilename)

    result = pd.merge(p, d, left_index=True, right_index=True)
    result = result.dropna()
    result = result.reset_index(drop=True)

    tmp = pd.DataFrame(result)
    tmp2 = tmp.groupby(['index_right_x', 'index_right_y'], as_index=False).count()[
        ['index_right_x', 'index_right_y', 'time_x']]
    region = region['center']
    return region, tmp2


# a, b = pTOl2('pickUp', 'pickUp', 'dropOff')
print(0)
