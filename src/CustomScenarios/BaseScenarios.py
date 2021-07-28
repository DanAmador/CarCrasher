from abc import ABC, abstractmethod

from OpenGL.GL import *
from OpenGL.GLUT import *
from beamngpy.sensors import Lidar

import src.BeamBuilder as BeamBuilder
from src.Recording.Sequence import CarSequence, StaticCamSequence
from src.config import UserSettings as us


class AbstractRecordingScenario(ABC):

    def __init__(self, bb: BeamBuilder):
        self.bb = bb
        self.sequences = []
        self.static_cameras = []
        self.setup_scenario()

    @abstractmethod
    def on_recording_step(self):
        for static_camera in self.static_cameras:
            static_camera.update_position()
            # self.bb.bmng.add_debug_spheres(tuple([float(a) for a in static_camera.camera.pos]),(5,5,5),(1,1,1))
        return

    @abstractmethod
    def setup_scenario(self, steps_per_sec=24):
        return []

    def create_sequences(self, car_list=None, static_cam_list=None):
        if static_cam_list is None:
            static_cam_list = []
        if car_list is None:
            car_list = []
        sequences_list = []

        sequences_list.extend([CarSequence(us.data_path, car) for car in car_list])
        sequences_list.extend([StaticCamSequence(us.data_path, cam, cam_id) for cam, cam_id in static_cam_list])
        self.sequences = sequences_list


class WithLidarView(AbstractRecordingScenario):

    def __init__(self, bb):
        from beamngpy.visualiser import LidarVisualiser
        super().__init__(bb)
        self.lidar_vis = LidarVisualiser(Lidar.max_points)
        # self.lidar_vis.open(SIZE, SIZE)

        # glutReshapeFunc(self.lidar_resize)

    @staticmethod
    def lidar_resize(width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)

    @staticmethod
    def open_window(width, height):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        glutInitWindowSize(width, height)
        window = glutCreateWindow(b'Lidar Tour')
        WithLidarView.lidar_resize(width, height)
        return window
