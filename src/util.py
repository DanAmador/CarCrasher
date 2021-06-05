import os
from pathlib import Path

project_root = (Path(__file__).absolute()).parent.parent


def create_paths(paths):
    for p in paths:
        if not p.exists():
            os.mkdir(p)


def create_folders(entry_path: Path, with_seq = True):
    folder_names = list(beam2folderNames.values())
    folders = [entry_path / name for name in folder_names]
    create_paths([entry_path])
    create_paths(folders)
    amount_of_seqs = []
    for folder in folders:
        amount_of_seqs.append(len([x for x in folder.iterdir() if x.is_dir()]))

    has_same = [x == amount_of_seqs[-1] for x in amount_of_seqs]
    assert all(has_same)

    seq_num = str(amount_of_seqs[-1] + 1).zfill(4)
    seq_name = f"seq{seq_num}"
    if with_seq:
        create_paths([folder / seq_name for folder in folders])
    return seq_name


beam2folderNames = {
    "colour": "images",
    "instance": "seg_maps",
    "depth": "depth",
    "annotation": "raw_annotations",

}


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

beam2CityLabelMap = {
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

