from copy import copy
from pathlib import Path

from PIL import Image

from util import data_path, create_paths, create_folders
import DatasetMapper as dsm
import cv2
import numpy as np

# 'unlabeled',
# 'ego vehicle',
# 'rectification border',
# 'out of roi',
# 'static',
# 'dynamic',
# ground
# 'road',
# 'parking',
# 'rail track', 10,
# 'building', 11, 2,
# 'wall', 12, 3, 'co
# 'fence', 13, 4, 'co
# 'guard rail', 14, 255, 'co
# 'bridge', 15, 255, 'co
# 'tunnel', 16, 255, 'c
# 'pole', 17,
# 'polegroup', 18, 25
# 'traffic light', 19,
# 'traffic sign', 20
# 'vegetation', 21,
# 'terrain', 22,
# 'person', 24
# 'rider',
# 'car', 26
# 'truck', 2
# 'bus', 28,
# 'caravan', 29
# 'trailer', 30,
# 'train', 31,
# 'motorcycle', 32
# 'bicycle', 33,
# 'license plate', -1,

mapping_dict = {
    "SKY": "sky",
    "STREET": "road",
    "SIDEWALK": "sidewalk",
    "ASPHALT": "road",
    "CAR": "car",
    "BUILDINGS": "building",
    "POLE": "truck",
    "BACKGROUND": None,
    "DASHED_LINE": None,
    "COBBLESTONE": None,
    "NATURE": None,
    "OBSTACLES": None,
    "DRIVING_INSTRUCTIONS": None,
    "RESTRICTED_STREET": None,
    "ROADBLOCK": None,
    "SIDEBARS": None,
    "SOLID_LINE": None,
    "SPEED_BUMP": None,
    "TRAFFIC_SIGNALS": None,
    "TRAFFIC_SIGNS": None,
    "TRUCK_TRAILERS": None,
    "TRUCK": None,
    "ZEBRA_CROSSING": None,
    "GUARD_RAIL": None,
    "WATER": None,
    "ROCK": None,
    "SAND": None,
    "GRASS": None,
    "MUD": None,
}


def get_all_seg_seqs(base_path: Path):
    try:
        seqs = set([p for p in (base_path / "annotation").iterdir() if p.is_dir()])

        return seqs
    except Exception as e:
        create_paths([base_path])
        return set()


def convert(unprocessed: Path, bmng: dsm.Dataset, grayscale=False):
    save_path = Path(str(unprocessed.absolute()).replace("raw", "mapped"))
    create_paths([save_path])
    pics = [x for x in unprocessed.iterdir() if x.is_file()]
    for pic in pics:
        image = cv2.imread(str(pic.absolute()))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        processed_image = np.zeros(image.shape)
        for k, v in bmng.mappings.items():
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
    bmng.create_mappings_from_dict(mapping_dict, dsm.cityscapes, use_grayscale)

    proc_data_path = data_path / "mapped"
    raw_data_path = data_path / "raw"
    proc_seqs = get_all_seg_seqs(proc_data_path)
    raw_seqs = get_all_seg_seqs(raw_data_path)
    diff = raw_seqs.difference(proc_seqs)
    print(f" {len(diff)} sequences found without processing")

    create_folders(proc_data_path, with_seq=False)
    for unprocessed in diff:
        convert(unprocessed, bmng, use_grayscale)
