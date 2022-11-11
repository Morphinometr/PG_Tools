import bpy
import random
from mathutils import Matrix, Vector
from bpy.types import Armature

def get_addon_name(context):
    modules = context.preferences.addons.keys()
    for mod in modules:
        if 'PG_Tools' in mod:
            print(mod)
            return mod

def get_collection(name : str):
    try: 
        collection = bpy.data.collections[name]
    except Exception:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection

def get_layer_collection(collection_name : str):
    def recurLayerCollection(layerColl, collName):
        """Recursively transverse layer_collection for a particular name"""
        found = None
        print(layerColl.name)
        if layerColl.name == collName:
            print(layerColl)
            return layerColl
        
        for layer in layerColl.children:  
            found = recurLayerCollection(layer, collName)
            if found:
                return found

    return recurLayerCollection(bpy.context.view_layer.layer_collection, collection_name)    

def get_obj(name : str):
    for ob in bpy.data.objects:
        if ob.name == name:
            return ob
    return None

def get_widget(type: str, size : float):
    widget_name = "WGT_" + type.capitalize() + "_1m"
    creation_func = {"cube" : create_wgt_cube, "sphere" : create_wgt_sphere, "circle" : create_wgt_circle, "square" : create_wgt_square}
    widget = get_obj(widget_name)
    if widget is None:
        widget = creation_func[type](widget_name, size)
    return widget

def create_wgt_cube(name : str, size : float = 1.0):
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    _size = size 

    bpy.ops.mesh.primitive_cube_add(size=_size, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    wgt = bpy.context.object
    wgt.name = name
    bpy.ops.object.mode_set_with_submode(mode='EDIT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    return wgt

def create_wgt_sphere(name : str, size : float = 1.0):
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    _size = size / 2 

    bpy.ops.mesh.primitive_circle_add(vertices=32, radius=_size, calc_uvs=False, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    wgt = bpy.context.object
    wgt.name = name
    bpy.ops.object.mode_set_with_submode(mode='EDIT')
    bpy.ops.mesh.duplicate()
    bpy.ops.transform.rotate(value=1.5708, orient_axis="X", orient_type="GLOBAL", use_proportional_edit=False)
    bpy.ops.mesh.duplicate()
    bpy.ops.transform.rotate(value=1.5708, orient_axis="Z", orient_type="GLOBAL", use_proportional_edit=False)
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    return wgt

def create_wgt_circle(name : str, size : float = 1.0):
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    _size = size / 2

    bpy.ops.mesh.primitive_circle_add(vertices=32, radius=_size, calc_uvs=False, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    wgt = bpy.context.object
    wgt.name = name
    bpy.ops.object.mode_set_with_submode(mode='EDIT')
    bpy.ops.transform.rotate(value=1.5708, orient_axis="X", orient_type="GLOBAL", use_proportional_edit=False)
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    return wgt

def create_wgt_square(name : str, size : float = 1.0):
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    _size = size 

    bpy.ops.mesh.primitive_plane_add(size=_size, calc_uvs=False, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    wgt = bpy.context.object
    wgt.name = name
    bpy.ops.object.mode_set_with_submode(mode='EDIT')
    bpy.ops.transform.rotate(value=1.5708, orient_axis="X", orient_type="GLOBAL", use_proportional_edit=False)
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bevel(offset=_size * 0.125, offset_pct=0, segments=7, affect='VERTICES')
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    return wgt

def add_bone(armature : Armature, name : str, transform : Matrix, length : float):
    bone = armature.edit_bones.new(name)
    vec = Vector((0,1,0))
    bone.tail = bone.head + vec * length
    bone.matrix = transform.copy()
    bone.select = bone.select_head = bone.select_tail = True
    return bone

def move_bones_to_layer(bones, layer : int):
    for bone in bones:
        bone.layers[layer]=True
        for l in range(32):
            if l == layer: 
                continue
            bone.layers[l] = False
                 
def set_td_size(scene, x, y):
    if addon_installed('Texel_Density'):
        scene.td.custom_width = str(x)
        scene.td.custom_height = str(y)


    
def create_mat(name):
    test_mat = bpy.data.materials.new(name)
    test_mat.use_nodes = True
    test_mat.use_fake_user = True
    test_mat.node_tree.nodes["Principled BSDF"].inputs[5].default_value = 0

    #test texture
    principled_node = test_mat.node_tree.nodes.get('Principled BSDF')
    test_image_node = test_mat.node_tree.nodes.new("ShaderNodeTexImage")
    test_image_node.location = (-350, 200)
        
    link  = test_mat.node_tree.links.new
    link(test_image_node.outputs[0], principled_node.inputs[0])
    test_image_node.interpolation = 'Closest'
    
    #bake texture
    bake_image_node = test_mat.node_tree.nodes.new("ShaderNodeTexImage")
    bake_image_node.name = bake_image_node.label = "Bake"
    bake_image_node.location = (-350, 500)
    bake_image_node.interpolation = 'Closest'

    return test_mat
    
def addon_installed(name):
    addons = bpy.context.preferences.addons.keys()
    for ad in addons:
        if ad.find(name) > -1:
            return True
    return False

def get_materials(context):
    materials = []
    
    if context.active_object is not None:
        for slot in context.active_object.material_slots:
            materials.append(slot.material)
    
    for ob in context.selected_objects:
        for slot in ob.material_slots:
            if slot.material not in materials:
                materials.append(slot.material) 
    return materials
    
def get_textures(materials):
    textures = []
    for mat in materials:
        for node in mat.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                textures.append(node)
    return textures

def texture_pixel_filter(context):
    materials = get_materials(context)
    textures = get_textures(materials)

    for mat in materials:
        mat.node_tree.nodes["Principled BSDF"].inputs[6].default_value = 0 # 6 - Metallic 

    for tex in textures:
        tex.interpolation = 'Closest'

def pg_unwrap(all=False):
    if all:
        bpy.ops.mesh.select_all(action = 'SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0)
    pg_tool = bpy.context.scene.pg_tool
    bpy.ops.pg.set_tex_density(size=pg_tool.tex_size, 
                                tex_size_x=pg_tool.tex_size_custom_x, 
                                tex_size_y=pg_tool.tex_size_custom_y, 
                                density=pg_tool.px_density, 
                                density_custom=pg_tool.px_density_custom)

def flatten_materials(context):
    materials = get_materials(context)
    for mat in materials:
        for i in (6,7,20): # 6 - Metallic, 7 - Specular, 20 - Emission
            mat.node_tree.nodes["Principled BSDF"].inputs[i].default_value = 0

def random_color(steps, alpha=1):
    return (randvalue(steps),randvalue(steps),randvalue(steps),alpha)

def randvalue(steps):
    return random.randrange(steps+1)/steps

def color_list(length, steps=10, alpha=1):
    lst = []
    success = False
    # seed = random.randrange(1000000)
    for i in range(length):
        for c in range(1000):
            col = random_color(steps, alpha)
            if col not in lst and col != (1,1,1, alpha):
                success = True
                lst.append(col)
                break
            else:
                success = False
        if success:
            continue
        else:    
            raise ValueError("Too many instantiated objects. Couldn't create enough color variants. Something is very wrong in calculation number of variants")
    return lst

def match_bone_transform(bone_pairs):
    """Expects a dictionary with Pose bone pairs. {transform : source}
    
    :transform: the bone that will be transformed to source bone. Type: bpy.types.PoseBone
    :source: reference bone. Type: bpy.types.PoseBone
    """

    def recurse(bone, bones):
        # Matrix math to ability to use it for different objects        
        mat = bones[bone].id_data.matrix_world @ bones[bone].matrix 
        bone.matrix = bone.id_data.matrix_world.inverted() @ mat

        bpy.context.view_layer.update()

        for child in bone.children:
            recurse(child, bones)
    
    bones = bone_pairs.keys()    
    top_level = [bone for bone in bones if bone.parent not in bones]  

    for bone in top_level:
        recurse(bone, bone_pairs)
    
def vse_trim_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("pg.trim_timeline_to_strips")

