import json

from src.config import UserSettings as us
from .common import get_seqs_in_path, get_folder_diff, get_all_files_in_path
from src import util
import open3d as o3d
import numpy as np

#
# class PointCloudGenerator:
#     def __init__(self):
#         raw_data_path = us.data_path / "depth"
#         # unprocessed_seqs = [p.name for p in get_folder_diff("depth", "pointclouds")]
#         self.generate_image_tuples(get_folder_diff("depth", "pointclouds"))
#
#     def generate_image_tuples(self, unprocessed_seqs):
#         for seq_path in unprocessed_seqs:
#             # json.load(us.data_path / "extrinsic")
#             depth_images = get_all_files_in_path(seq_path)
#             merged_pcd = o3d.geometry.PointCloud()
#             for img in depth_images:
#                 cam_param_path = (us.data_path / "extrinsic" / seq_path.name / f"{img.stem}.json")
#                 rgb_path = (us.data_path / "images" / seq_path.name / img.name)
#                 extrinsic = json.loads(cam_param_path.read_text())
#                 depth_raw = o3d.io.read_image(str(img.absolute()))
#                 rgb_raw = o3d.io.read_image(str(rgb_path))
#
#                 rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
#                     rgb_raw, depth_raw)
#                 camera_matrix = np.identity(4)
#                 intrinsic = o3d.camera.PinholeCameraIntrinsic(
#                     o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault)
#
#                 (fx, fy) = intrinsic.get_focal_length()
#                 (cx, cy) = intrinsic.get_principal_point()
#                 intrinsic = o3d.camera.PinholeCameraIntrinsic(1920, 1080, fx, fy, cx, cy)
#                 pcd = o3d.geometry.PointCloud.create_from_rgbd_image(image=rgbd_image,
#                                                                      intrinsic=intrinsic,
#                                                                      extrinsic=camera_matrix,
#                                                                      # depth_scale=extrinsic["depth"]
#                                                                      )
#                 # print(pcd)
#                 merged_pcd = merged_pcd + pcd
#             pcd_path = us.data_path / "pointclouds" / seq_path.name / "pointcloud.ply"
#             # o3d.visualization.draw_geometries(merged_pcd)
#             o3d.io.write_point_cloud(pcd_path, merged_pcd)
#
#             # rgb_depth_pair = (us.data_path / "images" / img.name / ".png",depth_images)
#             # print(rgb_depth_pair)
