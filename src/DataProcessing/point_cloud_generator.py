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


def create_config(seq_path):
    return {
        "name": "Beam Dataset",
        "path_dataset": str(seq_path.parent.absolute()),
        "max_depth": 50,
        "voxel_size": 2,
        "max_depth_diff": 5,
        "n_frames_per_fragment": 5,
        "n_keyframes_per_n_frame": 5,
        "preference_loop_closure_odometry": 0.1,
        "preference_loop_closure_registration": 5.0,
        "tsdf_cubic_size": 20,
        "icp_method": "color",
        "global_registration": "ransac",
        "seq_name": seq_path.name,
        "python_multi_threading": True
    }


class PointCloudGenerator:
    @staticmethod
    def read_rgbd_image(color_file, depth_file, convert_rgb_to_intensity, config):
        color = o3d.io.read_image(color_file)
        depth = o3d.io.read_image(depth_file)
        rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color,
            depth,
            depth_scale=config["max_depth"],
            depth_trunc=1,
            convert_rgb_to_intensity=convert_rgb_to_intensity)

        return rgbd_image

    @staticmethod
    def build_pointcloud(path_dataset, seq_name):
        merged = o3d.geometry.PointCloud()
        pcd_path = path_dataset / "pointclouds" / seq_name

        pcd_paths = [p for p in pcd_path.iterdir() if p.is_file()]

        for p in pcd_paths:
            pcd = o3d.io.read_point_cloud(str(p.absolute()), print_progress=True, format="xyz")
            merged = merged + pcd

        return merged

    @staticmethod
    def unproject_pcd(path_dataset, pcd, seq_name, save_image=False):
        # vis = o3d.visualization.Visualizer()
        # vis.create_window(width=640, height=480)
        # vis.add_geometry(pcd)
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

        pcd = np.asarray(pcd.points)

        # o3d.visualization.draw_geometries([pcd])
        for cam_extrs in cams:
            cam_e = json.loads(cam_extrs.read_text())
            # render.setup_camera()
            world_pos = np.array(cam_e["world_cam_pos"])
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
            for idx,(h, w) in enumerate(point_screen_coords):
                if idx % 50000 == 0:
                    print(f"Unprojecting {seq_name}-{cam_extrs.stem} {(idx/amount_of_points)*100}%")
                depth_val = d_img[h][w][0]
                unp = render.scene.camera.unproject(w, h, depth_val, cam_i.width, cam_i.height)
                if not math.isinf(unp[0]) and not math.isinf(unp[1]) and not math.isinf(unp[2]):
                    [_, idx, _] = pcd_tree.search_knn_vector_3d(unp, 1)
                    r = [int(w), int(h), int(idx[0])]
                    unprojections['w%dxh%d' % (w, h)] = r
            print(f"Saving unprojection for {cam_extrs.stem}")
            pickle.dump(unprojections, open(unp_path / f"{cam_extrs.stem}.pkl", 'wb'))
        # # for w in cam_i.width:
        #     for h in cam_i.height:
        #         unp = render.scene.camera.unproject(w,h,)
        # for idx, r in enumerate(results):
        #     (w, h) = r[0]
        #     print(w, h)
        #     if 0 <= w <= cam_i.width and 0 <= h <= cam_i.height:
        #         print(idx / len(results))
        #         shot_unprojection.append([w, h, idx])
        # print(idx)
        # cv2.project_po
        # unp = render.scene.camera.unproject(cam_i.width, cam_i.height, cam_e["depth"])
        # print(unp)
        # frame_points = render.scene.camera.unproject()
        # unproj_path = path_dataset / "unprojections / "

    @staticmethod
    def process_sequence(multithreaded=False):
        unprocessed_seqs = list(get_folder_diff("depth", "fragments"))
        unprocessed_seqs.sort()
        seq_path = unprocessed_seqs[0]
        # create_paths([us.data_path / "fragments" / seq_path.stem / "unoptimized"])

        for seq_path in unprocessed_seqs:
            # process_sequence(us.data_path, seq_path.name)
            config = create_config(seq_path)
            pcd = PointCloudGenerator.build_pointcloud(us.data_path, seq_path.name)
            PointCloudGenerator.unproject_pcd(us.data_path, pcd, seq_path.name, True)
            break

        #     print(f"Starting pipeline for {seq_path.name}")
        #     [color_files, depth_files] = get_rgbd_file_lists(seq_path)
        #     assert len(color_files) == len(depth_files)
        #     print(seq_path)
        #     n_files = len(color_files)
        #     n_fragments = int(
        #         math.ceil(float(n_files) / config["n_frames_per_fragment"]))
        #
        #     if multithreaded is True:
        #         from joblib import Parallel, delayed
        #         import multiprocessing
        #         MAX_THREAD = min(multiprocessing.cpu_count(), n_fragments)
        #         Parallel(n_jobs=MAX_THREAD)(delayed(PointCloudGenerator.process_single_fragment)(
        #             fragment_id, color_files, depth_files, n_files, n_fragments, create_config(seq_path))
        #                                     for fragment_id in range(n_fragments))
        #     else:
        #         for fragment_id in range(n_fragments):
        #             PointCloudGenerator.process_single_fragment(fragment_id, color_files, depth_files,
        #                                                         n_files, n_fragments, config)
        #             break
        #     # break
