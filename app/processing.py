#!-*-coding:utf-8-*-
import os
import sys
import shutil

from footprint import MakeFootprint
from generate_tms import GenerateTMS
from shapely.geometry.multipolygon import MultiPolygon
from shapely import wkt
from utils import Utils
from validator import Validator
from log import Log
from constants import (
    OUTSIZE_RGB, FILE_ALL_RAPIDEYE, TOTAL_PART, BAND_R, BAND_G, BAND_B,
    DIR_PNG, DIR_TMS, ZOOM_MIN, ZOOM_MAX, URL_TMS, DESTINY_RAPIDEYE,
    DIR_PNG_TO_DB
)
from dao import DAO
from datetime import datetime
from prepare_threads import PrepareThreads
from image_info import ImageInfo
"""
Possible Params:
    -thr / -oneImg / -dirImgs / -move
"""


class Processing:

    def __init__(self, process_one_img_bool, log_obj):
        self.__log = log_obj
        self.__dao = DAO(log=self.__log)

    def __make_footprint(self, abspath_dir_img, shp_out='teste-foot'):
        """Method that create the footprint from tif"""
        tif = Utils.get_file(abspath_dir_img, is_tif=True)
        print('\nGerando footprint.\n')
        MakeFootprint.footprint(tif, shp_out)
        print('\nRemovendo shapefile do footprint.\n')
        poly = MakeFootprint.shp_to_wkt(shp_out)
        poly = wkt.loads(poly)
        multipoly = MultiPolygon([poly])
        shutil.rmtree(shp_out)
        return multipoly.wkt

    def __make_tms(self, abspath_dir_img):
        """Method that start tms generation."""
        zoom_list = [ZOOM_MIN, ZOOM_MAX]
        tif = Utils.get_file(abspath_dir_img, is_tif=True)
        GenerateTMS.main(
            tif, BAND_R, BAND_G, BAND_B, abspath_dir_img, zoom_list,
            URL_TMS, DIR_TMS
        )

    def __make_png(self, abspath_img_rgb):
        """Method that create png image from RGB."""
        if not os.path.exists(DIR_PNG):
            os.makedirs(DIR_PNG)

        outsize = '{}%'.format(OUTSIZE_RGB)
        img_name_rgb = os.path.basename(abspath_img_rgb)
        suffix_extension_tif = Utils.get_suffix_tif(img_name_rgb)
        img_png = img_name_rgb.replace(suffix_extension_tif, '.png')
        path_img_png = os.path.join(DIR_PNG, img_png)

        command = "gdal_translate -ot byte -of PNG -outsize {} {} " \
            "-a_nodata 0 -q  {} {}".format(
                outsize, outsize, abspath_img_rgb, path_img_png
            )
        os.system(command)
        return os.path.join(DIR_PNG_TO_DB, img_png)

    def __make_processing(self, img_name, abspath_dir_img, id_foot):
        """
        Method that call other methods to perform all the necessary
        processings in the imagery.
        """
        data = {}
        data['data'] = ImageInfo.get_date(abspath_dir_img)
        data['total_part'] = TOTAL_PART
        data['nuvens'] = ImageInfo.get_cloud(abspath_dir_img)
        self.__make_tms(abspath_dir_img)
        data['geom'] = self.__make_footprint(abspath_dir_img, shp_out=id_foot)
        abspath_rgb, img_name_rgb = ImageInfo.get_image_rgb(
            abspath_dir_img, img_name
        )
        data['tms'] = ImageInfo.get_xml_tms(img_name_rgb)
        data['image'] = img_name_rgb
        data['quicklook'] = self.__make_png(abspath_rgb)
        data['path'] = ImageInfo.get_path(img_name)
        return data

    def make_processing_one_image(self, abspath_image, move_img_bool):
        """Method that make the processing in one image"""
        start_time = datetime.now().replace(microsecond=0)
        abspath_image = abspath_image.rstrip('/')
        img_name = os.path.basename(abspath_image)

        if Utils.check_tif_and_metadata(abspath_image, log_obj=self.__log):
            try:
                data = self.__make_processing(
                    img_name, abspath_image, 'foot_1'
                )
            except Exception as ex:
                self.__log.error(
                    '\nErro ao processar a imagem {} (Inserção '
                    'em banco interrompida)\n{}\n'.format(abspath_image, ex)
                )
            else:
                self.__dao.insert_catalog_rapideye(data, start_time)

                if move_img_bool:
                    Utils.move_dir(abspath_image, DESTINY_RAPIDEYE, self.__log)
        else:
            sys.exit()

    def __prepare_process_many_imgs(
        self, path_4a_cobertura, img_name, move_img_bool, id_foot
    ):
        """Method that prepare to process many images"""
        start_time = datetime.now().replace(microsecond=0)
        path_dir_img = os.path.join(
            path_4a_cobertura, img_name.strip('\n')
        )
        if not os.path.exists(path_dir_img):
            self.__log.error(' O diretório {} não existe.'.format(
                path_dir_img
            ))
            return None

        abspath_dir_img = os.path.abspath(path_dir_img)

        if Utils.check_tif_and_metadata(abspath_dir_img, log_obj=self.__log):
            try:
                data = self.__make_processing(
                    img_name.strip('\n'), abspath_dir_img, id_foot=id_foot
                )
            except Exception as ex:
                self.__log.error(
                    '\nErro ao processar a imagem {} (Inserção em'
                    ' banco interrompida)\n{}\n'.format(path_dir_img, ex)
                )
            else:
                self.__dao.insert_catalog_rapideye(data, start_time)

                if move_img_bool:
                    Utils.move_dir(abspath_dir_img, DESTINY_RAPIDEYE, self.__log)

    def main(self, path_4a_cobertura, move_img_bool, process_with_thread):
        """
        This is main method that will iterate in the file with all the names of
        the rapideye (all_rapideye.txt) imagery and will call the processing
        method to make all the processing and to return the data to insert in
        database. after get the necessary datas, this datas will to pass to DAO
        to make insertion in the database.
        """
        all_rapideye = open(FILE_ALL_RAPIDEYE, 'r')
        imgs = all_rapideye.readlines()

        if process_with_thread:

            PrepareThreads.perform(
                imgs, self.__prepare_process_many_imgs, path_4a_cobertura,
                move_img_bool
            )

        else:
            for img in imgs:
                self.__prepare_process_many_imgs(
                    path_4a_cobertura, img, move_img_bool, 'foot_1'
                )


if __name__ == '__main__':
    start_execution_time = datetime.now().replace(microsecond=0)
    args, move_img_bool, process_one_img_bool, process_with_thread = \
        Validator.validate_params(
            sys.argv
        )
    log_obj = Log(process_one_img_bool)
    process = Processing(process_one_img_bool, log_obj)

    if move_img_bool:
        print('\nA(s) imagem(s) de {} será(ão) movida(s) para {}\n'.format(
            args['-dirImgs'], DESTINY_RAPIDEYE
        ))

    # Processing one image
    if process_one_img_bool:
        process.make_processing_one_image(
            args['-dirImgs'], move_img_bool
        )
        log_obj.success(
            'O tempo gasto para o processamento desta imagem foi de {}'.format(
                datetime.now().replace(microsecond=0) - start_execution_time
            )
        )
        sys.exit()

    # Processing many imagery
    process.main(args['-dirImgs'], move_img_bool, process_with_thread)

    log_obj.success(
        'O tempo gasto para todo este processamento foi de {}.'.format(
            datetime.now().replace(microsecond=0) - start_execution_time
        )
    )
