import bpy
import math
from math import radians
import bmesh
# import random as r
# import mathutils
import decimal
from mathutils.geometry import intersect_line_plane
from mathutils.geometry import intersect_line_line
from mathutils import Vector
from mathutils import Matrix
from bpy.props import IntProperty, FloatProperty


def calc():
    def drange(x, y, jump):
        while x < y:
            yield float(x)
            x += decimal.Decimal(jump)

    def get_mirrored_vector(point, plane_position, plane_normal):
        """Get Mirrored Vector"""
        proj = intersect_line_plane(point, point + plane_normal, plane_position, plane_normal)
        mirrored_point = 2 * proj - point
        return mirrored_point

    def get_camera_position(location, distance):
        a = Vector((2 * location[0], 0, 2 * location[2]))
        b = Vector((-1, -8 + distance, -1))
        return a + b

    def get_range(total_steps, max_value, start=0, stop=None):
        if stop is None:
            stop = total_steps
        return [x / total_steps * max_value for x in range(start, stop)]

    # Parameters ##############################
    empty_group_name = 'Group'
    camera_angle_range = get_range(10, 120, 1) 
    empty_distance_range = get_range(10, 100, 1)
    y_angle_range = range(-3, 3, 1)
    z_angle_range = range(-13, -7, 1)
    ###########################################

    # Global Variables
    frame = 0

    # Get Camera Position
    camera_position = bpy.context.scene.camera.location

    # Get Objects in the Group
    objects = bpy.data.groups[empty_group_name].objects

    for camera_angle in camera_angle_range:
        # Set Camera Angle
        bpy.context.scene.camera.data.angle = radians(camera_angle)

        # Calculate Distance
        distance = 1 / math.tan(bpy.context.scene.camera.data.angle / 2)

        # Get Normal from Camera Origin to the target
        center_vector = (get_camera_position(objects['Center'].location, distance) - camera_position).normalized()

        # Calculate Camera Positions of Empties
        camera_position_array = {}
        for t_object in objects:
            if t_object.name.endswith('.L') or t_object.name.endswith('.R'):
                camera_position_array[t_object.name] = get_camera_position(t_object.location, distance)

        for empty_distance in empty_distance_range:
            # Calculate Empty Position
            empty_position = camera_position + center_vector * empty_distance

            # Get Best Angle
            result_array = []
            for y_angle in y_angle_range:
                for z_angle in z_angle_range:
                    # Rotation Matrix
                    rm = Matrix.Rotation(radians(y_angle), 4, 'Y') * Matrix.Rotation(radians(z_angle), 4, 'Z')
                    # Get Mirror Normal
                    normal = Vector((1, 0, 0)) * rm
                    # You Need to Tweak Somehow
                    normal = Vector((normal[0], -normal[1], -normal[2]))

                    def get_ideal_position(empty_name):
                        # Set Maximum Distance
                        max_distance = 1000
                        # Get Empty Positions
                        main_c = camera_position_array[empty_name + '.L']
                        sub_c = camera_position_array[empty_name + '.R']
                        # Vector to Target Point From Camera
                        target_vector = (sub_c - camera_position).normalized() * max_distance
                        # Get Line
                        A = get_mirrored_vector(camera_position, empty_position, normal)
                        B = get_mirrored_vector(
                            camera_position + (main_c - camera_position).normalized() * max_distance,
                            empty_position, normal
                        )
                        # Calculate Intersection
                        intersection = intersect_line_line(camera_position, target_vector, A, B)
                        mirrored_intersection = get_mirrored_vector(Vector(intersection[1]), empty_position, normal)
                        return mirrored_intersection, (Vector(intersection[1]) - Vector(intersection[0])).length

                    # Calculate Closest Position on each Empty and Get Total Loss on the Angle #########################
                    position_array = []
                    total_loss = 0
                    for t_object in objects:
                        if t_object.name.endswith('.L'):
                            name = t_object.name.replace('.L', '')
                            idea_position = get_ideal_position(name)
                            total_loss += math.pow(idea_position[1], 2)
                            position_array.append(idea_position[0])

                    total_loss /= 2 * len(position_array)
                    result_array.append((y_angle, z_angle, position_array, total_loss))
                    ###################################################################################################

            ############################################################################################################
            # Visualizing Section ######################################################################################
            best_result_of_angle = sorted(result_array, key=lambda unit: unit[3])[0]

            # Visualize Total Loss
            bar = bpy.data.objects['bar']
            bar.location[2] = best_result_of_angle[3] * 10000
            # Save Camera Angle as Z Rotation
            bar.rotation_euler[2] = math.radians(camera_angle)
            bar.keyframe_insert(data_path="location", frame=frame)
            bar.keyframe_insert(data_path="rotation_euler", frame=frame)

            # Move Center
            cd = bpy.data.objects['Center.dummy']
            cd.location = empty_position
            cd.rotation_euler[0] = 0
            cd.rotation_euler[1] = math.radians(best_result_of_angle[0])
            cd.rotation_euler[2] = math.radians(best_result_of_angle[1])
            cd.keyframe_insert(data_path="location", frame=frame)
            cd.keyframe_insert(data_path="rotation_euler", frame=frame)

            # Move Points
            for number, unit in enumerate(best_result_of_angle[2]):
                tmp_obj = bpy.data.objects['tmp.' + str(number).rjust(3, '0')]
                tmp_obj.location = unit
                tmp_obj.keyframe_insert(data_path="location", frame=frame)

            # Display Result
            print('#' * 100)
            print('# FRAME : ', frame)
            print('# Parameters')
            print(camera_angle, empty_distance)
            print('# Best Angle and Total Loss (Times 10000)')
            print(best_result_of_angle[0], best_result_of_angle[1], best_result_of_angle[3] * 10000)

            frame += 1
            ############################################################################################################
            ############################################################################################################

if False:
    for i in range(0, len(bpy.context.selected_objects)):
        if i % 2 == 0:
            bpy.context.selected_objects[i].name = str(i) + '.L'
            bpy.context.selected_objects[i + 1].name = str(i) + '.R'
        else:
            continue

if False:
    for i in range(0, len(bpy.context.selected_objects)):
        bpy.context.selected_objects[i].name += '.L'

if False:
    for object in bpy.data.objects:
        if 'tmp.' in object.name:
            bpy.data.objects['MainArm'].pose.bones[object.name].location = object.location


class ModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"

    first_mouse_x = IntProperty()

    # first_value = FloatProperty()

    def move_vert_by_camera_norm(distance):
        obj = bpy.context.object
        camera_position = Vector((0, -8, 0))

        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        for vert in bm.verts:
            if vert.select is True:
                mat_world = obj.matrix_world
                pos_world = mat_world * vert.co
                tmp = (pos_world - camera_position).normalized()
                pos_world += tmp * distance
                vert.co = mat_world.inverted() * pos_world
        bmesh.update_edit_mesh(mesh)

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            delta = self.first_mouse_x - event.mouse_x

            # Change Here ###############################################
            # context.object.location.x = self.first_value + delta * 0.01
            for vert in self.bm.verts:
                if vert.select is True:
                    pos_world = self.mat_world * self.first_value + self.tmp * delta * -0.0025
                    vert.co = self.mat_world.inverted() * pos_world
            bmesh.update_edit_mesh(self.mesh)
            #############################################################

        elif event.type == 'LEFTMOUSE':
            # Change Here ###############################################
            bmesh.update_edit_mesh(self.mesh)
            #############################################################
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # Change Here ###############################################
            for vert in self.bm.verts:
                if vert.select is True:
                    vert.co = self.first_value
            bmesh.update_edit_mesh(self.mesh)
            #############################################################
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            self.first_mouse_x = event.mouse_x
            ############################################################
            self.obj = bpy.context.object
            self.camera_position = Vector((0, -8, 0))
            self.mesh = self.obj.data
            self.bm = bmesh.from_edit_mesh(self.mesh)
            self.mat_world = self.obj.matrix_world
            for vert in self.bm.verts:
                if vert.select is True:
                    self.first_value = vert.co.copy()
                    pos_world = self.mat_world * vert.co
                    self.tmp = (pos_world - self.camera_position).normalized()
            context.window_manager.modal_handler_add(self)
            ############################################################
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


addon_keymaps = []


def register():
    bpy.utils.register_class(ModalOperator)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    key_assign_list = [(ModalOperator.bl_idname, "Q", "PRESS", False, False, False)]
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        for (idname, key, event, ctrl, alt, shift) in key_assign_list:
            kmi = km.keymap_items.new(idname, key, event, ctrl=ctrl, alt=alt, shift=shift)
            addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(ModalOperator)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()