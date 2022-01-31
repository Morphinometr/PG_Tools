import bpy, math
from mathutils import Matrix, Vector
from bpy.types import Object, Armature


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

def create_wgt_cube(context, size : float = 1):
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    _size = size / context.scene.unit_settings.scale_length

    bpy.ops.mesh.primitive_cube_add(size=_size, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(size, size, size))
    bpy.context.object.name = "WGT_Cube"
    bpy.ops.object.mode_set_with_submode(mode='EDIT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set_with_submode(mode='OBJECT')
    
def add_bone(armature : Object, name : str, transform : Matrix, length : float):
    bone = armature.data.edit_bones.new(name)
    bone.tail = bone.head + Vector((0,1,0)) * length
    bone.matrix = transform.copy()
    bone.select_tail = False




def optimize(self, context):
    """Dissolves inner faces, welds double vertices and sets mesh sharp"""
    mod = context.object.mode
    bpy.ops.object.mode_set_with_submode(mode='EDIT')
    
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.dissolve_limited()
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.normals_tools(mode='RESET')
    bpy.ops.mesh.mark_sharp(clear=True)
    bpy.ops.mesh.faces_shade_flat()

    bpy.ops.object.mode_set_with_submode(mode=mod)
    
def unwrap(self, context):
    mod = context.object.mode
    bpy.ops.object.mode_set_with_submode(mode='EDIT')
    
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    
    seams = bpy.ops.mesh.edges_select_sharp()
    bpy.ops.mesh.mark_seam(clear=False)

    #unwrap
    bpy.ops.mesh.select_all(action = 'SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0)

    
    bpy.ops.object.mode_set_with_submode(mode=mod)
    
def create_mat(self,context):
    test_mat = bpy.data.materials.new(name="Test Material")
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
    test_image_node = test_mat.node_tree.nodes.new("ShaderNodeTexImage")
    test_image_node.location = (-350, 800)
    test_image_node.interpolation = 'Closest'

    return test_mat

def texture_pixel_filter(self, context):
    materials = get_materials(context)
    textures = get_textures(materials)
    
    for mat in materials:
        mat.node_tree.nodes["Principled BSDF"].inputs[5].default_value = 0

    for tex in textures:   
         tex.interpolation = 'Closest'

def reload_textures(self, context):
    materials = get_materials(context)
    textures = get_textures(materials)
    
    for tex in textures:
        tex.image.reload()

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

