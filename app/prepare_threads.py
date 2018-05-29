#!-*-coding:utf-8-*-
import numpy as np
from threader import Threader

ALL_THREADS = [
    Threader, Threader, Threader, Threader, Threader,
    Threader, Threader, Threader, Threader, Threader
]


class PrepareThreads:

    @classmethod
    def __get_lot(cls, imgs, max_threads=10):
        """
        - Method that return a lot of the agrouped images and a quantity of the
        threads that will to process this groups. Case the total lot has most
        of 10 images, the images will be agrouped in groups of 10 images and
        will return the quantity maximun of the threads (10).
        Case the lote has images remaining, this rest will be returned.
        - Case the lot is smaller 10
        images will be returned in a array and the thread maximum quantity
        will be the quantity of the itens.
        """
        lot_agrouped = None
        lot_remaining = None
        lot_without_rest = False
        imgs_array = np.array(imgs)

        if len(imgs) < max_threads:
            max_threads = len(imgs)
            lot_agrouped = imgs_array
        else:
            rest_imgs = len(imgs) % max_threads

            if rest_imgs:
                lot_without_rest = imgs_array[:-rest_imgs]
                lot_remaining = imgs_array[-rest_imgs:]
                items_by_group = int(len(lot_without_rest) / max_threads)
                lot_agrouped = lot_without_rest.reshape(
                    items_by_group, max_threads
                )
            else:
                lot_remaining = None
                items_by_group = int(len(imgs_array) / max_threads)
                lot_agrouped = imgs_array.reshape(
                    items_by_group, max_threads
                )

        return lot_agrouped, max_threads, lot_remaining

    @classmethod
    def __perform_few_threads(
        cls, lot_imgs, max_threads, callback, args_callback
    ):
        """
        Method that will perform the processing in remaining group concorrently
        when the lot of the images given by argument (lot_imgs) have less of
        10 itens.
        The threads maximum quantity will be the size of the lot remaining
        (lot_imgs)
        """
        print('\nEste lote será processado com {} threads\n\n'.format(
            max_threads
        ))
        thrds_in_running = []
        i = 0
        for img in lot_imgs:
            args_callback['id_foot'] = 'foot{}'.format(i)
            args_callback['img_name'] = img
            thrd = Threader(callback, **args_callback)
            thrd.start()
            thrds_in_running.append(thrd)
            i += 1

        for thrd_running in thrds_in_running:
            thrd_running.join()

    @classmethod
    def __perform_10_threads(
        cls, lot_agrouped, lot_remaining, max_threads, callback, args_callback
    ):
        """
        Method that perform the processing in a agrouped lot with 10 threads
        """
        print('\nEste lote será processado com {} threads\n\n'.format(
            max_threads
        ))
        i = 0
        thrds_in_running = []

        for group in lot_agrouped:
            i = 0

            for process_thread in ALL_THREADS:
                # identifing the foot print to each thread
                args_callback['id_foot'] = 'f{}'.format(i)
                args_callback['img_name'] = group[i]
                thrd = process_thread(callback, **args_callback)
                thrd.start()
                thrds_in_running.append(thrd)
                i += 1

            for thrd_running in thrds_in_running:
                thrd_running.join()

        if lot_remaining:
            PrepareThreads.__perform_few_threads(
                lot_remaining, len(lot_remaining), callback, args_callback
            )

    @classmethod
    def perform(cls, imgs, callback, path_4a_cobertura, move_img_bool):
        """
        Method that call the function to agroup the lot for the processing and
        define if the lots will be processed with 10 threads or with a few
        threads (the size of little lot (lot smaller that 10) will be a
        threads quantity to processing this lot)
        """
        lot_agrouped, max_threads, lot_remaining = cls.__get_lot(imgs)
        args_callback = {
            'path_4a_cobertura': path_4a_cobertura,
            'move_img_bool': move_img_bool,
            'id_foot': None
        }
        if max_threads == 10:
            cls.__perform_10_threads(
                lot_agrouped, lot_remaining, max_threads, callback,
                args_callback
            )
        else:
            cls.__perform_few_threads(
                lot_agrouped, max_threads, callback, args_callback
            )
