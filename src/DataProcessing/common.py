from pathlib import Path

from src.config import UserSettings as us
from src.util import create_paths


def get_rgbd_file_lists(path):
    seq_path = Path(path)
    rgb_path = (us.data_path / "images" / seq_path.name)
    depth_path = (us.data_path / "depth" / seq_path.name)

    depth_images = [str(p.absolute()) for p in get_all_files_in_path(depth_path)]
    rgb_images = [str(p.absolute()) for p in get_all_files_in_path(rgb_path)]
    return [rgb_images, depth_images]


def initialize_opencv():
    opencv_installed = True
    try:
        import cv2
    except ImportError:
        pass
        print("OpenCV is not detected. Using Identity as an initial")
        opencv_installed = False
    if opencv_installed:
        print("OpenCV is detected. Using ORB + 5pt algorithm")
    return opencv_installed


def get_all_files_in_path(p: Path):
    return [x for x in p.iterdir() if x.is_file()]


def get_seqs_in_path(base_path: Path):
    try:
        seqs = set([p for p in base_path.iterdir() if p.is_dir()])

        return seqs
    except Exception as e:
        create_paths([base_path])
        return set()


# Finds sequences that exist in folder 1 but not in folder 2
def get_folder_diff(folder1, folder2):
    f1_data_path = us.data_path / folder1
    to_check_seqs = get_seqs_in_path(f1_data_path)

    f2_data_path = us.data_path / folder2
    difference_set = get_seqs_in_path(f2_data_path)
    diff = to_check_seqs.difference(difference_set)
    print(f" {len(diff)} sequences found without processing")
    return diff
