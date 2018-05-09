#!-*-coding:utf-8-*-
import os
import sys
import xmltodict
import shutil
import socket


from footprint import MakeFootprint
from generate_tms import GenerateTMS
from shapely.geometry.multipolygon import MultiPolygon
from shapely import wkt
from utils import Utils
from log import Log
from constants import OUTSIZE_RGB, FILENAME_WITH_ALL_RAPIDEYE, TOTAL_PART
from dao import DAO
from collections import defaultdict


class FileManager:

    __utils = None
    __log = None

    def __init__(self):
        self.__utils = Utils()
        self.__log = Log()
        self.__dao = DAO()

    def __check_tif_and_metadata(self, abspath_image):
        """
        Method that check the existence of the useful files to processing.
        Are checked (image.tif) and the metadatas from image
        (image_metadata.xml).
        """
        tif = self.__utils.get_file(abspath_image, is_tif=True)
        metadata = self.__utils.get_file(abspath_image, is_metadata=True)

        if tif is False:
            self.__log.error(
                'O diretório {} está sem .tif'.format(abspath_image)
            )
            return False

        if metadata is False:
            self.__log.error(
                'O diretório {} está sem metadados'.format(abspath_image)
            )
            return False

        return True

    def get_cloud(self, abspath_dir_img):
        """
        This method will access metadata from image and will get the cloud
        cover percecentage.
        """
        metadata_xmlfile = self.__utils.get_file(
            abspath_dir_img, is_metadata=True
        )
        cloud_percentage = None

        with open(metadata_xmlfile) as metadata:
            metadata_dict = xmltodict.parse(metadata.read())
            cloud_percentage = metadata_dict[
                're:EarthObservation'
            ]['gml:resultOf']['re:EarthObservationResult'][
                'opt:cloudCoverPercentage'
            ]['#text']

        return cloud_percentage

    def __make_footprint(self, abspath_dir_img, shp_out='teste-foot'):
        """
        Method that create the footprint from tif
        """
        tif = self.__utils.get_file(abspath_dir_img, is_tif=True)
        print('\nFazendo footprint.\n')
        MakeFootprint.footprint(tif, shp_out)
        print('\nRemovendo shp do footprint.\n')
        poly = MakeFootprint.shp_to_wkt(shp_out)
        poly = wkt.loads(poly)
        multipoly = MultiPolygon([poly])
        # import pdb; pdb.set_trace()
        shutil.rmtree(shp_out)
        return multipoly.wkt

    def __make_tms(
        self, abspath_dir_img, num_band_red=3, num_band_green=2,
        num_band_blue=1, zoom_list=[2, 15], out_dir_rgb='.',
        link_base='teste.com.br', output_folder='tms'
    ):
        """
        Method that start tms generation
        """
        tif = self.__utils.get_file(abspath_dir_img, is_tif=True)
        link_base = os.path.abspath(output_folder)
        GenerateTMS.main(
            tif, num_band_red, num_band_green, num_band_blue,
            out_dir_rgb, zoom_list, link_base, output_folder
        )

    # CORRIGIR
    def __get_xml_tms(
        self, image_name, num_band_red, num_band_green,
        num_band_blue, path_all_tms
    ):
        # tms = "http://10.1.25.66/imagens/tms/rapideye/2328613_2011-09-20T140632_RE1_3A-NAC_10911835_148037_CR_r3g5b2_tms.xml"
        abs_path_tms = os.path.abspath(path_all_tms)
        http = 'http:'
        ip_current = socket.gethostbyname(socket.gethostname())
        img_rgb = '{}_r{}g{}b{}.xml'.format(
            image_name, num_band_red, num_band_green, num_band_blue
        )
        path_img_rgb = os.path.join(abs_path_tms, img_rgb)
        return '{}//{}{}'.format(http, ip_current, path_img_rgb)

    def __get_image_rgb(
        self, image_name, num_band_red, num_band_green,
        num_band_blue, out_dir_rgb
    ):
        """
        Method that get image name from rgb image to add in the database
        """
        # image = "2328613_2011-09-20T140632_RE1_3A-NAC_10911835_148037_CR_r3g5b2.tif"
        sufix_rgb = '_r{}g{}b{}.tif'.format(
            num_band_red, num_band_green, num_band_blue
        )
        image_name += sufix_rgb
        abspath_image = os.path.abspath(os.path.join(out_dir_rgb, image_name))
        if os.path.exists(abspath_image):
            return abspath_image, image_name
        else:
            print('Image {} não encontrada'.format(image_name))

    def __get_path(self, abspath_dir_img):
        # path = "\\10.1.25.66\b52_imagens\rapideye\2328613_2011-09-20T140632_RE1_3A-NAC_10911835_148037_CR"
        """
        Method that return path to directory of the images
        """
        """
        ARRRUMAR CONTRA BARRA
        """
        ip_current = socket.gethostbyname(socket.gethostname())
        abspath_dir_img = abspath_dir_img.replace('/', "\\")
        return '\\\\{}{}'.format(ip_current, abspath_dir_img)

    def __make_png(self, abspath_img_rgb):
        """
        Function that create png image from rgb
        """
        # quicklook = "http://10.1.25.66/imagens/png/rapideye/2328613_2014-02-10T140451_RE3_3A-NAC_18111582_241547_CR_r3g5b2.png"
        outsize = '{}%'.format(OUTSIZE_RGB)
        abspath_img_png = abspath_img_rgb.replace('.tif', '.png')

        command = "gdal_translate -ot byte -of PNG -outsize {} {} " \
            "-a_nodata 0 -q  {} {}".format(
                outsize, outsize, abspath_img_rgb, abspath_img_png
            )
        os.system(command)
        return abspath_img_png

    def __make_processing(
        self, img_name, num_band_red, num_band_green, num_band_blue,
        out_dir_rgb, abspath_dir_img, out_dir_tms='tms'
    ):
        import random
        import datetime

        data = {}
        data['gid'] = random.randint(0, 10000)
        data['data'] = datetime.datetime.now().strftime('%Y-%m-%d') 

        data['total_part'] = TOTAL_PART
        data['nuvens'] = self.get_cloud(abspath_dir_img)
        self.__make_tms(
            abspath_dir_img, num_band_red=num_band_red,
            num_band_green=num_band_green, num_band_blue=num_band_blue,
            out_dir_rgb=out_dir_rgb, output_folder=out_dir_tms
        )
        data['geom'] = self.__make_footprint(abspath_dir_img)
        data['tms'] = self.__get_xml_tms(
            img_name, num_band_red, num_band_green, num_band_blue,
            out_dir_tms
        )
        abspath_rgb, img_name_rgb = self.__get_image_rgb(
            img_name.strip('\n'), num_band_red, num_band_green,
            num_band_blue, out_dir_rgb
        )
        data['image'] = img_name_rgb
        data['quicklook'] = self.__make_png(abspath_rgb)
        data['path'] = self.__get_path(abspath_dir_img)
        return data

    def main(
        self, path_4a_cobertura, num_band_red, num_band_green,
        num_band_blue, out_dir_rgb, out_dir_tms='tms'
    ):
        all_rapideye = open(FILENAME_WITH_ALL_RAPIDEYE, 'r')
        i = 0

        for img_name in all_rapideye.readlines():
            data = {}
            path_dir_img = os.path.join(
                path_4a_cobertura, img_name.strip('\n')
            )
            abspath_dir_img = os.path.abspath(path_dir_img)
            i += 1

            if self.__check_tif_and_metadata(abspath_dir_img):
                data = self.__make_processing(
                    img_name, num_band_red, num_band_green, num_band_blue,
                    out_dir_rgb, abspath_dir_img, out_dir_tms
                )
                self.__dao.insert_catalog_rapideye(data)

                if i > 1:
                    break


if __name__ == '__main__':
    args = sys.argv
    args = Utils.make_params(args)
    process = FileManager()

    # args['-imgPathIn'], args['-br'], args['-bg'], args['-bb'],
    # args['-imgPathOut'], zoom_list, args['-link'], args['-outDirTms']
    if not os.path.exists(args['-outDirRgb']):
        os.mkdir(os.path.abspath(args['-outDirRgb']))

    process.main(
        args['-imgPathIn'], args['-br'], args['-bg'], args['-bb'],
        args['-outDirRgb'], args['-outDirTms']
    )
