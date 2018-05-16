#!-*-coding:utf-8-*-
import os
import sys
import xmltodict
import shutil

from footprint import MakeFootprint
from generate_tms import GenerateTMS
from shapely.geometry.multipolygon import MultiPolygon
from shapely import wkt
from utils import Utils
from log import Log
from constants import (
    OUTSIZE_RGB, FILE_ALL_RAPIDEYE, TOTAL_PART, BAND_R, BAND_G,
    BAND_B, DIR_PNG, DIR_TMS, ZOOM_MIN, ZOOM_MAX, URL_TMS, B52_PATH,
    DESTINY_RAPIDEYE
)
from dao import DAO
from threading import Thread


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
                'O diretório {} está sem .tif.'.format(abspath_image)
            )
            return False

        if metadata is False:
            Log.error(
                'O diretório {} está sem metadados.'.format(abspath_image)
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

    def __get_xml_tms(self, image_name):
        """Method that get the xml file from TMS generated"""
        suffix_extension_tif = Utils.get_suffix_tif(image_name)
        img_rgb_xml = image_name.replace(suffix_extension_tif, '.xml')
        return os.path.join(URL_TMS, img_rgb_xml)

    def __get_image_rgb(self, abspath_dir_img, image_name):
        """
        Method that get image name from RGB image to add in the database.
        """
        sufix_rgb = '_r{}g{}b{}.tif'.format(BAND_R, BAND_G, BAND_B)
        image_name += sufix_rgb
        abspath_image = os.path.join(abspath_dir_img, image_name)
        if os.path.exists(abspath_image):
            return abspath_image, image_name
        else:
            print('Imagem {} não encontrada'.format(image_name))

    def __get_path(self, img_name):
        """Method that return path to directory of the images on b52."""
        return '{}{}'.format(B52_PATH, img_name)

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
        return path_img_png

    def __get_date(self, abspath_dir_img):
        """
        Method that get the date from name of the image.tif.
        """
        img_name = os.path.basename(abspath_dir_img)
        return img_name.split('_')[1]

    def __make_processing(self, img_name, abspath_dir_img, id_foot):
        """
        Method that call other methods to perform all the necessary
        processings in the imagery.
        """
        data = {}
        data['data'] = self.__get_date(abspath_dir_img)
        data['total_part'] = TOTAL_PART
        data['nuvens'] = self.get_cloud(abspath_dir_img)
        self.__make_tms(abspath_dir_img)
        data['geom'] = self.__make_footprint(abspath_dir_img, shp_out=id_foot)
        abspath_rgb, img_name_rgb = self.__get_image_rgb(
            abspath_dir_img, img_name
        )
        data['tms'] = self.__get_xml_tms(img_name_rgb)
        data['image'] = img_name_rgb
        data['quicklook'] = self.__make_png(abspath_rgb)
        data['path'] = self.__get_path(img_name)
        return data

    def make_processing_one_image(self, abspath_image, move_img_bool):
        """
        Method that make the processing in one image
        """
        abspath_image = abspath_image.rstrip('/')
        img_name = os.path.basename(abspath_image)

        if self.__check_tif_and_metadata(abspath_image):
            try:
                data = self.__make_processing(img_name, abspath_image)
            except Exception as ex:
                Log.error(
                    '\nErro ao processar a imagem {} (Inserção '
                    'em banco interrompida)\n{}\n'.format(abspath_image, ex)
                )
            else:
                self.__dao.insert_catalog_rapideye(data)

                if move_img_bool:
                    Utils.move_dir(abspath_image, DESTINY_RAPIDEYE)
        else:
            sys.exit()

    def __prepare_process_many_imgs(
        self, path_4a_cobertura, img_name, move_img_bool, id_foot
    ):
        path_dir_img = os.path.join(
            path_4a_cobertura, img_name.strip('\n')
        )
        if not os.path.exists(path_dir_img):
            Log.error(' O diretório {} não existe.'.format(path_dir_img))
            return None

        abspath_dir_img = os.path.abspath(path_dir_img)

        if self.__check_tif_and_metadata(abspath_dir_img):
            try:
                data = self.__make_processing(
                    img_name.strip('\n'), abspath_dir_img, id_foot=id_foot
                )
            except Exception as ex:
                Log.error(
                    '\nErro ao processar a imagem {} (Inserção em'
                    ' banco interrompida)\n{}\n'.format(path_dir_img, ex)
                )
            else:
                self.__dao.insert_catalog_rapideye(data)

                if move_img_bool:
                    Utils.move_dir(abspath_dir_img, DESTINY_RAPIDEYE)

    def main(self, path_4a_cobertura, move_img_bool):
        """
        This is main method that will iterate in the file with all the names of
        the rapideye (all_rapideye.txt) imagery and will call the processing
        method to make all the processing and to return the data to insert in
        database. after get the necessary datas, this datas will to pass to DAO
        to make insertion in the database.
        """
        all_rapideye = open(FILE_ALL_RAPIDEYE, 'r')
        imgs = all_rapideye.readlines()
        i = 0

        while i <= len(imgs):

            t1 = Thread(target=self.__prepare_process_many_imgs,
                args=[path_4a_cobertura, imgs[i], move_img_bool, 'foot_1'],
                daemon=True)
            t2 = Thread(target=self.__prepare_process_many_imgs,
                args=[path_4a_cobertura, imgs[i + 1], move_img_bool, 'foot_2'],
                daemon=True)
            t3 = Thread(target=self.__prepare_process_many_imgs,
                args=[path_4a_cobertura, imgs[i + 2], move_img_bool, 'foot_3'],
                daemon=True)
            t4 = Thread(target=self.__prepare_process_many_imgs,
                args=[path_4a_cobertura, imgs[i + 3], move_img_bool, 'foot_1'],
                daemon=True)
            t5 = Thread(target=self.__prepare_process_many_imgs,
                args=[path_4a_cobertura, imgs[i + 4], move_img_bool, 'foot_2'],
                daemon=True)
            t6 = Thread(target=self.__prepare_process_many_imgs,
                args=[path_4a_cobertura, imgs[i + 5], move_img_bool, 'foot_3'],
                daemon=True)
            t7 = Thread(target=self.__prepare_process_many_imgs,
                args=[path_4a_cobertura, imgs[i + 6], move_img_bool, 'foot_1'],
                daemon=True)
            t8 = Thread(target=self.__prepare_process_many_imgs,
                args=[path_4a_cobertura, imgs[i + 7], move_img_bool, 'foot_2'],
                daemon=True)
            t9 = Thread(target=self.__prepare_process_many_imgs,
                args=[path_4a_cobertura, imgs[i + 8], move_img_bool, 'foot_3'],
                daemon=True)
            t10 = Thread(target=self.__prepare_process_many_imgs,
                args=[path_4a_cobertura, imgs[i + 9], move_img_bool, 'foot_1'],
                daemon=True)

            t1.start()
            t2.start()
            t3.start()
            t4.start()
            t5.start()
            t6.start()
            t7.start()
            t8.start()
            t9.start()
            t10.start()

            t1.join()
            t2.join()
            t3.join()
            t4.join()
            t5.join()
            t6.join()
            t7.join()
            t8.join()
            t9.join()
            t10.join()

            if i == len(imgs) - 10:
                break

            i += 10


if __name__ == '__main__':
    process = FileManager()

    args_dict, move_img_bool, process_one_img = Utils.validate_params(sys.argv)

    if move_img_bool:
        print('\nA(s) imagem(s) de {} será(ão) movida(s) para {}\n'.format(
            args_dict['-dirImgs'], DESTINY_RAPIDEYE
        ))

    if process_one_img:
        process.make_processing_one_image(args_dict['-dirImgs'], move_img_bool)
        sys.exit()

    process.main(args_dict['-dirImgs'], move_img_bool)
