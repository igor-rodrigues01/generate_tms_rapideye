#!-*-coding:utf-8-*-

import sys
import os
import fiona
import json
import geojson
# from shapely.geometry.multipolygon import MultiPolygon
# from shapely import wkt
from shapely.geometry import shape

"""
 - gerar apenas footprint
 python footprint.py -imgIn 2032526_2014-07-31_RE4_3A_315082_CR_r3g2b1.tif -footOut myfoot

 - gerar footprint e wkt
 python footprint.py -imgIn 2032526_2014-07-31_RE4_3A_315082_CR_r3g2b1.tif -footOut myfoot -wkt 1

- FAZER VALIDAÇÃO DE PARAMETROS DE ENTRADA
"""


class MakeFootprint:

    @classmethod
    def footprint(cls, ds_path, shp_out_path):
        """
        Method that create a shp with footprint based in gdal with vrt's.
        """
        ds_vrt = ds_path.replace('.tif', '.vrt')
        ds_vr2 = ds_vrt.replace(ds_vrt[:-4], '_2.vrt')
        # -a_srs EPSG:4674
        command1 = "gdal_translate -b mask -of vrt -a_nodata 0 {} {}".format(ds_path, ds_vrt)
        command2 = "gdal_translate -b 1 -of vrt -a_nodata 0 {} {}".format(ds_vrt, ds_vr2)
        command3 = 'gdal_polygonize.py -q -8 {} -b 1 -f "ESRI Shapefile" {}'.format(ds_vr2, shp_out_path)
        os.system(command1)
        os.system(command2)
        os.system(command3)
        os.remove(ds_vrt)
        os.remove(ds_vr2)

    @classmethod
    def __write_file(cls, content, filename='geo.wkt'):
        """
        Mehtod that create wkt file and write a content.
        """
        f = open('{}.wkt'.format(filename), 'w')
        f.write(content)
        f.close()

    @classmethod
    def __shp_to_wkt(cls, shapefile_dir):
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
        # polygon = wkt.loads(g2.wkt)
        # m_polygon = MultiPolygon([polygon])
        cls.__write_file(g2.wkt, shapefile_dir)

    @classmethod
    def generate_footprint_wkt(cls, ds_path, shp_out_path):
        """
        Method that generate a footprint and create file with a geometry
        of the shp.
        """
        cls.footprint(ds_path, shp_out_path)
        cls.__shp_to_wkt(shp_out_path)


def make_params(args):
    data = {}
    for i in range(len(args)):
        if i == 0:  # saltando a primeira iteracao pra
            # saltar o parametro que é o nome do arquivo de execução
            continue
        if not i % 2 == 0:
            data[args[i]] = args[i + 1]
    return data


if __name__ == '__main__':
    args = sys.argv
    # if args > 6:
    #     sys.exit('entre com a imagem de entrada e o shp de saída')

    args = make_params(args)
    if '-wkt' in args.keys():
        MakeFootprint.generate_footprint_wkt(
            args['-imgIn'], args['-footOut']
        )
        sys.exit()
    else:
        MakeFootprint.footprint(
            args['-imgIn'], args['-footOut']
        )

# insert into ibama.img_catalogo_rapideye_a
#     (gid, path, image, "data", tms, quicklook, geom, nuvens, total_part)
# values(
#    3, 'abc.com', 'img123', '2016-12-01', 'img.tms', 'qicklook',
#    ST_GeomFromText('MULTIPOLYGON (((763500 8440500, 788500 8440500, 788500 8415500, 763500 8415500, 763500 8440500)))', 4674),
#   1.5,1)
