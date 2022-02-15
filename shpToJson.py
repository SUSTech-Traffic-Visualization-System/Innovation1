import shapefile
from json import dumps

# function: transform a given shape file into a json(geojson) file
# input: filepath: the relative or absolute path of the target .shp file
#        name: the name for output json(geojson) file
# return: void

def trans(filepath, name):
    reader = shapefile.Reader(filepath)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", geometry=geom, properties=atr))

    geojson = open("./shp/Geojson/"+name+".geojson", "w", encoding='utf-8')
    geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=4) + '\n')
    geojson.close()
