#!-*-coding:utf-8-*-

import os
import sys

from landsat_processor.tiler import Tiler


class GenerateTMS:

    __dir_tms = None

    @classmethod
    def __create_tms_dir(cls, dir_tms):
        """
        Method that will create the directory where will stay the TMS's
        """
        cls.__dir_tms = dir_tms
        if not os.path.exists(cls.__dir_tms):
            os.mkdir(dir_tms)

    @classmethod
    def __make_rgb(
        cls, image_path_input, num_band_red, num_band_green, num_band_blue,
        path_output
    ):
        """
        Method that make rgb composition and return the path from output image
        """
        print('Fazendo composição rgb. {} {} {}'.format(
            num_band_red, num_band_green, num_band_blue
        ))
        suffix_img_output = '_r{}g{}b{}.tif'.format(
            num_band_red, num_band_green, num_band_blue
        )
        image_name = os.path.basename(image_path_input)

        image_path_output = os.path.join(
            path_output,
            image_name.replace('.tif', suffix_img_output)
        )
        command = "gdal_translate -q -co COMPRESS=LZW "\
            "-b {num_band_red} -b {num_band_green} -b {num_band_blue}"\
            " {image_input} {image_output}".format(
                image_input=image_path_input, num_band_red=num_band_red,
                num_band_green=num_band_green, num_band_blue=num_band_blue,
                image_output=image_path_output
            )
        os.system(command)
        print('Composição concluída.')
        return image_path_output

    @classmethod
    def __make_equalize(cls, image_input, image_output):
        """
        Method that make "contrast streach" in image already composed
        """

        print('Aplicando constraste streach.\n')
        command = "gdal_contrast_stretch -ndv '0 0 0' "\
            "-outndv 0 -percentile-range 0.02 0.98 "\
            "{image_input} {image_output}".format(
                image_input=image_input, image_output=image_output
            )
        os.system(command)
        print('Contraste aplicado.')
        return image_output

    @classmethod
    def __make_tms(
        cls, image_equalized, link_base, zoom_list=[2, 15],
        nodata_list=[0, 0, 0]
    ):
        """
        Function that call the functions to create TMS from
        plugin landsat_processor
        """
        print('Gerando TMS.\n')
        tms_path, xml_path = Tiler.make_tiles(
            image_path=image_equalized, link_base=link_base,
            output_folder=cls.__dir_tms, zoom=zoom_list,
            quiet=False, nodata=nodata_list, convert=False
        )
        return tms_path, xml_path

    @classmethod
    def main(
        cls, image_input, num_band_red, num_band_green, num_band_blue,
        rgb_out, zoom_list, link_base='teste.com.br',
        output_folder='tms'
    ):
        cls.__create_tms_dir(output_folder)
        image_rgb = cls.__make_rgb(
            image_input, num_band_red, num_band_green,
            num_band_blue, rgb_out
        )
        image_equalized = cls.__make_equalize(image_rgb, image_rgb)
        cls.__make_tms(image_equalized, link_base, zoom_list)


class ParamsController:

    def make_params(func):
        """
        Decorator that organize the entry params given by user
        """
        @classmethod
        def inner(cls, args):
            data = {}
            for i in range(len(args)):
                if i == 0:  # saltando a primeira iteracao pra
                    # saltar o parametro que é o nome do arquivo de execução
                    continue
                if not i % 2 == 0:
                    data[args[i]] = args[i + 1]
            return func(cls, data)
        return inner

    @make_params
    def validate_params(cls, args):
        keys_args_as_set = set(args.keys())

        if KEYS_DEFAULT_AS_SET.difference(keys_args_as_set) != set():
            sys.exit('Paramentros errados.')

        zoom_list = [int(args['-zoomMin']), int(args['-zoomMax'])]
        return args, zoom_list


MSG_ERROR_PARAMS = "Entre com:" \
    "\n\t-imgPathIn: \tPath da imagem rapideye de entrada:" \
    "\n\t-br: \t\tNúmero da banda red" \
    "\n\t-bg: \t\tNúmero da banda green" \
    "\n\t-br: \t\tNúmero da banda blue" \
    "\n\t-rgbPathOut: \tPath imagem rgb saída" \
    "\n\t-zoomMin: \tzoom Mínimo " \
    "\n\t-zoomMax: \tzoom Máximo" \
    "\n\t-link: \t\tLink para tms (Caminho até o imagem.tms)" \
    "\n\t-dirTms: \tPath do direttório do tms" \
    "\nExemplo:\n\n" \
    "  python generate_tms.py -imgPathIn ../path/img.tif -br 3"\
    " -bg 2 -bb 1 -imgPathOut ../teste -link teste.com -zoomMin 5"\
    " -zoomMax 8 -dirTms ./tms-teste" \


KEYS_DEFAULT_AS_SET = set(
    [
        '-imgPathIn', '-br', '-bg', '-br', '-rgbPathOut', '-zoomMin',
        '-zoomMax', '-link', '-dirTms'
    ]
)

if __name__ == '__main__':
    args = sys.argv

    if len(args) != 19:
        sys.exit(MSG_ERROR_PARAMS)

    # validate params or if necessary stop the script
    args, zoom_list = ParamsController.validate_params(args)

    GenerateTMS.main(
        args['-imgPathIn'], args['-br'], args['-bg'], args['-bb'],
        args['-rgbPathOut'], zoom_list, args['-link'], args['-dirTms']
    )
