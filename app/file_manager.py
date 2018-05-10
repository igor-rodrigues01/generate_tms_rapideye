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
from log2 import Log
from constants import (
    OUTSIZE_RGB, FILENAME_WITH_ALL_RAPIDEYE, TOTAL_PART, BAND_R, BAND_G,
    BAND_B, DIR_TMS, DIR_RGB, ZOOM_MIN, ZOOM_MAX, URL_TMS, DIR_TMS
)
from dao import DAO


class FileManager:

    def __init__(self):
        self.__dao = DAO()

    def __check_tif_and_metadata(self, abspath_image):
        """
        Method that check the existence of the useful files to processing.
        Are checked (image.tif) and the metadatas from image
        (image_metadata.xml).
        """
        tif = Utils.get_file(abspath_image, is_tif=True)
        metadata = Utils.get_file(abspath_image, is_metadata=True)

        if tif is False:
            Log.error(
                'O diretório {} está sem .tif'.format(abspath_image)
            )
            return False

        if metadata is False:
            Log.error(
                'O diretório {} está sem metadados'.format(abspath_image)
            )
            return False

        return True

    def get_cloud(self, abspath_dir_img):
        """
        This method will access metadata from image and will get the cloud
        cover percecentage.
        """
        metadata_xmlfile = Utils.get_file(
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
        tif = Utils.get_file(abspath_dir_img, is_tif=True)
        print('\nFazendo footprint.\n')
        MakeFootprint.footprint(tif, shp_out)
        print('\nRemovendo shp do footprint.\n')
        poly = MakeFootprint.shp_to_wkt(shp_out)
        poly = wkt.loads(poly)
        multipoly = MultiPolygon([poly])
        shutil.rmtree(shp_out)
        return multipoly.wkt

    def __make_tms(
        self, abspath_dir_img, num_br, num_bg, num_bb, dir_rgb, out_dir
    ):
        """
        Method that start tms generation
        """
        """
        ESTÁ SENDO INSERIDO // NO LINK
        """
        zoom_list = [ZOOM_MIN, ZOOM_MAX]
        tif = Utils.get_file(abspath_dir_img, is_tif=True)
        GenerateTMS.main(
            tif, num_br, num_bg, num_bb, dir_rgb, zoom_list, URL_TMS, out_dir
        )

    # CORRIGIR
    def __get_xml_tms(self, image_name, num_br, num_bg, num_bb, path_all_tms):
        # tms = "http://10.1.25.66/imagens/tms/rapideye/2328613_2011-09-20T140632_RE1_3A-NAC_10911835_148037_CR_r3g5b2_tms.xml"
        abs_path_tms = os.path.abspath(path_all_tms)
        http = 'http:'
        ip_current = socket.gethostbyname(socket.gethostname())
        img_rgb = '{}_r{}g{}b{}.xml'.format(
            image_name, num_br, num_bg, num_bb
        )
        path_img_rgb = os.path.join(abs_path_tms, img_rgb)
        return '{}//{}{}'.format(http, ip_current, path_img_rgb)

    def __get_image_rgb(self, image_name, num_br, num_bg, num_bb, dir_rgb):
        """
        Method that get image name from rgb image to add in the database
        """
        """
        ESTÁ INDO O TIFF TAMBÉM
        """
        # image = "2328613_2011-09-20T140632_RE1_3A-NAC_10911835_148037_CR_r3g5b2.tif"
        sufix_rgb = '_r{}g{}b{}.tif'.format(
            num_br, num_bg, num_bb
        )
        image_name += sufix_rgb
        abspath_image = os.path.abspath(os.path.join(dir_rgb, image_name))
        if os.path.exists(abspath_image):
            return abspath_image, image_name
        else:
            print('Image {} não encontrada'.format(image_name))

    def __get_path(self, abspath_dir_img):
        # path = "\\10.1.25.66\b52_imagens\rapideye\2328613_2011-09-20T140632_RE1_3A-NAC_10911835_148037_CR"
        """
        Method that return path to directory of the images
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

    def __get_date(self, abspath_dir_img):
        img_name = os.path.basename(abspath_dir_img)
        return img_name.split('_')[1]

    def __make_processing(
        self, img_name, num_br, num_bg, num_bb, dir_rgb, abspath_dir_img, dir_tms
    ):
        import random

        data = {}
        data['gid'] = random.randint(0, 10000)
        data['data'] = self.__get_date(abspath_dir_img)

        data['total_part'] = TOTAL_PART
        data['nuvens'] = self.get_cloud(abspath_dir_img)
        self.__make_tms(
            abspath_dir_img, num_br, num_bg, num_bb, dir_rgb, dir_tms
        )
        data['geom'] = self.__make_footprint(abspath_dir_img)
        data['tms'] = self.__get_xml_tms(
            img_name, num_br, num_bg, num_bb, dir_tms
        )
        abspath_rgb, img_name_rgb = self.__get_image_rgb(
            img_name, num_br, num_bg, num_bb, dir_rgb
        )
        data['image'] = img_name_rgb
        data['quicklook'] = self.__make_png(abspath_rgb)
        data['path'] = self.__get_path(abspath_dir_img)
        return data

    def main(
        self, path_4a_cobertura, num_br, num_bg, num_bb, dir_rgb, dir_tms
    ):
        all_rapideye = open(FILENAME_WITH_ALL_RAPIDEYE, 'r')
        i = 0

        for img_name in all_rapideye.readlines():
            path_dir_img = os.path.join(path_4a_cobertura, img_name)
            abspath_dir_img = os.path.abspath(path_dir_img.strip('\n'))
            i += 1

            if self.__check_tif_and_metadata(abspath_dir_img):
                data = self.__make_processing(
                    img_name.strip('\n'), num_br, num_bg,
                    num_bb, dir_rgb, abspath_dir_img, dir_tms
                )
                self.__dao.insert_catalog_rapideye(data)

                if i > 1:
                    break


if __name__ == '__main__':
    args = sys.argv
    args = Utils.make_params(args)
    process = FileManager()

    if not os.path.exists(DIR_RGB):
        os.mkdir(DIR_RGB)

    process.main(
        args['-imgPathIn'], BAND_R, BAND_G, BAND_B,
        DIR_RGB, DIR_TMS
    )

# args['-imgPathIn'], args['-br'], args['-bg'], args['-bb'],
# args['-imgPathOut'], zoom_list, args['-link'], args['-outDirTms']
