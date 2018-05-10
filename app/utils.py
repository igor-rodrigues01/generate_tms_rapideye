#!-*-cofding:utf-8-*-

import os


class Utils:

    @staticmethod
    def make_params(args):
        data = {}
        for i in range(len(args)):
            if i == 0:  # saltando a primeira iteracao pra
                # saltar o parametro que é o nome do arquivo de execução
                continue
            if not i % 2 == 0:
                data[args[i]] = args[i + 1]
        return data

    @classmethod
    def get_file(
        cls, abspath_dir_img, is_metadata=False, is_tif=False
    ):
        """
        CRIAR ARQUIVO DE LOG E ADICINAR AS IMAGENS QUE ESTÃO SEM METADADOS
        E SEM TIF
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
