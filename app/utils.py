#!-*-cofding:utf-8-*-

import os
import sys
import shutil
from log import Log
"""
Possible Params:
    -thr
    -oneImg
    -dirImgs
    -move
"""


class Utils:

    @staticmethod
    def get_suffix_tif(img):
        """Method that return the correct suffix of the a image."""
        if img.endswith('.tif'):
            return '.tif'
        elif img.endswith('.tiff'):
            return '.tiff'
        elif img.endswith('.TIF'):
            return '.TIF'
        else:
            return '.TIFF'

    @classmethod
    def get_file(
        cls, abspath_dir_img, is_metadata=False, is_tif=False
    ):
        """
        Method that return the metadata or .tig from images
        """
        img = os.path.basename(abspath_dir_img)
        all_files_current_dir = os.listdir(abspath_dir_img)
        file_result = None

        if is_metadata and is_tif:
            print('Busque apenas 1 arquivo específico')

        if is_tif:
            file_result = '{}.tif'.format(img)
            if file_result not in all_files_current_dir:
                return False

        if is_metadata:
            file_result = '{}_metadata.xml'.format(img)
            if file_result not in all_files_current_dir:
                return False

        return os.path.join(abspath_dir_img, file_result)

    @classmethod
    def move_dir(cls, abspath_src, abspath_destiny, log_obj):
        """
        Method that will move the image to a destiny directory
        """
        print('Movendo imagem: {} \npara: {}'.format(
            abspath_src, abspath_destiny
        ))
        img_name = os.path.basename(abspath_src.rstrip('/'))
        try:
            shutil.move(
                abspath_src, os.path.join(abspath_destiny, img_name)
            )
        except Exception as ex:
            log_obj.error('Erro ao mover a imagem de {} para {}\n{}'.format(
                abspath_src, abspath_destiny, ex
            ))

    @classmethod
    def check_tif_and_metadata(
        cls, abspath_image, log_obj=None, is_validator=False
    ):
        """
        Method that check the existence of the useful files to processing.
        Are checked (image.tif) and the metadatas from image
        (image_metadata.xml).
        """
        tif = cls.get_file(abspath_image, is_tif=True)
        metadata = cls.get_file(abspath_image, is_metadata=True)
        msg_error_tif = 'O diretório {} está sem .tif.'.format(abspath_image)
        msg_error_metadata = 'O diretório {} está sem metadados.'.format(
            abspath_image
        )

        # if necessary to validation in validator.py file
        if is_validator:
            if tif is not False or metadata is not False:
                return True
            else:
                return False
        # =====

        if tif is False:
            log_obj.error(msg_error_tif)
            return False

        if metadata is False:
            log_obj.error(msg_error_metadata)
            return False

        return True
