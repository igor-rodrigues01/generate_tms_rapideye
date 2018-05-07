#!-*-coding:utf-8-*-
import os
import sys
import xmltodict
import shutil


from footprint import MakeFootprint
from generate_tms import GenerateTMS


FILENAME_WITH_ALL_RAPIDEYE = 'all_rapideye.txt'


class FileManager:

    @classmethod
    def get_file(
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
    def get_cloud_cover_percentage(cls, abspath_dir_img):
        """
        This method will access metadata from image and will get the cloud
        cover percecentage.
        """
        metadata_xmlfile = cls.get_file(
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
        tif = cls.get_file(abspath_dir_img, is_tif=True)
        print('\nFazendo footprint.\n')

        MakeFootprint.footprint(tif, shp_out)
        print('WKT: %s' % MakeFootprint.shp_to_wkt(shp_out))

        print('\nRemovendo shp do footprint.\n')
        shutil.rmtree(shp_out)

    @classmethod
    def __make_tms(
        cls, abspath_dir_img, num_band_red=3, num_band_green=2,
        num_band_blue=1, zoom_list=[2, 15], rgb_output='.',
        link_base='teste.com.br', output_folder='tms'
    ):
        """
        Method that start tms generation
        """
        tif = cls.get_file(abspath_dir_img, is_tif=True)
        link_base = os.path.basename(tif)
        GenerateTMS.main(
            tif, num_band_red, num_band_green, num_band_blue,
            rgb_output, zoom_list, link_base, output_folder
        )

    @classmethod
    def main(cls, path_4a_cobertura):
        all_rapideye = open(FILENAME_WITH_ALL_RAPIDEYE, 'r')
        # i = 0

        for dir_img in all_rapideye.readlines():
            path_dir_img = os.path.join(path_4a_cobertura, dir_img.strip('\n'))
            abspath_dir_img = os.path.abspath(path_dir_img)
            print('Cloud %s' % cls.get_cloud_cover_percentage(abspath_dir_img))
            cls.__make_tms(abspath_dir_img)
            cls.__make_footprint(abspath_dir_img)
            # i += 1
            # if i == 1:
            break


def make_params(args):
    data = {}
    for i in range(len(args)):
        if i == 0:  # saltando a primeira iteracao pra
            # saltar o parametro que é o nome do arquivo de execução
            continue
        if not i % 2 == 0:
            data[args[i]] = args[i + 1]
    return data


if __name__ == '__main__':
    args = sys.argv
    # args = make_params(args)

    # args['-imgPathIn'], args['-br'], args['-bg'], args['-bb'],
    # args['-imgPathOut'], zoom_list, args['-link'], args['-dirTms']

    FileManager.main(args[1])
