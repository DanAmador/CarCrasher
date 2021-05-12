from copy import copy
from pathlib import Path

from PIL import Image

from util import data_path, create_paths, create_folders, beam2CityLabelMap
import DatasetMapper as dsm
import cv2
import numpy as np


def get_all_seg_seqs(base_path: Path):
    try:
        seqs = set([p for p in (base_path / "annotation").iterdir() if p.is_dir()])

        return seqs
    except Exception as e:
        create_paths([base_path])
        return set()


def convert(unprocessed: Path, bmng_dataset: dsm.Dataset, grayscale=False):
    save_path = Path(str(unprocessed.absolute()).replace("raw", "mapped"))
    create_paths([save_path])
    pics = [x for x in unprocessed.iterdir() if x.is_file()]
    for pic in pics:
        image = cv2.imread(str(pic.absolute()))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        processed_image = np.zeros(image.shape)
        for k, v in bmng_dataset.mappings.items():
            processed_image[np.where((image == k).all(axis=2))] = v

        img_path = str((save_path / pic.name).absolute())
        print(img_path)
        if grayscale:
            processed_image = cv2.convertScaleAbs(processed_image)
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_RGB2GRAY)
        cv2.imwrite(img_path, processed_image)


if __name__ == "__main__":
    use_grayscale = True
    bmng = dsm.beamng_dataset
    bmng.create_mappings_from_dict(beam2CityLabelMap, dsm.cityscapes, use_grayscale)

    proc_data_path = data_path/ "captures" / "annotations"
    raw_data_path = data_path / "captures" / "raw_annotations"
    proc_seqs = get_all_seg_seqs(proc_data_path)
    raw_seqs = get_all_seg_seqs(raw_data_path)
    diff = raw_seqs.difference(proc_seqs)
    print(f" {len(diff)} sequences found without processing")

    create_folders(proc_data_path, with_seq=False)
    for unprocessed_seq in diff:
        convert(unprocessed_seq, bmng, use_grayscale)
