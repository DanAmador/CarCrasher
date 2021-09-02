from abc import ABC, abstractmethod

from OpenGL.GL import *
from OpenGL.GLUT import *
from beamngpy.sensors import Lidar

import src.BeamBuilder as BeamBuilder
from src.CustomScenarios.SceneData import SceneData


class AbstractRecordingScenario(ABC):

    def __init__(self, bb: BeamBuilder):
        self.bb: BeamBuilder = bb
        self.sequences = []
        self.initialize_scenario()

    def should_record_predicate(self) -> bool:
        return False


    @abstractmethod
    def setup_scenario(self) -> SceneData:
        return None

    def initialize_scenario(self):
        scene_data = self.setup_scenario()
        print(scene_data)
        self.sequences = scene_data.get_sequence_list()


class WithLidarView(AbstractRecordingScenario, ABC):

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
