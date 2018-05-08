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


class FileManager:

    @classmethod
    def get_cloud(cls, abspath_dir_img):
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

    @classmethod
    def __make_footprint(cls, abspath_dir_img, shp_out='teste-foot'):
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

    @classmethod
    def __make_tms(
        cls, abspath_dir_img, num_band_red=3, num_band_green=2,
        num_band_blue=1, zoom_list=[2, 15], out_dir_rgb='.',
        link_base='teste.com.br', output_folder='tms'
    ):
        """
        Method that start tms generation
        """
        tif = Utils.get_file(abspath_dir_img, is_tif=True)
        link_base = os.path.basename(tif)
        GenerateTMS.main(
            tif, num_band_red, num_band_green, num_band_blue,
            out_dir_rgb, zoom_list, link_base, output_folder
        )

    @classmethod
    def __get_xml_tms(
        cls, image_name, num_band_red, num_band_green,
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

    @classmethod
    def __get_image_rgb(
        cls, image_name, num_band_red, num_band_green,
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
            return image_name
        else:
            print('Image {} não encontrada'.format(image_name))

    @classmethod
    def __get_path(cls, abspath_dir_img):
        # path = "\\10.1.25.66\b52_imagens\rapideye\2328613_2011-09-20T140632_RE1_3A-NAC_10911835_148037_CR"
        """
        Method that return path to directory of the images
        """
        """
        ARRRUMAR CONTRA BARRA
        """
        ip_current = socket.gethostbyname(socket.gethostname())
        abspath_dir_img = abspath_dir_img.replace('/', "\\")
        return '\\{}{}'.format(ip_current, abspath_dir_img)

    @classmethod
    def __get_quicklook(cls):
        # quicklook = "http://10.1.25.66/imagens/png/rapideye/2328613_2014-02-10T140451_RE3_3A-NAC_18111582_241547_CR_r3g5b2.png"
        pass

    @classmethod
    def main(
        cls, path_4a_cobertura, num_band_red, num_band_green,
        num_band_blue, out_dir_rgb, out_dir_tms='tms'
    ):
        data = {}
        all_rapideye = open(Utils.FILENAME_WITH_ALL_RAPIDEYE, 'r')
        data['total_part'] = Utils.TOTAL_PART

        for img_name in all_rapideye.readlines():
            path_dir_img = os.path.join(
                path_4a_cobertura, img_name.strip('\n')
            )
            abspath_dir_img = os.path.abspath(path_dir_img)
            data['cloud'] = cls.get_cloud(abspath_dir_img)
            cls.__make_tms(
                abspath_dir_img, num_band_red=num_band_red,
                num_band_green=num_band_green, num_band_blue=num_band_blue,
                out_dir_rgb=out_dir_rgb, output_folder=out_dir_tms
            )
            data['geom'] = cls.__make_footprint(abspath_dir_img)
            data['tms'] = cls.__get_xml_tms(
                img_name, num_band_red, num_band_green, num_band_blue,
                out_dir_tms
            )
            data['image'] = cls.__get_image_rgb(
                img_name.strip('\n'), num_band_red, num_band_green,
                num_band_blue, out_dir_rgb
            )
            data['path'] = cls.__get_path(abspath_dir_img)
            # remove break
            break


if __name__ == '__main__':
    args = sys.argv
    args = Utils.make_params(args)

    # args['-imgPathIn'], args['-br'], args['-bg'], args['-bb'],
    # args['-imgPathOut'], zoom_list, args['-link'], args['-outDirTms']
    if not os.path.exists(args['-outDirRgb']):
        os.mkdir(os.path.abspath(args['-outDirRgb']))

    FileManager.main(
        args['-imgPathIn'], args['-br'], args['-bg'], args['-bb'],
        args['-outDirRgb'], args['-outDirTms']
    )
