#!-*-cofding:utf-8-*-

import os
import shutil
from log import Log
import sys


KEYS_DEFAULT_AS_SET = set(
    [
        '-dirImgs', '-oneImg', '-move'
    ]
)


class Utils:

    @staticmethod
    def make_params(args):
        """Method that reorganize the entry params of command line"""
        data = {}
        for i in range(len(args)):
            if i == 0:  # saltando a primeira iteracao pra
                # saltar o parametro que é o nome do arquivo de execução
                continue
            if not i % 2 == 0:
                data[args[i]] = args[i + 1]
        return data

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
    def move_dir(cls, abspath_src, abspath_destiny):
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
            Log.error('Erro ao mover a imagem de {} para {}\n{}'.format(
                abspath_src, abspath_destiny, ex
            ))

    @classmethod
    def check_args(cls, args_dict):
        process_one_img = False
        move_img = False

        if '-dirImgs' in args_dict.keys():
            if not os.path.exists(args_dict['-dirImgs']):
                sys.exit('O diretório {} não existe'.format(
                    args_dict['-dirImgs']
                ))
        else:
            sys.exit('O parâmetro -dirImgs não existe')

        if '-move' in args_dict.keys():
            if args_dict['-move'] != '1':
                sys.exit('O valor do parâmetro -move deve ser 1')
            move_img = True

        if '-oneImg' in args_dict.keys():
            if args_dict['-oneImg'] != '1':
                sys.exit('O valor do parâmetro -oneImg deve ser 1')
            process_one_img = True

        return args_dict, move_img, process_one_img

    @classmethod
    def validate_params(cls, args):
        if not (len(args) == 3 or len(args) == 5 or len(args) == 7):
            sys.exit(
                'Execute o script passando o caminho do diretório de'
                ' imagens da 4ª cobertura , ou apenas o path de um'
                'imagem o decidindo se deseja mover ou não'
            )

        args_dict = Utils.make_params(args)
        return cls.check_args(args_dict)
