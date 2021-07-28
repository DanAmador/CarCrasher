
import json
import random
from dataclasses import dataclass
from pathlib import Path

from src.util import beam2folderNames, NumpyArrayEncoder


@dataclass(frozen=False)
class Capture:
    frame: int
    data: dict
    name: str
    entry_path: Path
    seq_name: str

    def save_to_file(self):
        #  print(f"Saving {self.seq_name}/{self.name}")

        for beamName, folderName in beam2folderNames.items():
            f_path = self.entry_path / folderName / self.seq_name
            img = self.data.get(beamName)
            if beamName == "camera":
                with open((f_path / f"{self.name}.json").absolute(), "w") as f:
                    json.dump(img, f, cls=NumpyArrayEncoder)
            elif beamName == "pointclouds" and "points" in self.data:

                vertices = self.data.get("points")
                # vertices = points.reshape(points.size // 3, 3)
                # random.shuffle(vertices)
                with open((f_path / f"{self.name}.txt").absolute(), "w") as f:
                    for idx in range(len(vertices)):
                        # print(p)
                        # p = p.tolist()

                        if idx > 5000:
                            break
                        try:
                            # p = " ".join([str(v) for v in vertices[random.randint(0, len(vertices))]])
                            # p = vertices[random.randint(0, len(vertices))]
                            p = vertices[random.randint(0, len(vertices))]
                            f.write(f"{p[0]} {p[1]} {p[2]}\n")
                        except IndexError:
                            print(f"index error with {p}")
                            continue
            # o3d.io.write_point_cloud(pcd_name, pcd, False, True)
            elif img is not None:
                img.convert("RGB").save((f_path / f"{self.name}.png").absolute())

        del self.data

        # __init__(self: open3d.cpu.pybind.geometry.PointCloud, points: open3d.cpu.pybind.utility.Vector3dVector)

