#!-*-coding:utf-8-*-

import xmltodict
import os

from utils import Utils
from constants import URL_TMS, BAND_R, BAND_G, BAND_B, B52_PATH


class ImageInfo:

    @classmethod
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

    @classmethod
    def get_xml_tms(self, image_name):
        """Method that get the xml file from TMS generated"""
        suffix_extension_tif = Utils.get_suffix_tif(image_name)
        img_rgb_xml = image_name.replace(suffix_extension_tif, '.xml')
        return os.path.join(URL_TMS, img_rgb_xml)

    @classmethod
    def get_image_rgb(self, abspath_dir_img, image_name):
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

    @classmethod
    def get_path(self, img_name):
        """Method that return path to directory of the images on b52."""
        return '{}{}'.format(B52_PATH, img_name)

    @classmethod
    def get_date(self, abspath_dir_img):
        """
        Method that get the date from name of the image.tif.
        """
        img_name = os.path.basename(abspath_dir_img)
        return img_name.split('_')[1]
