#!-*-coding:utf-8-*-
import os
import sys

FILENAME_WITH_ALL_RAPIDEYE = 'all_rapideye.txt'


class FileManager:

    @classmethod
    def get_especific_file(
        cls, abspath_dir_img, is_metadata=False, is_tif=False
    ):
        """
        CRIAR ARQUIVO DE LOGO E ADICINAR AS IMAGENS QUE ESTÃO SEM METADADOS
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
                print('O arquivo {} não existe'.format(file_result))

        if is_metadata:
            file_result = '{}_metadata.xml'.format(img)
            if file_result not in all_files_current_dir:
                print('O arquivo {} não existe'.format(file_result))

        return os.path.join(abspath_dir_img, file_result)

    @classmethod
    def extrac_cloud_cover_percentage(cls):
        pass

    @classmethod
    def main(cls, path_4a_cobertura):
        all_rapideye = open(FILENAME_WITH_ALL_RAPIDEYE, 'r')
        i = 0
        for dir_img in all_rapideye.readlines():
            dir_img = dir_img.strip('\n')
            path_dir_img = os.path.join(path_4a_cobertura, dir_img)
            abspath_dir_img = os.path.abspath(path_dir_img)
            print(cls.get_especific_file(abspath_dir_img, is_metadata=True))

            i += 1
            if i == 3:
                break


if __name__ == '__main__':
    args = sys.argv
    FileManager.main(args[1])