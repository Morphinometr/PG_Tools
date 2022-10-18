import bpy, mathutils
from bpy.types import Operator, PropertyGroup
from bpy.props import EnumProperty, BoolProperty, IntProperty, FloatProperty, StringProperty, BoolVectorProperty
from .Utils import *

#   Custom properties

class PG_properties(bpy.types.PropertyGroup):
    
    tex_size : EnumProperty(
        name = 'Texture Dimentions', 
        items = [('16', '16x16', ''),
                 ('32', '32x32', ''),
                 ('64', '64x64', ''),
                 ('128', '128x128', ''),
                 ('256', '256x256', ''),
                 ('512', '512x512', ''),
                 ('1024', '1024x1024', ''),
                 ('2048', '2048x2048', ''),
                 ('4096', '4096x4096', ''),
                 ('custom', 'Custom', '')
                ],
        default = '64'
        )
    
    px_density : EnumProperty(
        name = 'Pixel Density',
        items = [('10', '10 px/m', ''),
                 ('16', '16 px/m', ''),
                 ('32', '32 px/m', ''),
                 ('1000', '1000 px/m', ''),
                 ('custom', 'Custom', ''),
                ],
        default = '16'
        )
        
    px_density_custom : FloatProperty(name="Custom Pixel Density", min = 0 )
    tex_size_custom_y : IntProperty(name="Custom texture size Y", min = 1, default = 64 )
    tex_size_custom_x : IntProperty(name="Custom texture size X", min = 1, default = 64 )
    reset_colors : BoolProperty(name="Reset Colors", default = False)
    
    weapon_tag : StringProperty(name="Weapon Tag", default = "")
    weapon_number : StringProperty(name="Weapon Number", default = "")
    avatar_tag : StringProperty(name="Avatar Tag", default = "")
    
    

#   Operators    
#   Modeling

class PG_OT_find_instances(Operator):
    """Detects objects that shares data mesh and assignes random object color"""
    bl_label = "Find Instances"
    bl_idname = "pg.find_instances"
    bl_options = {'REGISTER', 'UNDO'}

    reset_colors : BoolProperty(name="Reset Colors", default = False)

    def invoke(self, context, event):
        self.reset_colors = context.scene.pg_tool.reset_colors
                            
        return self.execute(context)

    def execute(self, context):
        meshes = []
        context.scene.pg_tool.reset_colors = self.reset_colors
        
        #instantiated_meshes = [mesh if mesh.users > 1 else pass for mesh in bpy.data.meshes]
        #[print(i) for i in x if i>3 ]
        for mesh, data in bpy.data.meshes.items():
            if bpy.data.meshes[mesh].users > 1:
                meshes.append(mesh)
                
        #Calculate how many color steps we need to cover all variations 
        col_steps = ((len(meshes) + 1) ** (1/3) ) // 1 
        
        if self.reset_colors:
            bpy.ops.pg.reset_ob_colors()

        try:
            col_lst = color_list(len(meshes), col_steps)
        except ValueError as ex:
            self.report({'ERROR'}, str(ex))
            return {'CANCELLED'}
        
        
        color_dict = dict(zip(meshes, col_lst))

        for ob in context.scene.objects:
            if ob.data.name in color_dict.keys():
                ob.color = color_dict[ob.data.name]
                ob.select_set(True)
        
        context.space_data.shading.color_type = 'OBJECT'

        return {'FINISHED'}

class PG_OT_reset_ob_colors(Operator):
    """Resets all object colors in the scene"""
    bl_label = "Reset Object Colors"
    bl_idname = "pg.reset_ob_colors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for ob in context.scene.objects:
            ob.color = (1,1,1,1)
        
        return {'FINISHED'}


class PG_OT_optimize(Operator):
    """Limited dissolve, weld and set sharp selected objects"""
    bl_label = "Optimize"
    bl_idname = "pg.optimize"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None:
            return False
        
        return (context.area.type == 'VIEW_3D' and 
                context.active_object.select_get() and
                context.active_object.type == 'MESH' 
                )
    
    def execute(self, context):
        mod = context.object.mode
        bpy.ops.object.mode_set_with_submode(mode='EDIT')
        
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.dissolve_limited()
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.normals_tools(mode='RESET')
        bpy.ops.mesh.mark_sharp(clear=True)
        bpy.ops.mesh.faces_shade_flat()

        bpy.ops.object.mode_set_with_submode(mode=mod)
       
        return {'FINISHED'}

class PG_OT_unwrap(Operator):
    """Unwrap mesh"""
    bl_label = "Unwrap"
    bl_idname = "pg.unwrap"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None:
            return False
        
        return (context.area.type == 'VIEW_3D' and 
                context.active_object.type == 'MESH' and 
                context.active_object.select_get()
                )
            
    def execute(self, context):
        mod = context.object.mode
        bpy.ops.object.mode_set_with_submode(mode='EDIT')
        
        bpy.ops.mesh.select_mode(type="EDGE")
        bpy.ops.mesh.select_all(action = 'DESELECT')
        
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)

        #unwrap
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0)

        
        bpy.ops.object.mode_set_with_submode(mode=mod)
    
        return {'FINISHED'}

class PG_OT_test_material(Operator):
    """Add test meterial"""
    bl_label = "Test Material"
    bl_idname = "pg.test_material"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None:
            return False
        
        return (context.area.type == 'VIEW_3D' and
                context.active_object.type == 'MESH' and 
                context.active_object.select_get()
                )
            
    def execute(self, context):
                
        if bpy.data.materials.find("Test Material") < 0:
            #create test material
            test_mat = create_mat("Test Material")
        else: test_mat = bpy.data.materials.get("Test Material")
        
            
        #append to selected objects
        for ob in bpy.context.selected_objects :
            ob.active_material = test_mat
                   
        return {'FINISHED'}
    
class PG_OT_test_texture(Operator):
    """Add test texture"""
    bl_label = "Set Texture"
    bl_idname = "pg.test_texture"
    bl_options = {'REGISTER', 'UNDO'}
    
    size : EnumProperty(
        name = 'Texture Dimentions', 
        items = [('16', '16x16', ''),
                 ('32', '32x32', ''),
                 ('64', '64x64', ''),
                 ('128', '128x128', ''),
                 ('256', '256x256', ''),
                 ('512', '512x512', ''),
                 ('1024', '1024x1024', ''),
                 ('2048', '2048x2048', ''),
                 ('4096', '4096x4096', ''),
                 ('custom', 'Custom', '')
                ],
        default = '64'
        )
        
    tex_size_x : IntProperty(name="Custom texture size X", min = 1, default = 64 )
    tex_size_y : IntProperty(name="Custom texture size Y", min = 1, default = 64 )
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None:
            return False
        
        if bpy.data.materials.find("Test Material") < 0:
            return False
        
        return context.area.type == 'VIEW_3D' and context.active_object.type == 'MESH' and context.active_object.select_get()
            
    
    def invoke(self, context, event):
        scene = context.scene
        pg_tool = scene.pg_tool
        self.size = pg_tool.tex_size
        self.tex_size_x = pg_tool.tex_size_custom_x
        self.tex_size_y = pg_tool.tex_size_custom_y
                    
        return self.execute(context)
        
    def execute(self, context):
        scene = context.scene
        pg_tool = scene.pg_tool
         #Custom tex size!
        if self.size != 'custom':
            self.tex_size_x = self.tex_size_y = int(self.size)
            pg_tool.tex_size_custom_x = pg_tool.tex_size_custom_y = int(self.size)
        
        #test texture add
        tex_name = "Test " + str(self.tex_size_x) + 'x' + str(self.tex_size_y)
                
        if bpy.data.images.find(tex_name) < 0:
            texture = bpy.ops.image.new(name= tex_name, width=self.tex_size_x, height=self.tex_size_y, generated_type='COLOR_GRID')
        
        test_mat = bpy.data.materials["Test Material"]
        test_image_node = test_mat.node_tree.nodes["Image Texture"] #FIXME: take texture in 'base color' node
        test_image_node.image = bpy.data.images[tex_name]
        
        #bake texture add
        texture = bpy.data.images.new(name= 'Bake', width=self.tex_size_x, height=self.tex_size_y, alpha=True)
        texture.generated_color = (0, 0, 0, 0)

        bake_image_node = test_mat.node_tree.nodes["Bake"] #FIXME
        bake_image_node.image = texture
        
        set_td_size(scene, scene.pg_tool.tex_size_custom_x, scene.pg_tool.tex_size_custom_y)
        
        return {'FINISHED'}

class PG_OT_texture_pixel_filter(Operator):
    """Set pixel interpolation mode to "Closest" for all textures of selected objects"""
    bl_label = "Make pixelated"
    bl_idname = "pg.texture_pixel_filter"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None and len(context.selected_objects) < 1:
            return False
        return True
            
    def execute(self, context):
        texture_pixel_filter(context)
        
        return {'FINISHED'}
 
class PG_OT_reload_textures(Operator):
    """Reload textures"""
    bl_label = "Reload Textures"
    bl_idname = "pg.reload_textures"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None and len(context.selected_objects) < 1:
            return False
        return True
        
#        return (context.area.type == 'VIEW_3D' and 
#                context.active_object.type == 'MESH' and 
#                context.active_object.select_get()
#                )
            
    def execute(self, context):
        materials = get_materials(context)
        textures = get_textures(materials)
        
        for tex in textures:
            if tex.image is not None:
                tex.image.reload()
    
        return {'FINISHED'}
    
#   Interaraction with texel density addon

class PG_OT_set_tex_desity(Operator):
    """Set texel density for selected faces"""
    bl_label = "Set Texel Density"
    bl_idname = "pg.set_tex_desity"
    bl_options = {'REGISTER', 'UNDO'}
    
    size : EnumProperty(
        name = 'Texture Dimentions', 
        items = [('16', '16x16', ''),
                 ('32', '32x32', ''),
                 ('64', '64x64', ''),
                 ('128', '128x128', ''),
                 ('256', '256x256', ''),
                 ('512', '512x512', ''),
                 ('1024', '1024x1024', ''),
                 ('2048', '2048x2048', ''),
                 ('4096', '4096x4096', ''),
                 ('custom', 'Custom', '')
                ],
        default = '64'
        )
        
    tex_size_x : IntProperty(name="Custom texture size X", min = 1, default = 64 )
    tex_size_y : IntProperty(name="Custom texture size Y", min = 1, default = 64 )
    
    density : bpy.props.EnumProperty(
        name = 'Pixel Density',
        items = [('10', '10 px/m', ''),
                 ('16', '16 px/m', ''),
                 ('32', '32 px/m', ''),
                 ('1000', '1000 px/m', ''),
                 ('custom', 'custom', ''),
                ],
        default = '16'
        )
        
    density_custom : bpy.props.FloatProperty(name="Custom Pixel Density") 
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None:
            return False
        
        return True
            
    
    def invoke(self, context, event):
        scene = context.scene
        pg_tool = scene.pg_tool
        self.size = pg_tool.tex_size
        self.tex_size_x = pg_tool.tex_size_custom_x
        self.tex_size_y = pg_tool.tex_size_custom_y

        self.density = context.scene.pg_tool.px_density
        self.density_custom = context.scene.pg_tool.px_density_custom
                    
        return self.execute(context)
        
    def execute(self, context):
        scene = context.scene
        pg_tool = scene.pg_tool
        scene.td.units = '1'
        scene.td.texture_size = '4'
        scene.td.set_method = '0'

         #Custom tex size!
        if self.size != 'custom':
            self.tex_size_x = self.tex_size_y = int(self.size)
            pg_tool.tex_size_custom_x = pg_tool.tex_size_custom_y = int(self.size)

        set_td_size(scene, scene.pg_tool.tex_size_custom_x, scene.pg_tool.tex_size_custom_y)

        if scene.pg_tool.px_density == 'custom':
            scene.td.density_set = str(scene.pg_tool.px_density_custom)
        else:
            scene.td.density_set = scene.pg_tool.px_density
        
        bpy.ops.object.texel_density_set()

        return {'FINISHED'}
            
               
#   Layout

#   Import
class PG_OT_import_weapon(Operator):
    """Import Weapon by its Tag"""
    bl_label = "Import Weapon"
    bl_idname = "pg.import_weapon"
    bl_options = {'REGISTER', 'UNDO'}

    weapon_tag : StringProperty(name = "Weapon tag" )
    pixelize : BoolProperty(name = "Pixelize", description = "Make imported textures pixelated", default = True)
    fix_materials : BoolProperty(name = "Flatten materaials", description = "set 0 in metallness, specular, emission properties in imported materials", default = True)

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D" and context.mode == "OBJECT"

    def invoke(self, context, event):
        self.weapon_tag = context.scene.pg_tool.weapon_tag
                    
        return self.execute(context)

    def execute(self, context):
        if context.collection != "Weapon":
            try: 
                collection = bpy.data.collections['Weapon']
            except Exception:
                collection = bpy.data.collections.new('Weapon')
                bpy.context.scene.collection.children.link(collection)
                
        layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        bpy.context.view_layer.active_layer_collection = layer_collection
        
        
        addon = context.preferences.addons[get_addon_name(context)]
        
        project_path = addon.preferences['project_filepath']
        weapon_path = project_path + "\\Assets\\Sources\\Models\\Weapons\\" + self.weapon_tag + "\\" + self.weapon_tag + ".fbx"
        textures_paths = []
        textures_paths.append(project_path + "\\Assets\\Sources\\Textures\\maps\\Weapons\\map_weapon\\")
        textures_paths.append(project_path + "\\Assets\\Resources\\WeaponSkinsV2\\WeaponSkinAssets\\Share4skins")
        textures_paths.append(project_path + "\\Assets\\Sources\\Textures")
        
        bpy.ops.better_import.fbx(filepath=weapon_path, 
                                  use_auto_bone_orientation=False, 
                                  use_fix_attributes=True, 
                                  my_import_normal='Import', 
                                  use_auto_smooth=False, 
                                  my_scale=1, 
                                  use_reset_mesh_origin=False)
        
        for path in textures_paths:
            bpy.ops.file.find_missing_files(directory=path)
        
        if self.pixelize:
            texture_pixel_filter(context)
        if self.fix_materials:
            flatten_materials(context)

        context.scene.pg_tool.weapon_tag = self.weapon_tag

        return {'FINISHED'}

class PG_OT_import_avatar(Operator):
    """Import Avatar by its Tag"""
    bl_label = "Import Avatar"
    bl_idname = "pg.import_avatar"
    bl_options = {'REGISTER', 'UNDO'}

    avatar_tag : StringProperty(name = "Avatar Name" )
    pixelize : BoolProperty(name = "Pixelize", description = "Make imported textures pixelated", default = True)
    fix_materials : BoolProperty(name = "Flatten materaials", description = "set 0 in metallness, specular, emission properties in imported materials", default = True)

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D" and context.mode == "OBJECT"

    def invoke(self, context, event):
        self.avatar_tag = context.scene.pg_tool.avatar_tag
                    
        return self.execute(context)

    def execute(self, context):
        
        if context.collection != "Avatar":
            try: 
                collection = bpy.data.collections['Avatar']
            except Exception:
                collection = bpy.data.collections.new('Avatar')
                bpy.context.scene.collection.children.link(collection)
                
        layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        bpy.context.view_layer.active_layer_collection = layer_collection
        
        
        addon = context.preferences.addons[get_addon_name(context)]
        
        project_path = addon.preferences['project_filepath']
        weapon_path = project_path + "\\Assets\\Sources\\battle_royale\\Models\\" + self.avatar_tag + ".fbx"

        textures_paths = []
        textures_paths.append(project_path + "\\Assets\\Sources\\battle_royale\\Textures")
        textures_paths.append(project_path + "\\Assets\\Resources\\WeaponSkinsV2\\WeaponSkinAssets\\Share4skins")
        
        bpy.ops.better_import.fbx(filepath=weapon_path, 
                                  use_auto_bone_orientation=False, 
                                  use_fix_attributes=True, 
                                  my_import_normal='Import', 
                                  use_auto_smooth=False, 
                                  my_scale=1, 
                                  use_reset_mesh_origin=False)
        
        for path in textures_paths:
            bpy.ops.file.find_missing_files(directory=path)
        

        if self.pixelize:
            texture_pixel_filter(context)
        if self.fix_materials:
            flatten_materials(context)

        context.scene.pg_tool.avatar_tag = self.avatar_tag

        return {'FINISHED'}
        
#Solve some bugs of Better FBX importer
class PG_OT_fix_import(Operator):
    """Fix imported Weapon Rig in active Collection"""
    bl_label = "Fix Imported Rig"
    bl_idname = "pg.fix_import"
    bl_options = {'REGISTER', 'UNDO'}
    
#    @classmethod
#    def poll(cls, context):
#        if bpy.context.active_object is None:
#            return False
#        
#        return (context.area.type == 'VIEW_3D' and 
#                context.active_object.type == 'ARMATURE' and 
#                context.active_object.select_get()
#                )
            
    def execute(self, context):
        scene = context.scene
        collection = context.collection
        
        emptys = []
        meshes = []
        armature = None
        
        #lookup for imported objects
        for name, id in collection.objects.items():
            if id.type == 'EMPTY':
                emptys.append(id)
            elif id.type == 'ARMATURE':
                armature = id          
            elif id.type == 'MESH':
                meshes.append(id)
        
        if armature == None:
            self.report({'ERROR'}, 'Armature not found')
            return {'CANCELLED'}
        
        #delete keyframes from armature object
        try:
            for f in range(int(armature.animation_data.action.frame_range[0]), int(armature.animation_data.action.frame_range[1]+1)):
                armature.keyframe_delete('location', frame=f)
                armature.keyframe_delete('rotation_quaternion', frame=f)
                armature.keyframe_delete('scale', frame=f)
        except:
            pass
        
        #
        if armature.parent == None:
            self.report({'ERROR'}, 'Armature has no parent')
            return {'CANCELLED'} 
        
        if scene.pg_tool.weapon_tag == '':
            scene.pg_tool.weapon_tag = armature.name
        
        tag = scene.pg_tool.weapon_tag
        
        
        #create trash collection
        if bpy.data.collections.find('trash') < 0:
            trash_col = bpy.data.collections.new('trash')
            collection.children.link(trash_col)
        else: trash_col = bpy.data.collections['trash']
              
        context.view_layer.objects.active = armature  #Set armature as Active Object
        
        #for Blender exporter 
        if armature.data.bones.find(tag) == 0:
             armature.data.bones[tag].name += ' 1'        

        #go to Edit Mode
        mod = context.object.mode
        bpy.ops.object.mode_set_with_submode(mode='EDIT')

        #create a bone in the location anorientation of Armature parent
        bpy.ops.armature.bone_primitive_add(name=tag)
        armature.data.edit_bones[tag].matrix = armature.parent.matrix_world
        armature.data.edit_bones[tag].length = 0.1/context.scene.unit_settings.scale_length
        
        #parent all bones without parent to newely created bone
        for name, id in armature.data.bones.items():
            if id.name == tag:
                continue
            if id.parent == None:
                armature.data.edit_bones[name].parent = armature.data.edit_bones[tag]
        
        #exit Edit Mode
        bpy.ops.object.mode_set_with_submode(mode=mod)

        #clear parenting and keep location
        parent = armature.parent
        matrix = armature.matrix_world
        armature.parent = None
        armature.matrix_world = matrix
        
        #move to trash collection
        for ob in emptys:
            trash_col.objects.link(ob)
            collection.objects.unlink(ob)
        
        #emptys.remove(parent) #remove solved empty from the list
        
        '''TODO: Hide Trash collection in outliner'''
        #context.view_layer.layer_collection.children[trash_col.name].exclude = True
        #trash_col.hide_render = True
        
       
       
        #Group Bone Channels
#        armature.animation_data.action.groups.new('1')
#        D.objects['royal_cobra_spirit'].animation_data.action.groups['New Group'].channels.items()
        
        return {'FINISHED'}
    
#   Combine rigs for presentation 
class PG_OT_combine_rigs(Operator):
    """Combine weapon rig (selected) with main avatar rig (active)"""
    bl_label = "Combine Rigs"
    bl_idname = "pg.combine_rigs"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    #make sure that there are 2 objects selected, one of with is active and both of them are armatures
    def poll(cls, context):
        if bpy.context.active_object is None :
            return False
        if len(context.selected_objects) != 2 :
            return False
        for arm in context.selected_objects:
            if arm.type != 'ARMATURE':
                return False        
        return True
    
    def execute(self, context):
        list = context.selected_objects
        avatar_rig = context.active_object
        list.remove(avatar_rig)
        weapon_rig =list[0]
        
        move_bones_to_layer(weapon_rig.data.bones, layer = 10) 
        
        #join rigs
        bpy.ops.object.join()
        
        #rotate avatar arms
        for bone in avatar_rig.data.bones:
            if bone.name.lower() == 'fps_player_arm_right':
                weapon_arm_R = bone
            if bone.name.lower() == 'fps_player_arm_left':
                weapon_arm_L = bone
            if bone.name.lower() == 'ctrl_fk_arm_r':
                avatar_arm_R = bone
            if bone.name.lower() == 'ctrl_fk_arm_l':
                avatar_arm_L = bone
        
        
        #TODO: Make rotations via transform matrix
        bpy.ops.object.mode_set_with_submode(mode='POSE')
        for bone in avatar_rig.pose.bones:
            bone.bone.select = False
            
        bpy.data.armatures[avatar_rig.data.name].layers[2] = True
        bpy.data.armatures[avatar_rig.data.name].layers[10] = True
        
        
        if addon_installed('space_view3d_copy_attributes'):
            #right arm rotation
            avatar_rig.data.bones.active = avatar_rig.pose.bones[weapon_arm_R.name].bone
            avatar_rig.pose.bones[avatar_arm_R.name].bone.select = True
            bpy.ops.pose.copy_pose_vis_rot()
            
            avatar_rig.pose.bones[weapon_arm_R.name].bone.select = False
            bpy.ops.transform.rotate(value=-3.14159, orient_axis='X', orient_type='LOCAL')
            avatar_rig.pose.bones[avatar_arm_R.name].bone.select = False
            #left arm rotation
            avatar_rig.data.bones.active = avatar_rig.pose.bones[weapon_arm_L.name].bone
            avatar_rig.pose.bones[avatar_arm_L.name].bone.select = True
            bpy.ops.pose.copy_pose_vis_rot()
            
            avatar_rig.pose.bones[weapon_arm_L.name].bone.select = False
            bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='LOCAL')
            avatar_rig.pose.bones[avatar_arm_L.name].bone.select = False
        
        
        
        #constrain weapon arms
        #right
        avatar_rig.pose.bones[weapon_arm_R.name].constraints.new('COPY_TRANSFORMS')
        avatar_rig.pose.bones[weapon_arm_R.name].constraints.active.target = avatar_rig
        avatar_rig.pose.bones[weapon_arm_R.name].constraints.active.subtarget = 'MCH_arm_R'


        #TODO: Make choice if left arm needed
        #left
        avatar_rig.pose.bones[weapon_arm_L.name].constraints.new('COPY_TRANSFORMS')
        avatar_rig.pose.bones[weapon_arm_L.name].constraints.active.target = avatar_rig
        avatar_rig.pose.bones[weapon_arm_L.name].constraints.active.subtarget = 'MCH_arm_L'
        
        #parenting weapon root bone to its proper parent in avatar rig
        bpy.ops.object.mode_set_with_submode(mode='EDIT')
        
        """
        character_holder = avatar_rig.data.edit_bones['CharacterHolder']
        
        #weap_prefab == ContentPres_weaponXXXX
        for bone in character_holder.children:
            if bone.name.find('Weapon') > -1:
                weap_prefab = bone
                break
        #FIXME!!

        for bone in weap_prefab.children:
            if bone.name.find('Weapon') > -1:
                weapon = bone
            if bone.name.find('avatar') > -1:
                avatar = bone
        for bone in weapon.children:
            if bone.name.find('Weapon') > -1:
                inner = bone
                break
        """
        for bone in avatar_rig.data.edit_bones:
            if bone.get("bone_id") is not None:
                if bone.get("bone_id") == "avatar_root":
                    avatar = bone
                if bone.get("bone_id") == "weapon_number":
                    weapon = bone
                if bone.get("bone_id") == "weapon_inner":
                    inner = bone
        
        weapon_tag = str(context.scene.pg_tool.weapon_tag)
        avatar_rig.data.edit_bones[weapon_tag].parent = inner
        bpy.ops.object.mode_set_with_submode(mode='OBJECT')
        
        #rename bones
        num = str(context.scene.pg_tool.weapon_number)
        if num != '':
            #weap_prefab.name = weap_prefab.name[0:-4] + num
            print(weapon.name)
            weapon.name = str(weapon.name)[0:-4] + num
            print(weapon.name)
            inner.name = str(inner.name)[0:6] + num + str(inner.name)[10:]
            
        avatar_name = str(context.scene.pg_tool.avatar_tag)
        if avatar_name != '':
            try: 
                avatar.name = avatar_name
            except:
                self.report({'WARNING'}, "Couldn't find Avatar. Avatar bone not renamed")
                
        #pin weapon mesh to avatar rig
        weapon_mesh = None
        for name, ob in bpy.data.objects.items():
            if ob.type == 'MESH' and name.startswith(weapon_tag): #not all weapon meshes has '_mesh' postfix
                weapon_mesh = ob
                break #we take the first match
        
        if weapon_mesh is not None:
            weapon_mesh.modifiers[0].object = avatar_rig
        else:
            self.report({'WARNING'}, "Couldn't find weapon mesh. Armature not assigned")
        
        return {'FINISHED'}


#   Riging

#   Create bone with proper scene scaling
class PG_OT_add_bone(Operator):
    """Create bone with proper scene scaling"""
    bl_label = "Add Bone"
    bl_idname = "pg.add_bone"
    bl_options = {'REGISTER', 'UNDO'}

    name : StringProperty(name="Name", default= "Bone")
    length : FloatProperty(name = 'Length', min = 0, unit= "LENGTH")
    y_up : BoolProperty(name= "Y up", default= False)

    @classmethod
    def poll(cls, context):
        if context.active_object is None :
            return False
        if context.active_object.type != 'ARMATURE':
            return False        
        return True

    def invoke(self, context, event):
        self.length = 1 / context.scene.unit_settings.scale_length
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        mod = context.object.mode
        arm = context.active_object.data
        bpy.ops.object.mode_set_with_submode(mode='EDIT')

        mat =  context.active_object.matrix_world.inverted() @ context.scene.cursor.matrix
        mat = mathutils.Matrix().Translation(mat.translation)

        if self.y_up:
            mat = Matrix(((1, 0, 0, mat[0][3]), 
                          (0, 0, -1, mat[1][3]),
                          (0, 1, 0, mat[2][3]),
                          (0, 0, 0, 1)))
        
        bpy.ops.armature.select_all(action='DESELECT')
        add_bone(arm, self.name, mat, self.length)
        bpy.ops.object.mode_set_with_submode(mode=mod)

        return {'FINISHED'}


#   Create simple controls
class PG_OT_simple_controls(Operator):
    """Create control bones"""
    bl_label = "Create simple controls"
    bl_idname = "pg.create_simple_controls"
    bl_options = {'REGISTER', 'UNDO'}

    ctrl_layer : BoolVectorProperty(name= "Layer", subtype= "LAYER", size= 32)
    set_wgt : BoolProperty(name = "Set Widgets", description = "Set Cube Widgets for Control Bones", default = False)
    wgt_size : FloatProperty(name= "Widget Size", min= 0, soft_max= 1000, default= 1, unit= "LENGTH")
    
    # TODO:
    # adaptive_wgt : BoolProperty(name = "Adaptive WGTs", description = "", default = True)
    # adj_transform : BoolProperty(name = "Adjust Transform", description = "Move Control Bones to Deformation Bones Transform", default = False )
    

    @classmethod
    def poll(cls, context):
        if context.active_object == None or context.active_object.type != 'ARMATURE' :
            return False
        return True

    def invoke(self, context, event):
        self.wgt_size = 1 / context.scene.unit_settings.scale_length
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "ctrl_layer", text= "CTRL Bone Layer (Optional)")
        
        layout.use_property_split = True
        layout.use_property_decorate = True
        layout.prop(self, "set_wgt")
        layout.prop(self, "wgt_size")


    def execute(self, context):
        avatar_rig = context.active_object
        armature = avatar_rig.data
        def_bones = []
        bone_pairs = {}
        mod = context.object.mode
        
        if not obj_exists('WGT_Cube') and self.set_wgt:
            widget = create_wgt_cube(1 / context.scene.unit_settings.scale_length)
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = avatar_rig
            context.active_object.select_set(True)
        else:
            widget = bpy.data.objects['WGT_Cube']
        
        bpy.ops.object.mode_set_with_submode(mode='EDIT')
        for bone in context.selected_bones:
            def_bones.append(bone)
            
        #Duplicate selected bones
        for bone in def_bones:
            ctrl_name = 'CTRL_' + bone.name
            ctrl_bone = add_bone(armature, ctrl_name, bone.matrix, bone.length * 1.5)
            ctrl_bone.use_deform = False
            
            #deselect old bones
            bone.select = bone.select_head = bone.select_tail = False
            
            bone_pairs[bone.name] = ctrl_bone.name  #Solves issue if name already existed
    
        for bone in context.selected_bones:
            bone.layers = self.ctrl_layer

        # Relations
        for bone in def_bones:
            if bone.parent in def_bones:
                armature.edit_bones[bone_pairs[bone.name]].parent = armature.edit_bones[bone_pairs[bone.parent.name]]
                
        
        # Constraints and widgets             
        bpy.ops.object.mode_set_with_submode(mode='POSE')
        wgt_sc = self.wgt_size * context.scene.unit_settings.scale_length
        wgt_scale = (wgt_sc, wgt_sc, wgt_sc)

        for bone, ctrl in bone_pairs.items():
            avatar_rig.pose.bones[bone].constraints.new('COPY_TRANSFORMS')
            avatar_rig.pose.bones[bone].constraints.active.target = avatar_rig
            avatar_rig.pose.bones[bone].constraints.active.subtarget = ctrl

            if self.set_wgt:
                avatar_rig.pose.bones[ctrl].custom_shape = widget
                avatar_rig.pose.bones[ctrl].use_custom_shape_bone_size = False
                avatar_rig.pose.bones[ctrl].custom_shape_scale_xyz = wgt_scale


        bpy.ops.object.mode_set_with_submode(mode=mod)
        
        return {'FINISHED'}

class PG_Bone_Spaces(PropertyGroup):
    armature : StringProperty(name= "Armature")
    bone : StringProperty(name= "Bone")

class PG_OT_add_space(Operator):
    """Add parent space"""
    bl_label = "Add space"
    bl_idname = "pg.add_space"
    #bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        self.add_space(context)
        return {"FINISHED"}

    def add_space(self, context):
        space = context.active_pose_bone.spaces.add()
        space.armature = context.active_object.name
        space.bone = ""
       
class PG_OT_remove_space(Operator):
    """Remove parent space"""
    bl_label = "Remove space"
    bl_idname = "pg.remove_space"
    #bl_options = {'REGISTER', 'UNDO'}

    index : IntProperty(name="index")

    def execute(self, context):
        context.active_pose_bone.spaces.remove(self.index)
        return {"FINISHED"}
 
class PG_OT_add_space_switching(Operator):
    """Configure Active Bone space switching"""
    bl_label = "Add Space Switching"
    bl_idname = "pg.add_space_switching"
    bl_options = {'UNDO'} #'REGISTER'
   
    @classmethod
    def poll(cls, context):
        if context.active_object == None or context.active_object.type != 'ARMATURE' :
            return False
        if context.mode != "POSE":
            return False
        if context.active_bone is None:
            return False
        if not addon_installed("space_switcher"):
            return False
        return True
 
    def invoke(self, context, event):
        if not context.active_pose_bone.spaces:
            bpy.ops.pg.add_space()
            bpy.ops.pg.add_space()

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        spaces = context.active_pose_bone.spaces
        layout = self.layout
        
        layout.label(text= "Bone: " + context.active_pose_bone.name)
        for i in range(len(spaces.keys())):
            row = layout.row(align = True)
            row.prop_search(spaces[i], "armature", bpy.data, "objects", text="")
            row.prop_search(spaces[i], "bone", bpy.data.objects[spaces[i].armature].pose, "bones", text="") #bpy.data.objects[self.armature]
            row.operator("pg.remove_space", text= "", icon= "X").index = i
        layout.operator("pg.add_space", text= "Add Space")

    def execute(self, context):
        own_armature = context.active_object
        active_bone = context.active_pose_bone
        prop_name = active_bone.name + "_space"

        if len(context.active_pose_bone.spaces) == 0:
            del active_bone["spaces"]
            if active_bone.get(prop_name) is not None:
                del active_bone[prop_name]
            
            switches = own_armature.data.space_switcher.space_switches
            if switches.get(prop_name):
                index = switches[prop_name].index
                switches.remove(index)
            
            constrain = active_bone.constraints.get(prop_name)
            if constrain:
                self.clear_constrain(constrain)
                active_bone.constraints.remove(constrain)
            return {"FINISHED"}
        
        
        
        con_spaces = []
        con_armatures = []

        for space in context.active_pose_bone.spaces:
            con_armatures.append(space.armature)
            con_spaces.append(space.bone)

        sw_spaces = ["World"]
        for i in range(len(con_armatures)):
            if con_armatures[i] != own_armature.name:
                sw_spaces.append(con_armatures[i] + ": " + con_spaces[i])
            else:
                sw_spaces.append(con_spaces[i])
        
        if active_bone.get(prop_name) is None:
            active_bone[prop_name] = 0
            active_bone.id_properties_ensure()
        
        property_manager = active_bone.id_properties_ui(prop_name)
        property_manager.update(min=0, max=len(con_spaces), soft_max=len(con_spaces))
        active_bone.property_overridable_library_set('["' + prop_name + '"]', True)
        
        switcher = own_armature.data.space_switcher.space_switches.get(prop_name)
        if not switcher:
            switcher = own_armature.data.space_switcher.space_switches.add()
            switcher.name = prop_name
        
        datapath = 'pose.bones["%s"]["%s"]' % (active_bone.name, prop_name)
        switcher.property_datapath = datapath
        switcher.space_switch_type = "ENUM"

        switcher.enum_type_properties.bones.clear()
        switcher.enum_type_properties.spaces.clear()
        
        switcher.enum_type_properties.bones.add()
        switcher.enum_type_properties.bones[0].name = active_bone.name
        for space in sw_spaces:
            sp = switcher.enum_type_properties.spaces.add()
            sp.name = space

        constrain = context.active_pose_bone.constraints.get(prop_name)
        if not constrain:
            constrain = active_bone.constraints.new(type = "ARMATURE")
            constrain.name = prop_name
        
        self.clear_constrain(constrain)

        # for target in constrain.targets:
        #     target.driver_remove("weight")
        # constrain.targets.clear()
        
        for num in range(len(con_spaces)):
            constrain.targets.new()
            constrain.targets[num].target = bpy.data.objects[con_armatures[num]]
            constrain.targets[num].subtarget = con_spaces[num]
            
            drv = constrain.targets[num].driver_add("weight")
            drv.driver.type = "SCRIPTED"
            var = drv.driver.variables.new()
            var.name = "parent_space"
            var.targets[0].id_type = "OBJECT"
            var.targets[0].id = context.active_object
            var.targets[0].data_path = datapath
            drv.driver.expression = "parent_space == %d" % (num + 1) 
    
        
        return {"FINISHED"}
    
    def clear_constrain(self, constrain):
        for target in constrain.targets:
            target.driver_remove("weight")
        constrain.targets.clear()
    
    


class PG_OT_test(Operator):
    """test operator"""
    bl_label = "DEV: test"
    bl_idname = "pg.test"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.report({'WARNING'}, "Couldn't find weapon mesh. Armature not assigned")
        # arm = bpy.data.objects['Armature'].data
        # sel_bone = arm.edit_bones['Bone']
        
        # bone_name = 'Bone_copy'

        # if not bone_exists(arm, bone_name):
        #     add_bone(arm, 'Bone_copy', sel_bone.matrix, sel_bone.length * 1.5 )
        
        return {'FINISHED'}
                
#   Registration

classes = (
    PG_properties,
    PG_Bone_Spaces,
    PG_OT_find_instances,
    PG_OT_reset_ob_colors,
    PG_OT_optimize,
    PG_OT_unwrap,
    PG_OT_test_material,
    PG_OT_test_texture,
    PG_OT_texture_pixel_filter,
    PG_OT_set_tex_desity,
    PG_OT_reload_textures,
    PG_OT_import_avatar,
    PG_OT_import_weapon,
    PG_OT_fix_import,
    PG_OT_combine_rigs,
    PG_OT_add_bone,
    PG_OT_simple_controls,
    PG_OT_add_space_switching,
    PG_OT_add_space,
    PG_OT_remove_space,

    PG_OT_test,
        
    )        
                
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.pg_tool = bpy.props.PointerProperty(type = PG_properties)
    bpy.types.PoseBone.spaces = bpy.props.CollectionProperty(type=PG_Bone_Spaces)

def unregister():
    del bpy.types.Scene.pg_tool
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
if __name__ == "__main__":
    register()
