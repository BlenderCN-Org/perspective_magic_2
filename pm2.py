import bpy
import math
from math import radians
import bmesh
# import random as r
# import mathutils
from mathutils.geometry import intersect_line_plane
from mathutils.geometry import intersect_line_line
from mathutils import Vector
from mathutils import Matrix
from bpy.props import IntProperty, FloatProperty


def move_empties_back(group_name):
    for object in bpy.data.groups[group_name].objects:
        zcord = None
        xcord = 0
        if object.name.endswith('.L'):
            xcord = 0
            zcord = 1 - int(object.name.split('.')[1]) * 0.02
        elif object.name.endswith('.R'):
            xcord = 0.02
            zcord = 1 - int(object.name.split('.')[1]) * 0.02
        else:
            continue

        object.location = Vector((xcord, 0, zcord))

def calc():
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

    def move_empties_by_verticies():
        mesh = bmesh.from_edit_mesh(bpy.context.object.data)
        for v in mesh.verts:
            world_cordinate = v.co
            rm = Matrix.Rotation(bpy.data.objects['Center.dummy'].rotation_euler[1], 4, 'Y') * Matrix.Rotation(bpy.data.objects['Center.dummy'].rotation_euler[2], 4, 'Z')
            normal = Vector((1, 0, 0)) * rm
            normal = Vector((normal[0], -normal[1], -normal[2]))
            mirrored_cordinate = get_mirrored_vector(world_cordinate, bpy.data.objects['Center.dummy'].location , normal)
            print(world_cordinate, mirrored_cordinate)

            # here calculate thingy like intersection point

        pass

    move_empties_by_verticies()
    return 0

    # Prerequisitions ####################################################
    # First, You need to place empties
    # name.001.L / name.002.R
    # and Center
    # And you have to make everithing Xray
    # You have to add those empties to Group
    # Place Active Camera on 0, -8, 0
    # Place Object Called Deform(Optional)
    # Place Center.dummy and bar
    # And Place tmp


    # Example Parameters #####################
    # best_result_preset = {
    #     y_angle: -2,
    #     z_angle: -30,
    #     viewing_angle: 24,
    #     center_distance: 22
    # }
    ###########################################

    # Parameters ##############################
    empty_group_name = 'Group'
    empty_group_important = 'Important'
    empty_group_not_important = 'Not'

    camera_angle_range = [24]
    empty_distance_range = [22]
    y_angle_range = range(-20, 0, 1)
    z_angle_range = range(-20, 0, 1)
    y_angle_division = 1
    z_angle_division = 1
    # angle_example_amount = None
    angle_example_amount = None
    ###########################################

    # Global Variables
    frame = 0

    # Get Camera Position
    camera_position = bpy.context.scene.camera.location

    # Get Objects in the Group
    objects = bpy.data.groups[empty_group_name].objects

    # Got to Edit Mode o Armature
    scene = bpy.context.scene
    scene.layers = [True] * 20  # Show all layers
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    scene.objects.active = bpy.data.objects['Armature']
    scene.objects.active.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.data.armatures['Armature'].edit_bones[0].head[0] = 10

    # Move Everything to Default
    for bone in bpy.data.armatures['Armature'].edit_bones:
        bone.head = Vector((0, 0 , 0))
        bone.tail = Vector((0, 0, 0.1))

    # Move Edit Bones to the Position
    for t_object in objects:
        if t_object.name.endswith('.R'):
            name = t_object.name.replace('.R', '').replace('aaa.', '')
            bpy.data.armatures['Armature'].edit_bones['tmp.' + name].head = t_object.location
            bpy.data.armatures['Armature'].edit_bones['tmp.' + name].tail = t_object.location + Vector((0,0,0.1))

    # Go Back to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    try:
        scene.objects.active = bpy.data.objects['Template.001']
        scene.objects.active.select = True
        bpy.ops.object.delete(use_global=False)
    except:
        print('ERROR')

    bpy.ops.object.select_all(action='DESELECT')
    scene.objects.active = bpy.data.objects['Template']
    scene.objects.active.select = True
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                  TRANSFORM_OT_translate={"value": (0, 0, 0), "constraint_axis": (False, False, False),
                                                          "constraint_orientation": 'GLOBAL', "mirror": False,
                                                          "proportional": 'DISABLED',
                                                          "proportional_edit_falloff": 'SMOOTH', "proportional_size": 1,
                                                          "snap": False, "snap_target": 'CLOSEST',
                                                          "snap_point": (0, 0, 0), "snap_align": False,
                                                          "snap_normal": (0, 0, 0), "gpencil_strokes": False,
                                                          "texture_space": False, "remove_on_cancel": False,
                                                          "release_confirm": False, "use_accurate": False})
    bpy.ops.object.move_to_layer(layers=(
    True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
    False, False, False, False))

    bpy.ops.object.select_all(action='DESELECT')
    scene.objects.active = bpy.data.objects['Template.001']
    scene.objects.active.select = True
    bpy.ops.object.mode_set(mode='EDIT')

    mesh = bmesh.from_edit_mesh(bpy.context.object.data)

    # In here, check the cordination of each verticies and find the corresponding bone
    index_name = {}
    for v in mesh.verts:
        index_num = v.index
        bone_name = None
        for bone in bpy.data.armatures['Armature'].bones:
            distance = (bone.head - v.co).length
            if distance < 0.01:
                bone_name = bone.name
        index_name[str(index_num)] = bone_name

    ################################################################
    for i, v2 in enumerate(mesh.verts):
        group_name = index_name[str(v2.index)]
        i = 0
        for v in mesh.verts:
            v.select = False
            print(v.index)
            if v.index == v2.index:
                v.select = True
        bpy.ops.object.vertex_group_add()
        bpy.context.object.vertex_groups.active.name = group_name
        bpy.ops.object.vertex_group_assign()
    ################################################################

    bpy.context.scene.objects.active = bpy.context.scene.objects.active

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
                y_angle = y_angle / y_angle_division
                for z_angle in z_angle_range:
                    z_angle = z_angle / z_angle_division
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
                        main_c = camera_position_array[empty_name + '.R']
                        sub_c = camera_position_array[empty_name + '.L']
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
                        # Here, You have to get position on the screen
                        insect = intersect_line_plane(
                            camera_position,
                            Vector(intersection[1]),
                            Vector((0, -8 + distance, 0)),
                            Vector((0, 1, 0))
                        )
                        # If it's not intersecting, just return ridiculous value
                        if (insect is None):
                            insect = Vector((100, 100 ,100))

                        return mirrored_intersection, (insect - sub_c).length

                    # Calculate Closest Position on each Empty and Get Total Loss on the Angle #########################
                    position_array = []
                    total_loss = 0
                    for t_object in objects:
                        if t_object.name.endswith('.R'):
                            name = t_object.name.replace('.R', '')
                            idea_position = get_ideal_position(name)
                            if any([i.name == 'Important' for i in t_object.users_group]):
                                total_loss += math.pow(idea_position[1], 2)

                            position_array.append([name.replace('aaa.', ''), idea_position[0]])

                    total_loss /= 2 * len(position_array)
                    result_array.append((y_angle, z_angle, position_array, total_loss))
                    ###################################################################################################

            ############################################################################################################
            # Visualizing Section ######################################################################################
            best_list = sorted(result_array, key=lambda unit: unit[3])

            for counter, best_result_of_angle in enumerate(best_list):
                if counter is angle_example_amount:
                    break

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
                # You can delete Number later
                for number, unit in enumerate(best_result_of_angle[2]):
                    tmp = unit[1] - bpy.data.objects['aaa.' + str(unit[0]).rjust(3, '0') + '.R'].location
                    bpy.data.objects['Armature'].pose.bones['tmp.' + str(unit[0]).rjust(3, '0')].location[0] = tmp[0]
                    bpy.data.objects['Armature'].pose.bones['tmp.' + str(unit[0]).rjust(3, '0')].location[1] = tmp[2]
                    bpy.data.objects['Armature'].pose.bones['tmp.' + str(unit[0]).rjust(3, '0')].location[2] = -tmp[1]
                    bpy.data.objects['Armature'].pose.bones['tmp.' + str(unit[0]).rjust(3, '0')].keyframe_insert(data_path="location", frame=frame)
                    # tmp_obj = bpy.data.objects['tmp.' + str(unit[0]).rjust(3, '0')]
                    # tmp_obj.location = unit[1]
                    # tmp_obj.keyframe_insert(data_path="location", frame=frame)

                # Display Result
                print('#' * 100)
                print('# FRAME : ', frame)
                print('# Parameters')
                print(camera_angle, empty_distance)
                print('# Best Angle and Total Loss (Times 10000)')
                print(best_result_of_angle[0], best_result_of_angle[1], best_result_of_angle[3] * 10000)

                frame += 1

            print('#' * 100)
            print('# Ranking')
            for unit in best_list:
                print(unit[0],unit[1],unit[3])
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

    # def move_vert_by_camera_norm(distance):
    #     obj = bpy.context.object
    #     camera_position = Vector((0, -8, 0))
    #
    #     mesh = obj.data
    #     bm = bmesh.from_edit_mesh(mesh)
    #     for vert in bm.verts:
    #         if vert.select is True:
    #             mat_world = obj.matrix_world
    #             pos_world = mat_world * vert.co
    #             tmp = (pos_world - camera_position).normalized()
    #             pos_world += tmp * distance
    #             vert.co = mat_world.inverted() * pos_world
    #     bmesh.update_edit_mesh(mesh)

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            delta = self.first_mouse_x - event.mouse_x

            # Change Here ###############################################
            # context.object.location.x = self.first_value + delta * 0.01
            for vert in self.bm.verts:
                if vert.select is True:
                    rep = self.vert_array[vert.index]
                    pos_world = self.mat_world * rep['first_value'] + rep['tmp'] * delta * -0.0005
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
                    vert.co = self.vert_array[vert.index]['first_value']
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

            self.vert_array = {}

            for vert in self.bm.verts:
                if vert.select is True:
                    self.vert_array[vert.index] = {}
                    self.vert_array[vert.index]['first_value'] = vert.co.copy()
                    self.vert_array[vert.index]['pos_world'] = self.mat_world * vert.co
                    self.vert_array[vert.index]['tmp'] = (self.vert_array[vert.index]['pos_world'] - self.camera_position).normalized()
                    # self.first_value = vert.co.copy()
                    # pos_world = self.mat_world * vert.co
                    # self.tmp = (pos_world - self.camera_position).normalized()
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