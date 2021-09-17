import bpy
import os

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from pathlib import Path
import json
import math
class OT_TestOpenFilebrowser(Operator, ImportHelper):

    bl_idname = "test.open_filebrowser"
    bl_label = "Open the file browser (yay)"
    
    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'}
    )
    

    def execute(self, context):
        """Do something with the selected file(s)."""

        filename, extension = os.path.splitext(self.filepath)
        p = Path(self.filepath)
        
        camera_path = json.loads(p.read_text())
        project_camera = None

        if "ProjectCamera" not in  bpy.data.objects:
            camera_data = bpy.data.cameras.new(name='ProjectCamera')
            camera_object = bpy.data.objects.new('ProjectCamera', camera_data)
            bpy.context.scene.collection.objects.link(camera_object)
        
        project_camera = bpy.data.objects["ProjectCamera"]

        project_camera.select_set(True)    
        bpy.context.view_layer.objects.active = project_camera
        for frame,cam in enumerate(camera_path):
            bpy.context.scene.frame_set(frame)

            project_camera.location = tuple(cam["position"])
            project_camera.keyframe_insert('location')
            
            rot = cam["rotation"]
            # z = rot[2]
            # rot[2] = rot[1]
            # rot[1] = z
            rot[0] = rot[0] + math.radians(59)
            rot[2] = -rot[2] + math.radians(20.6)
            project_camera.rotation_euler = tuple(rot)
            project_camera.keyframe_insert('rotation_euler')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(OT_TestOpenFilebrowser)


def unregister():
    bpy.utils.unregister_class(OT_TestOpenFilebrowser)


if __name__ == "__main__":
    register()

    bpy.ops.test.open_filebrowser('INVOKE_DEFAULT')