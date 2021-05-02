import os
from pathlib import Path

data_path = (Path(__file__).absolute()).parent.parent / "data"


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
    "annotation": "annotation",
    "annotation_dict": "annotation_dict",

}
