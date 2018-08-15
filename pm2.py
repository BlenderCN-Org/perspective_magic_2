import bpy
import mathutils
import math
import bmesh
import random as r
from mathutils.geometry import intersect_line_plane
from bpy.props import IntProperty, FloatProperty


def calc():
    def get_mirrored_vector(point, plane_position, plane_normal):
        """Get Mirrored Vector"""
        proj = intersect_line_plane(point, point + plane_normal, plane_position, plane_normal)
        mirrored_point = 2 * proj - point
        return mirrored_point

    def get_camera_position(cl, distance):
        a = mathutils.Vector((2 * cl[0], 0, 2 * cl[2]))
        b = mathutils.Vector((-1, -8 + distance, -1))
        real_center = a + b
        return real_center

    # Parameters ##############################
    group_name = 'Group'
    picture_scale = 1
    picture_position = (0, 0)
    # camera_angle = 60
    # empty_distance = 2
    ###########################################

    frame = 0

    for camera_angle_t in range(5, 50):
        camera_angle = camera_angle_t / 50 * 120
        for empty_t in range(1, 50):
            result_array = []
            empty_distance = empty_t / 100 * 40
            for y in range(-3, 3, 1):
                for z in range(-13, -7, 1):
                    y_angle = y
                    z_angle = z

                    # Get Active Camera
                    camera = bpy.context.scene.camera.data

                    # Set Random Camera Angle
                    camera.angle = math.radians(camera_angle)

                    # Get Distance from Camera Origin to Surface
                    distance = 1 / math.tan(camera.angle / 2)

                    # Get Objects in the Group
                    objects = bpy.data.groups[group_name].objects

                    # Scale Everything
                    # Translate Everything

                    # Get Center Object
                    cl = objects['Center'].location

                    # Calculate World Location of the Center
                    # You can change this to function
                    real_center = mathutils.Vector((2 * cl[0], 0, 2 * cl[2])) + mathutils.Vector(
                        (-1, -8 + distance, -1))

                    # Camera Position, You can delete this line
                    # Get Camera Position Somehow
                    camera_position = mathutils.Vector((0, -8, 0))

                    # Get Normal from Camera Origin to the target
                    center_vector = real_center - camera_position

                    # Calculate Empty Position
                    empty_position = camera_position + center_vector * empty_distance

                    # Default Mirror Vector
                    default_norm = mathutils.Vector((1, 0, 0))

                    # Rotate
                    mat_rot_A = mathutils.Matrix.Rotation(math.radians(y_angle), 4, 'Y')
                    mat_rot_B = mathutils.Matrix.Rotation(math.radians(z_angle), 4, 'Z')
                    result = mat_rot_B * mat_rot_A

                    # bpy.data.objects['Center.dummy'].location = empty_position
                    # bpy.data.objects['Center.dummy'].rotation_euler[0] = result.to_euler('YZX')[0]
                    # bpy.data.objects['Center.dummy'].rotation_euler[1] = result.to_euler('YZX')[1]
                    # bpy.data.objects['Center.dummy'].rotation_euler[2] = result.to_euler('YZX')[2]

                    # Get Mirror Normal
                    normal = default_norm * result
                    normal = mathutils.Vector((normal[0], -normal[1], -normal[2]))

                    # Get Camera Plane Position and Normal
                    camera_plane_position = mathutils.Vector((0, -8 + distance, 0))
                    camera_plane_normal = mathutils.Vector((0, 1, 0))

                    def get_ideal_position(name):
                        # Get One Empty that Contains L and not Center
                        main = objects[name + '.L'].location
                        # Get One Empty that Contains R and not Center
                        sub = objects[name + '.R'].location

                        # Calculate Camera Position
                        main_c = get_camera_position(main, distance)
                        sub_c = get_camera_position(sub, distance)

                        if False:
                            # Force Method
                            loss_array = []
                            for i in range(0, 5000):
                                # Multiplyer
                                main_distance = i * 0.02

                                # Get Unit Normal
                                main_unit_normal = main_c - camera_position
                                main_unit_normal.normalize()

                                # Multiply Unit Normal and Calculate Position
                                moved_position = camera_position + main_unit_normal * main_distance

                                # Calculate the Mirrored Position
                                mirrored_point = get_mirrored_vector(
                                    moved_position,
                                    empty_position,
                                    normal
                                )

                                # Get Intersection Position between Camera Plane and Camera to Mirrored Position
                                insect = intersect_line_plane(camera_position, mirrored_point, camera_plane_position,
                                                              camera_plane_normal)

                                if (insect is None):
                                    continue

                                # Calculate distance between R and Mirroed Point
                                result_distance = (insect - sub_c).length

                                # Save
                                loss_array.append((moved_position.copy(), result_distance))

                            final = sorted(loss_array, key=lambda unit: unit[1])
                            return final

                        else:
                            loss_array = []

                            # Set Maximum Distance
                            max_distance = 1000
                            min_distance = 0

                            # Vector to Target Point From Camera
                            target_vector = sub_c - camera_position
                            target_vector.normalize()
                            target_vector = target_vector * max_distance

                            # Get Unit Normal
                            main_unit_normal = main_c - camera_position
                            main_unit_normal.normalize()

                            # Multiply Unit Normal and Calculate Position ##########################
                            moved_position = camera_position + main_unit_normal * 0
                            # Calculate the Mirrored Position
                            mirrored_point_A = get_mirrored_vector(
                                moved_position,
                                empty_position,
                                normal
                            )
                            ########################################################################

                            # Multiply Unit Normal and Calculate Position ##########################
                            moved_position = camera_position + main_unit_normal * max_distance
                            # Calculate the Mirrored Position
                            mirrored_point_B = get_mirrored_vector(
                                moved_position,
                                empty_position,
                                normal
                            )
                            ########################################################################

                            # Get Intersection #####################################################
                            t_result = mathutils.geometry.intersect_line_line(camera_position, target_vector,
                                                                              mirrored_point_A, mirrored_point_B)
                            fff_result = get_mirrored_vector(
                                mathutils.Vector(t_result[1]),
                                empty_position,
                                normal
                            )
                            ########################################################################

                            loss_array.append((
                                fff_result.copy(),
                                (mathutils.Vector(t_result[1]) - mathutils.Vector(t_result[0])).length
                            ))
                            final = sorted(loss_array, key=lambda unit: unit[1])
                            return final

                    final_array = []
                    total_loss = 0
                    for tmp in objects:
                        if tmp.name.endswith('.L'):
                            name = tmp.name.replace('.L', '')
                            final_t = get_ideal_position(name)
                            # Square 2 Loss
                            total_loss += math.pow(final_t[0][1], 2)
                            # Average
                            # total_loss += math.pow(final_t[0][1],1)


                            final_array.append(final_t)
                    total_loss = total_loss / (2 * len(final_array))
                    print(total_loss)

                    position_array = [l[0][0] for l in final_array]
                    result_array.append((y_angle, z_angle, position_array, total_loss))
            if True:
                # Sort Result on Every Possible Angle
                real_final = sorted(result_array, key=lambda unit: unit[3])

                bpy.data.objects['bar'].location[2] = real_final[0][3] * 10000
                bpy.data.objects['bar'].keyframe_insert(data_path="location", frame=frame)

                # Move Center
                bpy.data.objects['Center.dummy'].location = empty_position
                bpy.data.objects['Center.dummy'].rotation_euler[0] = 0
                bpy.data.objects['Center.dummy'].rotation_euler[1] = math.radians(real_final[0][0])
                bpy.data.objects['Center.dummy'].rotation_euler[2] = math.radians(real_final[0][1])
                bpy.data.objects['Center.dummy'].keyframe_insert(data_path="location", frame=frame)
                bpy.data.objects['Center.dummy'].keyframe_insert(data_path="rotation_euler", frame=frame)
                # Move Points
                for i, unit in enumerate(real_final[0][2]):
                    fobj = bpy.data.objects['tmp.' + str(i).rjust(3, '0')]
                    fobj.location = unit
                    fobj.keyframe_insert(data_path="location", frame=frame)

                print(real_final[0][0], real_final[0][1], real_final[0][3])
                frame += 1
                print('FRAME : ', frame)
                print('Loss : ', real_final[0][3] * 10000)

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

# Make empty bones that have same names with empties
# tmp.000, tmp.001, tmp.002...
# Move Bones to Corresponding Positions by Empty Name
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
        camera_position = mathutils.Vector((0, -8, 0))

        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        for vert in bm.verts:
            if vert.select is True:
                mat_world = obj.matrix_world
                pos_world = mat_world * vert.co
                tmp = pos_world - camera_position
                tmp.normalize()
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
            self.camera_position = mathutils.Vector((0, -8, 0))
            self.mesh = self.obj.data
            self.bm = bmesh.from_edit_mesh(self.mesh)
            self.mat_world = self.obj.matrix_world
            for vert in self.bm.verts:
                if vert.select is True:
                    self.first_value = vert.co.copy()
                    pos_world = self.mat_world * vert.co
                    self.tmp = pos_world - self.camera_position
                    self.tmp.normalize()
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