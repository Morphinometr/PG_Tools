import bpy
from bpy.types import (Panel, Operator)
bl_info = {"name": "Tools Panel",
           "description": "tools",
           "author": "Morphin",
           "version": (0, 0, 2),
           "blender": (2, 80, 0),
           "location": "View3d > Properties > View > Pixel",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "3D View", }
  
#   Custom properties
class pixel_properties(bpy.types.PropertyGroup):
    
    tex_size : bpy.props.EnumProperty(
        name = 'Texture Dimentions', 
        items = [('32', '32x32', ''),
                 ('64', '64x64', ''),
                 ('128', '128x128', ''),
                 ('256', '256x256', ''),
                 ('512', '512x512', ''),
                 ('1024', '1024x1024', ''),
                 ('2048', '2048x2048', ''),
                 ('4096', '4096x4096', '')#,
                 #('custom', 'Custom', '')
                ],
        default = '64'
        )
        
#   Functions
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

    
    return test_mat






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
        items = [('32', '32x32', ''),
                 ('64', '64x64', ''),
                 ('128', '128x128', ''),
                 ('256', '256x256', ''),
                 ('512', '512x512', ''),
                 ('1024', '1024x1024', ''),
                 ('2048', '2048x2048', ''),
                 ('4096', '4096x4096', '')
                ],
        default = '64'
        )
    
    
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None:
            return False
        
        return context.area.type == 'VIEW_3D' and context.active_object.type == 'MESH' and context.active_object.select_get()
            
    
    def invoke(self, context, event):
        scene = context.scene
        pixel_tool = scene.pixel_tool
        self.size = pixel_tool.tex_size
                    
        return self.execute(context)
        
    def execute(self, context):
        #test texture add
        tex_name = "Test x" + self.size
        
        if bpy.data.images.find(tex_name) < 0:
            texture = bpy.ops.image.new(name= tex_name, width=int(self.size), height=int(self.size), generated_type='COLOR_GRID')
        
        test_mat = bpy.data.materials["Test Material"]
        test_image_node = test_mat.node_tree.nodes["Image Texture"]
        test_image_node.image = bpy.data.images[tex_name]
        
        #bake texture add
        texture = bpy.data.images.new(name= 'Bake', width=int(self.size), height=int(self.size), alpha=True)
        texture.generated_color = (0, 0, 0, 0)

        test_image_node = test_mat.node_tree.nodes["Image Texture.001"]
        test_image_node.image = texture
        test_image_node
        
        return {'FINISHED'}


#   Panels
class VIEW3D_PT_Pixel_Model(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Model"
    bl_idname = "VIEW3D_PT_Pixel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pixel"
    
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pixel_tool = scene.pixel_tool

          
        layout.operator("mesh.optimize")
        layout.operator("mesh.test_material")
        
        row = layout.row(align = True)
        row.operator("mesh.test_texture")
        row.prop(pixel_tool, 'tex_size', text='')
        layout.operator("mesh.unwrap")
        
        
        
        
                
#   Registration
classes = (
    pixel_properties,
    VIEW3D_PT_Pixel_Model,
    MESH_OT_optimize,
    MESH_OT_unwrap,
    MESH_OT_test_material,
    MESH_OT_test_texture,
    
    )
                    
                
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.pixel_tool = bpy.props.PointerProperty(type = pixel_properties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.pixel_tool

if __name__ == "__main__":
    register()
