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

def recurLayerCollection(layerColl, collName):
    """Recursivly transverse layer_collection for a particular name"""
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found

##Switching active Collection to active Object selected
#    obj = bpy.context.object
#    ucol = obj.users_collection
#    for i in ucol:
#        layer_collection = bpy.context.view_layer.layer_collection
#        layerColl = recurLayerCollection(layer_collection, i.name)
#        bpy.context.view_layer.active_layer_collection = layerColl

def obj_exists(name : str):
    for ob in bpy.data.objects:
        if ob.name == name:
            return True
    return False

def bone_exists(arm : Armature, name : str):
    for b in arm.edit_bones:
        if b.name == name:
            return True
    return False

def create_wgt_cube(size : float = 1.0):
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    _size = size 

    bpy.ops.mesh.primitive_cube_add(size=_size, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    wgt = bpy.context.object
    wgt.name = "WGT_Cube"
    bpy.ops.object.mode_set_with_submode(mode='EDIT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
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
            raise ValueError("Too many instanciated objects. Couldn't create enough color variants. Try to increase 'Color steps' parameter")
    return lst

def vse_trim_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("pg.trim_timeline_to_strips")
    