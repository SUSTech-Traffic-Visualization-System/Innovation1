import os, re
import geopandas as gpd
import pandas as pd
from osgeo import ogr, osr, gdal  # osr用于获取坐标系统，ogr用于处理矢量文件

# 解决shp dbf 文件中文编码   选自自己想转的编码   常用的 gbk  gb2312  utf8
# gdal.SetConfigOption("SHAPE_ENCODING", "")
# gdal.SetConfigOption("SHAPE_ENCODING", "gb2312")
gdal.SetConfigOption("SHAPE_ENCODING", "gbk")


def point_csv_2_shp(csv_lyr, shp_fn):
    """
    point  转 shp
    """
    # os.chdir(os.path.dirname(path))  # 将path所在的目录设置为当前文件夹
    # ds = ogr.Open(path, 1)  # 1代表可读可写，默认为0
    # csv_lyr = ds.GetLayer()  # 获取csv文件
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)  # 定义坐标系统
    shp_driver = ogr.GetDriverByName('ESRI Shapefile')  # 获取shapefile文件处理句柄
    if os.path.exists(shp_fn):  # 如果文件夹中已存在同名文件则先删除
        shp_driver.DeleteDataSource(shp_fn)
    shp_ds = shp_driver.CreateDataSource(shp_fn)
    layer = shp_ds.CreateLayer(shp_fn, sr, ogr.wkbPoint)  # 创建一个点图层

    layer.CreateField(ogr.FieldDefn('id', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('ground_h', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('type', ogr.OFTString))

    for i in range(len(csv_lyr)):  # 对于csv文件中每一行
        point_feature = ogr.Feature(layer.GetLayerDefn())  # 创建一个点
        x = csv_lyr[i][0]  # csv中的坐标字段
        y = csv_lyr[i][1]  # csv中的坐标字段
        shp_pt = ogr.Geometry(ogr.wkbPoint)  # 创建几何点
        shp_pt.AddPoint(x, y)
        # 获取csv字段
        # # 为创建的shp文件字段赋值
        # point_feature.SetField('id', csv_row.GetFieldAsString('local_id'))  # GetFieldAsString  获取csv中的列名
        # point_feature.SetField('ground_h', csv_row.GetFieldAsString('ground_h'))
        # point_feature.SetField('type', csv_row.GetFieldAsString('dev_type'))

        point_feature.SetGeometry(shp_pt)  # 将点的几何数据添加到点中
        layer.CreateFeature(point_feature)  # 将点写入到图层中

    # del ds
    del shp_ds  # 释放句柄，文件缓冲到磁盘
    print("This process has succeeded!")


def line_csv_2_dbf(csv_lyr, shp_fn):
    """
    geometry坐标为 LineString坐标
    """
    # os.chdir(os.path.dirname(path))  # 将path所在的目录设置为当前文件夹
    # ds = ogr.Open(path, 1)  # 1代表可读可写，默认为0
    # csv_lyr = [[1, 1], [1, 2], [2, 2], [2, 1]]  # 获取csv文件
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)  # 定义坐标系统
    shp_driver = ogr.GetDriverByName('ESRI Shapefile')  # 获取shapefile文件处理句柄
    if os.path.exists(shp_fn):  # 如果文件夹中已存在同名文件则先删除
        shp_driver.DeleteDataSource(shp_fn)
    shp_ds = shp_driver.CreateDataSource(shp_fn)
    layer = shp_ds.CreateLayer(shp_fn, sr, ogr.wkbLineString)  # 创建多个点图层

    layer.CreateField(ogr.FieldDefn('id', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('l_id', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('u_id', ogr.OFTString))

    for i in range(len(csv_lyr)):  # 对于csv文件中每一行

        point_feature = ogr.Feature(layer.GetLayerDefn())
        x1 = csv_lyr[i][0]  # csv中的 x1坐标
        y1 = csv_lyr[i][1]  # y1坐标
        x2 = csv_lyr[i][2]  # x2坐标
        y2 = csv_lyr[i][3]  # y2坐标

        mult_coord = '(' + str(x1) + ' ' + str(y1) + ',' + str(x2) + ' ' + str(y2) + ')'
        # geom = ogr.CreateGeometryFromWkt('LINESTRING ' + '(2 1,0 1)')
        geom = ogr.CreateGeometryFromWkt('LINESTRING' + mult_coord)

        # # 获取csv字段
        # # 为创建的shp文件字段赋值
        # point_feature.SetField('id', csv_row.GetFieldAsString('gid'))  # GetFieldAsString  获取csv中的列名
        # point_feature.SetField('l_id', csv_row.GetFieldAsString('l_id'))
        # point_feature.SetField('u_id', csv_row.GetFieldAsString('u_id'))

        point_feature.SetGeometryDirectly(geom)
        layer.CreateFeature(point_feature)

    # del ds
    del shp_ds  # 释放句柄，文件缓冲到磁盘
    print("This process has succeeded!")


def read_shapefile(path):
    """
    测试转成的shp文件
    """
    df = gpd.read_file(path, encoding='gbk', rows=20)  # 转shp前的编码格式
    print(df)

def point(path,l):
    shp_fn = path  # 最终要得到的shp文件的文件名
    # path = 'E:\\NEW TRY\\line.csv'  # csv文件名称
    point_csv_2_shp(l, shp_fn=shp_fn)
def line(path,l):
    shp_fn = path  # 最终要得到的shp文件的文件名
    # path = 'E:\\NEW TRY\\line.csv'  # csv文件名称
    line_csv_2_dbf(l, shp_fn=shp_fn)


if __name__ == '__main__':
    '''线表转shp  以及读取测试'''
    shp_fn = "E:\\NEW TRY\\shp\\test\\gd.shp"  # 最终要得到的shp文件的文件名
    # path = 'E:\\NEW TRY\\line.csv'  # csv文件名称
    l = [[1, 1], [1, 2], [2, 2], [2, 1]]
    line_csv_2_dbf(l, shp_fn=shp_fn)
    # 读取测试转之后的结果
    read_shapefile('E:\\NEW TRY\\shp\\DBSCAN\\line0.shp')
    read_shapefile('E:\\NEW TRY\\shp\\DBSCAN\\point.shp')

    '''点表转shp  以及读取测试'''
    # shp_fn = "xnd.shp"
    # path = os.path.join(gis_excel_dir, 'point.csv')  # csv文件名称
    # point_csv_2_shp(path=path, shp_fn=shp_fn)
    # 读取测试转之后的结果
    # read_shapefile(path=os.path.join(gis_excel_dir, 'point.shp'))
