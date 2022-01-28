import bpy
from bpy.types import Operator
bl_info = {"name": "Tools Panel",
           "description": "tools",
           "author": "Morphin",
           "version": (0, 0, 2),
           "blender": (2, 80, 0),
           "location": "View3d > Properties > View > PixelGun",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "3D View", }

#   Custom properties

class pixel_properties(bpy.types.PropertyGroup):
    
    tex_size : bpy.props.EnumProperty(
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
    
    px_density : bpy.props.EnumProperty(
        name = 'Pixel Density',
        items = [('10', '10 px/m', ''),
                 ('16', '16 px/m', ''),
                 ('32', '32 px/m', ''),
                 ('1000', '1000 px/m', ''),
                 ('custom', 'Custom', ''),
                ],
        default = '16'
        )
        
    tex_size_custom_x : bpy.props.IntProperty(name="Custom texture size X", min = 1, default = 64 )
    tex_size_custom_y : bpy.props.IntProperty(name="Custom texture size Y", min = 1, default = 64 )
    px_density_custom : bpy.props.FloatProperty(name="Custom Pixel Density", min = 0 )
    
    weapon_tag : bpy.props.StringProperty(name="Weapon Tag", default = "")
    weapon_number : bpy.props.StringProperty(name="Weapon Number", default = "")
    avatar_tag : bpy.props.StringProperty(name="Avatar Tag", default = "")
    
    

#   Operators    

class MESH_OT_optimize(Operator):
    """Limited dissolve, weld and set sharp selected objects"""
    bl_label = "Optimize"
    bl_idname = "mesh.optimize"
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
        optimize(self, context)
       
        return {'FINISHED'}

class MESH_OT_unwrap(Operator):
    """Unwrap mesh"""
    bl_label = "Unwrap"
    bl_idname = "mesh.unwrap"
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
        unwrap(self,context)
    
        return {'FINISHED'}

class MESH_OT_test_material(Operator):
    """Add test meterial"""
    bl_label = "Test Material"
    bl_idname = "mesh.test_material"
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
            test_mat = create_mat(self,context)
        else: test_mat = bpy.data.materials.get("Test Material")
        
            
        #append to selected objects
        for ob in bpy.context.selected_objects :
            ob.active_material = test_mat
                   
        return {'FINISHED'}
    
    
class MESH_OT_test_texture(Operator):
    """Add test texture"""
    bl_label = "Set Texture"
    bl_idname = "mesh.test_texture"
    bl_options = {'REGISTER', 'UNDO'}
    
    size : bpy.props.EnumProperty(
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
        
    tex_size_x : bpy.props.IntProperty(name="Custom texture size X", min = 1, default = 64 )
    tex_size_y : bpy.props.IntProperty(name="Custom texture size Y", min = 1, default = 64 )
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None:
            return False
        
        if bpy.data.materials.find("Test Material") < 0:
            return False
        
        return context.area.type == 'VIEW_3D' and context.active_object.type == 'MESH' and context.active_object.select_get()
            
    
    def invoke(self, context, event):
        scene = context.scene
        pixel_tool = scene.pixel_tool
        self.size = pixel_tool.tex_size
        self.tex_size_x = pixel_tool.tex_size_custom_x
        self.tex_size_y = pixel_tool.tex_size_custom_y
                    
        return self.execute(context)
        
    def execute(self, context):
        scene = context.scene
        pixel_tool = scene.pixel_tool
         #Custom tex size!
        if self.size != 'custom':
            self.tex_size_x = self.tex_size_y = int(self.size)
            pixel_tool.tex_size_custom_x = pixel_tool.tex_size_custom_y = int(self.size)
        
        #test texture add
        tex_name = "Test " + str(self.tex_size_x) + 'x' + str(self.tex_size_y)
                
        if bpy.data.images.find(tex_name) < 0:
            texture = bpy.ops.image.new(name= tex_name, width=self.tex_size_x, height=self.tex_size_y, generated_type='COLOR_GRID')
        
        test_mat = bpy.data.materials["Test Material"]
        test_image_node = test_mat.node_tree.nodes["Image Texture"]
        test_image_node.image = bpy.data.images[tex_name]
        
        #bake texture add
        texture = bpy.data.images.new(name= 'Bake', width=self.tex_size_x, height=self.tex_size_y, alpha=True)
        texture.generated_color = (0, 0, 0, 0)

        test_image_node = test_mat.node_tree.nodes["Image Texture.001"]
        test_image_node.image = texture
        #test_image_node         #???
        
        if addon_installed('Texel_Density'):
            scene.td.custom_width = str(scene.pixel_tool.tex_size_custom_x)
            scene.td.custom_height = str(scene.pixel_tool.tex_size_custom_y)
        
        return {'FINISHED'}
    
class MESH_OT_texture_pixel_filter(Operator):
    """Set pixel interpolation mode to "Closest" for all textures of selected objects"""
    bl_label = "Make pixelated"
    bl_idname = "mesh.texture_pixel_filter"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None and len(context.selected_objects) < 1:
            return False
        return True
            
    def execute(self, context):
        texture_pixel_filter(self, context)
        
        return {'FINISHED'}
 
class MESH_OT_reload_textures(Operator):
    """reload textures"""
    bl_label = "Reload Textures"
    bl_idname = "mesh.reload_textures"
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
        reload_textures(self,context)
    
        return {'FINISHED'}
    
#   Interaraction with texel density addon

class MESH_OT_set_tex_desity(Operator):
    """Set texel density for selected faces"""
    bl_label = "Set Texel Density"
    bl_idname = "mesh.set_tex_desity"
    bl_options = {'REGISTER', 'UNDO'}
    
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
        self.density = context.scene.pixel_tool.px_density
        self.density_custom = context.scene.pixel_tool.px_density_custom
                    
        return self.execute(context)
        
    def execute(self, context):
        scene = context.scene
        scene.td.units = '1'
        scene.td.texture_size = '4'
        scene.td.set_method = '0'

        if scene.pixel_tool.px_density == 'custom':
            scene.td.density_set = str(scene.pixel_tool.px_density_custom)
        else:
            scene.td.density_set = scene.pixel_tool.px_density
        
        bpy.ops.object.texel_density_set()

        return {'FINISHED'}
            
               
#   Layout

#   Import Weapon
class PIXEL_OT_import_weapon(Operator):
    """Import Weapon by its Tag"""
    bl_label = "Import Weapon"
    bl_idname = "pixel.import_weapon"
    bl_options = {'REGISTER', 'UNDO'}

#    @classmethod
#    def poll(cls, context):
#        if context.preferences.addons['Pixel_Tools-main'].preferences['project_filepath'] == '' :
#            return False

    def execute(self, context):
        scene = context.scene
        
        if context.collection != "Weapon":
            try: 
                collection = bpy.data.collections['Weapon']
            except Exception:
                collection = bpy.data.collections.new('Weapon')
                bpy.context.scene.collection.children.link(collection)
                
        layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        bpy.context.view_layer.active_layer_collection = layer_collection
        
        
        
        
        project_path = context.preferences.addons['Pixel_Tools-main'].preferences['project_filepath']
        weapon_path = project_path + "\\Assets\\Sources\\Models\\Weapons\\" + scene.pixel_tool.weapon_tag + "\\" + scene.pixel_tool.weapon_tag + ".fbx"        
        textures_path = project_path + "\\Assets\\Sources\\Textures\\maps\\Weapons\\map_weapon\\"
        
        bpy.ops.better_import.fbx(filepath=weapon_path, 
                                  use_auto_bone_orientation=False, 
                                  use_fix_attributes=True, 
                                  my_import_normal='Import', 
                                  use_auto_smooth=False, 
                                  my_scale=1, 
                                  use_reset_mesh_origin=False)
        
        bpy.ops.file.find_missing_files(directory=textures_path)

        
        #bpy.context.view_layer.collections.active = bpy.data.collections['Weapon']

        return {'FINISHED'}
        
#Solve some bugs of Better FBX importer
class PIXEL_OT_fix_import(Operator):
    """Fix imported Weapon Rig"""
    bl_label = "Fix Imported Rig"
    bl_idname = "pixel.fix_import"
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
        
        if armature.parent == None:
            self.report({'ERROR'}, 'Armature has no parent')
            return {'CANCELLED'} 
        
        #Temp
        '''TODO: Make "tag" variable'''
        scene.pixel_tool.weapon_tag
        
        if scene.pixel_tool.weapon_tag == '':
            scene.pixel_tool.weapon_tag = armature.name
        
        tag = scene.pixel_tool.weapon_tag
        
        
        #create trash collection        
        trash_col = bpy.data.collections.new('trash')
        collection.children.link(trash_col)        
              
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
                #print(name)
                continue
            if id.parent == None:
                armature.data.edit_bones[name].parent = armature.data.edit_bones[tag]
                #print(name)
        
        #exit Edit Mode
        bpy.ops.object.mode_set_with_submode(mode=mod)
    
        
        #delete keyframes from armature object
        for f in range(int(armature.animation_data.action.frame_range[0]), int(armature.animation_data.action.frame_range[1]+1)):
            armature.keyframe_delete('location', frame=f)
            armature.keyframe_delete('rotation_quaternion', frame=f)
            armature.keyframe_delete('scale', frame=f)
             
        #clear parenting and keep location
        parent = armature.parent
        matrix = armature.matrix_world
        armature.parent = None
        armature.matrix_world = matrix
        
        #move to trash collection
        trash_col.objects.link(parent)
        collection.objects.unlink(parent)
        
        emptys.remove(parent) #remove solved empty from the list
        
        '''TODO: Hide Trash collection in outliner'''
        #context.view_layer.layer_collection.children[trash_col.name].exclude = True
        #trash_col.hide_render = True
        
       
       
        #Group Bone Channels
#        armature.animation_data.action.groups.new('1')
#        D.objects['royal_cobra_spirit'].animation_data.action.groups['New Group'].channels.items()
        
        return {'FINISHED'}
    
    
#   Combine rigs for presentation 
class PIXEL_OT_combine_rigs(Operator):
    """Combine weapon rig (selected) with main avatar rig (active)"""
    bl_label = "Combine Rigs"
    bl_idname = "pixel.combine_rigs"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    #make sure that there are 2 objects selected, one of with is active and both of them are armatures
    def poll(cls, context):
        if bpy.context.active_object is None :
            return False
        if len(context.selected_objects) < 2 or len(context.selected_objects) >3:
            return False
        for ob in context.selected_objects:
            if ob.type != 'ARMATURE':
                return False        
        return True
    
    def execute(self, context):
        list = context.selected_objects
        avatar_rig = context.active_object
        list.remove(avatar_rig)
        weapon_rig =list[0]
        
        #move all bones in weapon rig to 10th layer
        for bone in weapon_rig.data.bones:
            bone.layers[10]=True
            bone.layers[0]=False      
        
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
        #some dirty code !!!
        bpy.ops.object.mode_set_with_submode(mode='POSE')
        for bone in avatar_rig.pose.bones:
            bone.bone.select = False
            
        bpy.data.armatures[avatar_rig.data.name].layers[2] = True
        bpy.data.armatures[avatar_rig.data.name].layers[10] = True
        
        
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


        #TODO: Make choice
        #left
        avatar_rig.pose.bones[weapon_arm_L.name].constraints.new('COPY_TRANSFORMS')
        avatar_rig.pose.bones[weapon_arm_L.name].constraints.active.target = avatar_rig
        avatar_rig.pose.bones[weapon_arm_L.name].constraints.active.subtarget = 'MCH_arm_L'
        
        #parenting weapon root bone to its proper parent in avatar rig
        bpy.ops.object.mode_set_with_submode(mode='EDIT')
        
        character_holder = avatar_rig.data.edit_bones['CharacterHolder']
        
        #weap_prefab = character_holder.children[0]
        for bone in character_holder.children:
            if bone.name.find('Weapon') > -1:
                weap_prefab = bone
                break
        for bone in weap_prefab.children:
            if bone.name.find('Weapon') > -1:
                weapon = bone
            if bone.name.find('avatar') > -1:
                avatar = bone
        for bone in weapon.children:
            if bone.name.find('Weapon') > -1:
                inner = bone
                break
        
        weapon_tag = context.scene.pixel_tool.weapon_tag
        avatar_rig.data.edit_bones[weapon_tag].parent = inner
        bpy.ops.object.mode_set_with_submode(mode='OBJECT')
        
        #rename bones
        num = context.scene.pixel_tool.weapon_number
        if context.scene.pixel_tool.weapon_number != '':
            weap_prefab.name = weap_prefab.name[0:-4] + num
            weapon.name = weapon.name[0:-4] + num
            inner.name = inner.name[0:6] + num + inner.name[10:]
            
        if context.scene.pixel_tool.avatar_tag != '':
            avatar.name = context.scene.pixel_tool.avatar_tag
             
        #pin weapon mesh to avatar rig
        weapon_mesh = bpy.data.objects[weapon_tag +'_mesh']
        if weapon_mesh is not None:
            weapon_mesh.modifiers[0].object = avatar_rig
        
        
        return {'FINISHED'}


#   Riging

#   Create simple controls
class PIXEL_OT_simple_controls(Operator):
    """Create control bones"""
    bl_label = "Create simple controls"
    bl_idname = "pixel.create_simple_controls"
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context):
    #     if context.preferences.addons['Pixel_Tools-main'].preferences['project_filepath'] == '' :
    #         return False

    def execute(self, context):
        avatar_rig = context.active_object
        def_bones = []
        ctrl_bones = []
        mod = context.object.mode
        
        
        
        bpy.ops.object.mode_set_with_submode(mode='EDIT')
        for bone in context.selected_bones:
            def_bones.append(bone)
        
        
        #Dirty!    
        bpy.ops.armature.duplicate_move()
        
        for bone in context.selected_bones:
            bone.name = "CTRL_" + bone.name[:-4]
            ctrl_bones.append(bone)
            bone.length *= 1.5
            
        bpy.ops.object.mode_set_with_submode(mode='POSE')
        for bone in def_bones:
            avatar_rig.pose.bones[bone.name].constraints.new('COPY_TRANSFORMS')
            avatar_rig.pose.bones[bone.name].constraints.active.target = avatar_rig
            avatar_rig.pose.bones[bone.name].constraints.active.subtarget = 'CTRL_' + bone.name
            
        create_wgt_cube(1)
        bpy.ops.object.select_all(action='DESELECT')
        context.active_object = avatar_rig
        context.active_object.select_set(True)
        
        bpy.ops.object.mode_set_with_submode(mode=mod)
        
        
        
        return {'FINISHED'}

###########################   Panels  ################################



        
                
#   Registration

classes = (
    pixel_properties,
    MESH_OT_optimize,
    MESH_OT_unwrap,
    MESH_OT_test_material,
    MESH_OT_test_texture,
    MESH_OT_texture_pixel_filter,
    MESH_OT_set_tex_desity,
    MESH_OT_reload_textures,
    PIXEL_OT_import_weapon,
    PIXEL_OT_fix_import,
    PIXEL_OT_combine_rigs,
    PIXEL_OT_simple_controls,
    
    
    )
                    
                
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.pixel_tool = bpy.props.PointerProperty(type = pixel_properties)


def unregister():
    del bpy.types.Scene.pixel_tool
    for cls in classes:
        bpy.utils.unregister_class(cls)
        

if __name__ == "__main__":
    register()
