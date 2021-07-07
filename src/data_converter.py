import queue
import threading
from pathlib import Path

import cv2
import numpy as np
from typing import List

import DatasetMapper as dsm
from thread_worker import ThreadQueueWorker
from util import create_paths, beam2CityLabelMap
from config import UserSettings as us


def get_all_seg_seqs(base_path: Path):
    try:
        seqs = set([p for p in base_path.iterdir() if p.is_dir()])

        return seqs
    except Exception as e:
        create_paths([base_path])
        return set()


class DataConverter:
    def __init__(self, use_grayscale):
        self.grayscale = use_grayscale
        self.queue_worker = ThreadQueueWorker(self.convert_worker)

        self.bmng_dataset = dsm.beamng_dataset

        self.bmng_dataset.create_mappings_from_dict(beam2CityLabelMap, dsm.cityscapes, self.grayscale)
        diff = self.get_folder_diff("beamng")

        self.images_to_queue(diff)
        self.queue_worker.start_execution(10)
        # create_folders(proc_data_path, with_seq=False)

        print("Done converting")

    def get_folder_diff(self, folder_name):

        proc_data_path = us.data_path / folder_name / "seg_maps"
        proc_seqs = get_all_seg_seqs(proc_data_path)

        raw_data_path = us.data_path / folder_name / "raw_annotations"
        raw_seqs = get_all_seg_seqs(raw_data_path)
        diff = raw_seqs.difference(proc_seqs)
        print(f" {len(diff)} sequences found without processing")
        return diff

    def images_to_queue(self, path_list):
        for unprocessed in path_list:
            save_path = Path(str(unprocessed.absolute()).replace("raw_annotations", "seg_maps"))
            create_paths([save_path])

            pics = [x for x in unprocessed.iterdir() if x.is_file()]
            for pic in pics:
                self.queue_worker.push_to_queue((pic, save_path))

    def convert_worker(self):
        while True:
            (img_path, save_path) = self.queue_worker.work_q.get()
            print(img_path)
            self.convert(img_path, save_path)

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


if __name__ == "__main__":
    dc = DataConverter(use_grayscale=True)
