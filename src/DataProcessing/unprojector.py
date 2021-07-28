import json
import math
import pickle
import time

import numpy as np
import open3d as o3d
import torch
from beamngpy import compute_rotation_matrix, angle_to_quat
from open3d.cpu.pybind.visualization import rendering

from src.config import UserSettings as us
from src.util import create_paths
from .common import get_folder_diff
import cv2


def build_intrinsic():
    intrinsic = o3d.camera.PinholeCameraIntrinsic(o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault)

    (fx, fy) = intrinsic.get_focal_length()
    (cx, cy) = intrinsic.get_principal_point()
    intrinsic.set_intrinsics(1920, 1080, fx, fy, cx, cy)
    return intrinsic



def build_pointcloud(path_dataset, seq_name):
    merged = o3d.geometry.PointCloud()
    pcd_path = path_dataset / "pointclouds" / seq_name

    pcd_paths = [p for p in pcd_path.iterdir() if p.is_file()]

    for p in pcd_paths:
        pcd = o3d.io.read_point_cloud(str(p.absolute()), print_progress=True, format="xyz")
        merged = merged + pcd

    return merged


def unproject_pcd(path_dataset, pcd, seq_name, save_image=False):
    cameras = path_dataset / "camera" / seq_name
    depth_path = path_dataset / "depth" / seq_name
    unp_path = path_dataset / "unprojections" / seq_name
    cams = [p for p in cameras.iterdir() if p.is_file()]

    cam_i = build_intrinsic()
    render = o3d.visualization.rendering.OffscreenRenderer(cam_i.width, cam_i.height)
    # render.scene.scene.enable_sun_light(True)
    depth_mat = rendering.Material()
    depth_mat.shader = "depth"
    render.scene.show_axes(True)
    render.scene.add_geometry("merged", pcd, depth_mat)
    render.scene.set_background([0, 0, 0, 0])
    pcd_tree = o3d.geometry.KDTreeFlann(pcd)

    # o3d.visualization.draw_geometries([pcd])
    for cam_extrs in cams:
        cam_e = json.loads(cam_extrs.read_text())
        # render.setup_camera()
        world_pos = np.array(cam_e["world_car_pos"])
        cam_pos = np.array(cam_e["local_cam_pos"])
        pos = world_pos + cam_pos
        look_at = np.array(cam_e["car_dir"]) + pos
        render.setup_camera(cam_e["fov"], look_at, pos, cam_e["up"])

        img = render.render_to_image()
        if save_image:
            save_path = path_dataset / "fragments" / f"{cam_extrs.stem}.png"
            # print(save_path)
            o3d.io.write_image(str(save_path.absolute()), img)
        point_screen_coords = np.argwhere(np.any(np.asarray(img) != [0, 0, 0], axis=2))
        d_img = cv2.imread(str(depth_path / f"{cam_extrs.stem}.png"))
        unprojections = {}
        amount_of_points = len(point_screen_coords)
        for idx, (h, w) in enumerate(point_screen_coords):
            key = 'w%dxh%d' % (w, h)
            if idx % 50000 == 0:
                print(
                    f"Unprojecting {seq_name}-{cam_extrs.stem} {round((idx / amount_of_points) * 100, 2)}% {amount_of_points - idx} left")
            depth_val = d_img[h][w][0]
            unp = render.scene.camera.unproject(w, h, depth_val, cam_i.width, cam_i.height)
            if not math.isinf(unp[0]) and not math.isinf(unp[1]) and not math.isinf(unp[2]):
                [_, idx, _] = pcd_tree.search_knn_vector_3d(unp, 1)
                r = [int(w), int(h), int(idx[0])]
                if key not in unprojections:
                    unprojections[key] = []
                unprojections[key].extend(r)
        print(f"Saving unprojection for {cam_extrs.stem}")
        pickle.dump(unprojections, open(unp_path / f"{cam_extrs.stem}.pkl", 'wb'))


def unproject_dataset(multithreaded=False):
    unprocessed_seqs = list(get_folder_diff("depth", "fragments"))
    unprocessed_seqs.sort()
    # create_paths([us.data_path / "fragments" / seq_path.stem / "unoptimized"])

    for seq_path in unprocessed_seqs:
        # process_sequence(us.data_path, seq_path.name)
        pcd = build_pointcloud(us.data_path, seq_path.name)
        unproject_pcd(us.data_path, pcd, seq_path.name, True)
        break
