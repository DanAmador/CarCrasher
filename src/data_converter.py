import queue
import threading
from pathlib import Path

import cv2
import numpy as np
from typing import List

import DatasetMapper as dsm
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
        self.work_q = queue.Queue()
        self.total_images = 0
        folder_name = "beamng"
        self.bmng_dataset = dsm.beamng_dataset
        self.bmng_dataset.create_mappings_from_dict(beam2CityLabelMap, dsm.cityscapes, use_grayscale)

        proc_data_path = us.data_path / folder_name / "seg_maps"
        proc_seqs = get_all_seg_seqs(proc_data_path)

        raw_data_path = us.data_path / folder_name / "raw_annotations"
        raw_seqs = get_all_seg_seqs(raw_data_path)
        diff = raw_seqs.difference(proc_seqs)
        print(f" {len(diff)} sequences found without processing")
        self.images_to_queue(diff)

        # create_folders(proc_data_path, with_seq=False)
        threads = []
        for t in range(10):
            worker = threading.Thread(target=self.convert_worker)
            worker.daemon = True
            threads.append(worker)
            worker.start()
        for thread in threads:  # iterates over the threads
            thread.join(20)  # waits until the thread has finished work

        print("Done converting")

    def images_to_queue(self, path_list):
        for unprocessed in path_list:
            save_path = Path(str(unprocessed.absolute()).replace("raw_annotations", "seg_maps"))
            create_paths([save_path])

            pics = [x for x in unprocessed.iterdir() if x.is_file()]
            for pic in pics:
                self.total_images = self.total_images + 1
                self.work_q.put((pic, save_path))

    def convert_worker(self):
        while True:

            r = (img_path, save_path) = self.work_q.get()
            print(r)
            self.convert(img_path, save_path)

    def convert(self, pic: Path, save_path: Path):
        img_path = str((save_path / pic.name).absolute())
        image = cv2.imread(str(pic.absolute()))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        processed_image = np.zeros(image.shape)

        for k, v in self.bmng_dataset.mappings.items():
            processed_image[np.where((image == k).all(axis=2))] = v

        if self.grayscale:
            processed_image = cv2.convertScaleAbs(processed_image)
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_RGB2GRAY).astype('uint8')
        cv2.imwrite(img_path, processed_image)
        del processed_image


if __name__ == "__main__":
    dc = DataConverter(use_grayscale=True)
