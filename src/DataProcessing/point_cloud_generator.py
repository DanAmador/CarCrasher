import math
from pathlib import Path

import numpy as np
import open3d as o3d

from src.config import UserSettings as us
from src.util import create_paths
from .common import get_folder_diff, get_all_files_in_path, initialize_opencv, get_rgbd_file_lists
from .optimize_posegraph import optimize_posegraph_for_fragment, get_posegraph_name

reg = o3d.pipelines.registration
with_opencv = initialize_opencv()
if with_opencv:
    from .opencv_pose_estimation import pose_estimation


def build_intrinsic():
    intrinsic = o3d.camera.PinholeCameraIntrinsic(
        o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault)

    (fx, fy) = intrinsic.get_focal_length()
    (cx, cy) = intrinsic.get_principal_point()
    intrinsic = o3d.camera.PinholeCameraIntrinsic(1920, 1080, fx, fy, cx, cy)
    return intrinsic


def create_config(seq_path):
    # TODO use beam info
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
    def register_one_rgbd_pair(s, t, color_files, depth_files, intrinsic,
                               with_opencv, config):
        source_rgbd_image = PointCloudGenerator.read_rgbd_image(color_files[s],
                                                                depth_files[s], True,
                                                                config)
        target_rgbd_image = PointCloudGenerator.read_rgbd_image(color_files[t],
                                                                depth_files[t], True,
                                                                config)

        option = o3d.pipelines.odometry.OdometryOption()
        option.max_depth_diff = config["max_depth_diff"]
        if abs(s - t) != 1:
            if with_opencv:
                success_5pt, odo_init = pose_estimation(source_rgbd_image,
                                                        target_rgbd_image,
                                                        intrinsic, False)
                if success_5pt:
                    [success, trans, info
                     ] = o3d.pipelines.odometry.compute_rgbd_odometry(
                        source_rgbd_image, target_rgbd_image, intrinsic, odo_init,
                        o3d.pipelines.odometry.RGBDOdometryJacobianFromHybridTerm(),
                        option)
                    return [success, trans, info]
            return [False, np.identity(4), np.identity(6)]
        else:
            odo_init = np.identity(4)
            [success, trans, info] = o3d.pipelines.odometry.compute_rgbd_odometry(
                source_rgbd_image, target_rgbd_image, intrinsic, odo_init,
                o3d.pipelines.odometry.RGBDOdometryJacobianFromHybridTerm(), option)
            return [success, trans, info]

    @staticmethod
    def make_posegraph_for_fragment(path_dataset, sid, eid, color_files,
                                    depth_files, fragment_id, n_fragments,
                                    intrinsic, with_opencv, config):
        o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Info)
        pose_graph = o3d.pipelines.registration.PoseGraph()
        trans_odometry = np.identity(4)
        pose_graph.nodes.append(
            o3d.pipelines.registration.PoseGraphNode(trans_odometry))
        for s in range(sid, eid):
            for t in range(s + 1, eid):
                # odometry
                if t == s + 1:
                    print(
                        "Fragment %03d / %03d :: RGBD matching between frame : %d and %d"
                        % (fragment_id, n_fragments - 1, s, t))
                    [success, trans,
                     info] = PointCloudGenerator.register_one_rgbd_pair(s, t, color_files, depth_files,
                                                                        intrinsic, with_opencv, config)
                    trans_odometry = np.dot(trans, trans_odometry)
                    trans_odometry_inv = np.linalg.inv(trans_odometry)
                    pose_graph.nodes.append(
                        o3d.pipelines.registration.PoseGraphNode(
                            trans_odometry_inv))
                    pose_graph.edges.append(
                        o3d.pipelines.registration.PoseGraphEdge(s - sid,
                                                                 t - sid,
                                                                 trans,
                                                                 info,
                                                                 uncertain=False))

                # keyframe loop closure
                if s % config['n_keyframes_per_n_frame'] == 0 and t % config['n_keyframes_per_n_frame'] == 0:
                    print("Fragment %03d / %03d :: RGBD matching between frame : %d and %d"
                          % (fragment_id, n_fragments - 1, s, t))
                    [success, trans, info] = PointCloudGenerator.register_one_rgbd_pair(s, t, color_files, depth_files,
                                                                                        intrinsic, with_opencv, config)
                    if success:
                        pose_graph.edges.append(
                            o3d.pipelines.registration.PoseGraphEdge(
                                s - sid, t - sid, trans, info, uncertain=True))

        fragment_name = f"{str(fragment_id).zfill(6)}"
        p = path_dataset / "fragments" / config["seq_name"] / "unoptimized" / f"{fragment_name}.json"
        print(f"Saving pose at {p}")
        o3d.io.write_pose_graph(str(p.absolute()), pose_graph)

    @staticmethod
    def integrate_rgb_frames_for_fragment(color_files, depth_files, fragment_id,
                                          n_fragments, pose_graph_name, intrinsic,
                                          config):
        pose_graph = o3d.io.read_pose_graph(pose_graph_name)
        volume = o3d.pipelines.integration.ScalableTSDFVolume(
            voxel_length=config["tsdf_cubic_size"] / 512.0,
            sdf_trunc=0.04,
            color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8)
        for i in range(len(pose_graph.nodes)):
            i_abs = fragment_id * config['n_frames_per_fragment'] + i
            print(
                "Fragment %03d / %03d :: integrate rgbd frame %d (%d of %d)." %
                (fragment_id, n_fragments - 1, i_abs, i + 1, len(pose_graph.nodes)))
            rgbd = PointCloudGenerator.read_rgbd_image(color_files[i_abs], depth_files[i_abs], False,
                                                       config)
            pose = pose_graph.nodes[i].pose
            volume.integrate(rgbd, intrinsic, np.linalg.inv(pose))
        mesh = volume.extract_triangle_mesh()
        mesh.compute_vertex_normals()
        return mesh

    @staticmethod
    def make_pointcloud_for_fragment(path_dataset, color_files, depth_files,
                                     fragment_id, n_fragments, intrinsic, config):

        merged = o3d.geometry.PointCloud()
        pcd = None
        pcd_path = path_dataset / "pointclouds" / config["seq_name"]
        pcds = [p for p in pcd_path.iterdir() if p.is_file()]

        for p in pcds:
            pcd = o3d.io.read_point_cloud(str(p.absolute()), print_progress=True, format="xyz")

            merged = merged + pcd
        # for idx, (color, depth) in enumerate(zip(color_files, depth_files)):
        #     rgbd_image = PointCloudGenerator.read_rgbd_image(color, depth, True, config)
        #     if pcd:
        #         del pcd
                # rgbd_image,
                # o3d.camera.PinholeCameraIntrinsic(
                #     o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault))

            # if idx % 5 == 0:
            #     merged = merged.voxel_down_sample(.5)


        o3d.visualization.draw_geometries([merged])
            # if idx % 20 == 1:
            #     break


        #
        # pg_path = get_posegraph_name(path_dataset, config, fragment_id, True)
        # mesh = PointCloudGenerator.integrate_rgb_frames_for_fragment(
        #     color_files, depth_files, fragment_id, n_fragments,
        #     pg_path,
        #     intrinsic, config)
        # pcd = o3d.geometry.PointCloud()
        # pcd.points = mesh.vertices
        # pcd.colors = mesh.vertex_colors
        # print(pcd)
        # fragment_name = f"{str(fragment_id).zfill(6)}"
        # pcd_name = str(path_dataset / "fragments" / config["seq_name"] / "pointclouds" / f"{fragment_name}.ply")
        # o3d.io.write_point_cloud(pcd_name, merged, False, True)
        # print(f"SAved {pcd_name} : {merged}")

    @staticmethod
    def process_single_fragment(fragment_id, color_files, depth_files, n_files, n_fragments, config):

        sid = fragment_id * config['n_frames_per_fragment']
        eid = min(sid + config['n_frames_per_fragment'], n_files)
        intrinsic = build_intrinsic()
        dataset_path = Path(config["path_dataset"]).parent

        # PointCloudGenerator.make_posegraph_for_fragment(dataset_path, sid, eid, color_files,
        #                                                 depth_files, fragment_id, n_fragments,
        #                                                 intrinsic, with_opencv, config)
        # optimize_posegraph_for_fragment(dataset_path, fragment_id, config)
        PointCloudGenerator.make_pointcloud_for_fragment(dataset_path, color_files,
                                                         depth_files, fragment_id, n_fragments,
                                                         intrinsic, config)

    def run(self, multithreaded=False):

        unprocessed_seqs = list(get_folder_diff("depth", "fragments"))
        unprocessed_seqs.sort()
        seq_path = unprocessed_seqs[0]
        create_paths([
            us.data_path / "fragments" / seq_path.stem / "optimized",
            us.data_path / "fragments" / seq_path.stem / "pointclouds",
            us.data_path / "fragments" / seq_path.stem / "unoptimized"])
        for seq_path in unprocessed_seqs:
            print(f"Starting pipeline for {seq_path.name}")
            [color_files, depth_files] = get_rgbd_file_lists(seq_path)
            assert len(color_files) == len(depth_files)
            config = create_config(seq_path)
            print(seq_path)
            n_files = len(color_files)
            n_fragments = int(
                math.ceil(float(n_files) / config["n_frames_per_fragment"]))

            if multithreaded is True:
                from joblib import Parallel, delayed
                import multiprocessing
                MAX_THREAD = min(multiprocessing.cpu_count(), n_fragments)
                Parallel(n_jobs=MAX_THREAD)(delayed(PointCloudGenerator.process_single_fragment)(
                    fragment_id, color_files, depth_files, n_files, n_fragments, create_config(seq_path))
                                            for fragment_id in range(n_fragments))
            else:
                for fragment_id in range(n_fragments):
                    PointCloudGenerator.process_single_fragment(fragment_id, color_files, depth_files,
                                                                n_files, n_fragments, config)
                    break
            # break
