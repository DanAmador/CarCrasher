"""
.. module:: lidar_tour
    :platform: Windows
    :synopsis: Example starting in west_coast_usa with a vehicle that has a
               Lidar attached and drives around the environment using the
               builtin AI. Lidar data is displayed using the OpenGL-based
               Lidar visualiser.

.. moduleauthor:: Marc Müller <mmueller@beamng.gmbh>

"""

import sys

from time import sleep


import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from beamngpy import BeamNGpy, Scenario, Vehicle, setup_logging
from beamngpy.sensors import Lidar
from beamngpy.visualiser import LidarVisualiser
from BeamBuilder import BeamBuilder
from config import Levels, Cars

SIZE = 1024


def lidar_resize(width, height):
    if height == 0:
        height = 1

    glViewport(0, 0, width, height)


def open_window(width, height):
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(width, height)
    window = glutCreateWindow(b'Lidar Tour')
    lidar_resize(width, height)
    return window


def main():
    setup_logging()

    
    bb = BeamBuilder(launch=True, scenario_name="Lidar Tour")


    bb.car_setup(car=Cars.ETK, pos=(-717.121, 101, 118.675), rot_quat=(0, 0, 0.3826834, 0.9238795), sensors={"lidar": Lidar()})



    try:
        bb.build_environment(ai_mode="span")

        window = open_window(SIZE, SIZE)
        lidar_vis = LidarVisualiser(Lidar.max_points)
        #lidar_vis.open(SIZE, SIZE)

        bb.bmng.pause()

        #def update():
        #    bb.vehicle.poll_sensors()
        #    points = lidar.data['points']
        #    bb.bmng.step(3, wait=False)
        #    lidar_vis.update_points(points, vehicle.state)
        #    glutPostRedisplay()
        #glutReshapeFunc(lidar_resize)
        #glutIdleFunc(update)
        #glutMainLoop()
    finally:
        print("this shit crashed")
        #bb.bmng.close()


if __name__ == '__main__':
    main()
