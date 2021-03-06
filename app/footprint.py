#!-*-coding:utf-8-*-

import sys
import os
import fiona
import json
import geojson
from shapely.geometry import shape
from osgeo import gdal


class MakeFootprint:

    @classmethod
    def footprint(cls, ds_path, shp_out_path):
        """
        Method that create a shp with footprint based in gdal with vrt's.
        """
        # Creating a dataset reprojected to 4674
        ds_reprojected = ds_path.replace('.tif', '_reprojected.tif')
        gdal.Warp(ds_reprojected, ds_path, dstSRS='EPSG:4674')

        ds_vrt = ds_reprojected.replace('.tif', '.vrt')
        ds_vr2 = ds_reprojected.replace(ds_reprojected[-4:], '_2.vrt')
        command1 = "gdal_translate -b mask -of vrt -a_nodata 0 {} {}".format(ds_reprojected, ds_vrt)
        command2 = "gdal_translate -b 1 -of vrt -a_nodata 0 {} {}".format(ds_vrt, ds_vr2)
        command3 = 'gdal_polygonize.py -q -8 {} -b 1 -f "ESRI Shapefile" {}'.format(ds_vr2, shp_out_path)
        os.system(command1)
        os.system(command2)
        os.system(command3)
        os.remove(ds_vrt)
        os.remove(ds_vr2)
        os.remove(ds_reprojected)

    @classmethod
    def __write_file(cls, content, filename='geo.wkt'):
        """
        Mehtod that create wkt file and write a content.
        """
        f = open('{}.wkt'.format(filename), 'w')
        f.write(content)
        f.close()

    @classmethod
    def shp_to_wkt(cls, shapefile_dir):
        """
        Method that get geometry from shp and write in wkt.
        """
        files_shapefiledir = os.listdir(shapefile_dir)
        shp = None

        for file in files_shapefiledir:
            if file.endswith('.shp'):
                shp = file

        shp = fiona.open(os.path.join(shapefile_dir, shp))
        data = shp.next()
        s = json.dumps(data['geometry'])
        g1 = geojson.loads(s)
        g2 = shape(g1)
        return g2.wkt

    @classmethod
    def generate_footprint_wkt(cls, ds_path, shp_out_path):
        """
        Method that generate a footprint and create file with a geometry
        of the shp.
        """
        cls.footprint(ds_path, shp_out_path)
        footprint_geom_wkt = cls.shp_to_wkt(shp_out_path)
        cls.__write_file(footprint_geom_wkt, shp_out_path)


def validate_params(args):
    """
    Method that will organize entry params in key and value
    """
    data = {}

    if len(args) > 7:
        sys.exit(MSG_ERROR)

    elif len(args) % 2 == 0:
        sys.exit(MSG_ERROR)

    elif len(args) < 5:
        sys.exit(MSG_ERROR)

    for i in range(len(args)):
        if i == 0:  # jumping the first interaction to the omit
            continue  # the filename footprint.py
        if not i % 2 == 0:
            data[args[i]] = args[i + 1]

    if '-footOut' not in data.keys() or '-imgIn' not in data.keys():
        sys.exit('Verifique se os parâmetros passados estão corretos!')

    return data


MSG_ERROR = 'Entre com a imagem de entrada e o shp de saída. Ex:\n' \
    'python3 footprint.py -imgIn img.tif -footOut myfoot \nou\n' \
    'python3 footprint.py -imgIn img.tif -footOut myfoot -wkt 1'


if __name__ == '__main__':
    args = sys.argv
    args = validate_params(args)

    if '-wkt' in args.keys():
        MakeFootprint.generate_footprint_wkt(
            args['-imgIn'], args['-footOut']
        )
        sys.exit()
    else:
        MakeFootprint.footprint(
            args['-imgIn'], args['-footOut']
        )
