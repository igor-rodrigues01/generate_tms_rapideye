#!-*-coding:utf-8-*-

import os
import sys
from utils import Utils


KEYS_DEFAULT_AS_SET = {'-thr', '-oneImg', '-dirImgs', '-move'}


class Validator:

    @classmethod
    def __validate_dir_imgs(cls, args_dict, process_one_img):
        """
        Method that validate the -dirImgs params
        """
        if '-dirImgs' in args_dict.keys():
            args_dict['-dirImgs'] = args_dict['-dirImgs'].rstrip('/')

            if not os.path.exists(args_dict['-dirImgs']):
                sys.exit('O diretório {} não existe'.format(
                    args_dict['-dirImgs']
                ))
            if not process_one_img and \
               Utils.check_tif_and_metadata(
                   args_dict['-dirImgs'], is_validator=True
               ):
                sys.exit(
                    'Para processar apenas uma imagem passe o parâmetro'
                    ' "-oneImg 1"'
                )
        else:
            sys.exit('O parâmetro -dirImgs não existe')

    @classmethod
    def __check_args(cls, args_dict):
        """
        Method that accomplish the verification of the entry parameters
        """
        process_one_img = False
        move_img = False
        process_with_thread = False
        keys = args_dict.keys()

        # preventing the thread processing to one image
        if all([i in keys for i in ['-thr', '-oneImg']]) is True:
            sys.exit(
                'Não é possível utilizar threads para processar apenas '
                'uma imagem'
            )

        if '-thr' in keys:
            if args_dict['-thr'] != '1':
                sys.exit('O valor do parâmetro -thr deve ser 1')
            process_with_thread = True

        if '-move' in keys:
            if args_dict['-move'] != '1':
                sys.exit('O valor do parâmetro -move deve ser 1')
            move_img = True

        if '-oneImg' in keys:
            if args_dict['-oneImg'] != '1':
                sys.exit('O valor do parâmetro -oneImg deve ser 1')
            process_one_img = True

        cls.__validate_dir_imgs(args_dict, process_one_img)

        return args_dict, move_img, process_one_img, process_with_thread

    @staticmethod
    def __make_params(args):
        """Method that reorganize the entry params of command line"""
        data = {}
        for i in range(len(args)):
            if i == 0:  # saltando a primeira iteracao pra
                # saltar o parametro que é o nome do arquivo de execução
                continue
            if not i % 2 == 0:
                data[args[i]] = args[i + 1]
        return data

    @classmethod
    def validate_params(cls, args):
        """
        Method that call other methods to make the entry parameters validations
        """
        if not (len(args) == 3 or len(args) == 5 or len(args) == 7):
            sys.exit(
                'Execute o script passando o caminho do diretório de'
                ' imagens da 4ª cobertura , ou apenas o path de uma'
                'imagem e decida se deseja mover ou não'
            )
        args_dict = cls.__make_params(args)
        keys_args_set = set(args_dict.keys())
        if keys_args_set.difference(KEYS_DEFAULT_AS_SET) != set():
            sys.exit(
                'Verifique a passagem de parâmetros.'
                ' Foi encontrado parâmetros desconhecidos.'
            )

        return cls.__check_args(args_dict)
