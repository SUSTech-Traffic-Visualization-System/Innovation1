import shapefile
from json import dumps


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


# trans('./shp/Polygon/Pick.shp')
