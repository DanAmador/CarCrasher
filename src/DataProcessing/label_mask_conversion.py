from pathlib import Path

import cv2
import numpy as np

import src.DataProcessing as dsm
from src.DataProcessing.common import get_folder_diff, get_all_files_in_path
from src.util import create_paths, beam2CityLabelMap, ThreadQueueWorker


class SegmentationMasksConversion:
    def __init__(self, use_grayscale):
        self.grayscale = use_grayscale
        self.queue_worker = ThreadQueueWorker(self.convert_worker)
        self.bmng_dataset = dsm.beamng_dataset

        self.bmng_dataset.create_mappings_from_dict(beam2CityLabelMap, dsm.cityscapes, self.grayscale)

        # self.queue_worker.start_execution(10)
        # create_folders(proc_data_path, with_seq=False)

    @staticmethod
    def get_all_images():
        diff = get_folder_diff("raw_annotations", "seg_maps")
        for unprocessed in diff:
            save_path = Path(str(unprocessed.absolute()).replace("raw_annotations", "seg_maps"))
            create_paths([save_path])

            pics = get_all_files_in_path(unprocessed)
            for pic in pics:
                yield pic, save_path

    def images_to_queue(self):
        for pic, save_path in self.get_all_images():
            self.queue_worker.push_to_queue((pic, save_path))

    def process_all_single_thread(self):
        total = 0
        for pic, save_path in self.get_all_images():
            total += 1
            if total % 20 == 0:
                print(save_path)
            self.convert(pic, save_path)
        print("Done converting")

    def convert_worker(self):
        while True:
            item = (img_path, save_path) = self.queue_worker.work_q.get()
            if item is None:
                break
            self.queue_worker.work_q.task_done()
            self.convert(img_path, save_path)
            print(img_path)

    def convert(self, pic: Path, save_path: Path):
        img_path = str((save_path / pic.name).absolute())
        image = cv2.imread(str(pic.absolute()))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        processed_image = np.zeros(image.shape)

        for mask, replaced_value in self.bmng_dataset.mappings.items():
            processed_image[np.where((image == mask).all(axis=2))] = replaced_value

        if self.grayscale:
            processed_image = cv2.convertScaleAbs(processed_image)
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_RGB2GRAY).astype('uint8')
        cv2.imwrite(img_path, processed_image)
        del processed_image
