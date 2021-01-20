import bpy
from bpy.types import (Panel, Operator)
bl_info = {"name": "Tools Panel",
           "description": "tools",
           "author": "Morphin",
           "version": (0, 0, 1),
           "blender": (2, 80, 0),
           "location": "View3d > Properties > View > Pixel",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "3D View", }
  

class my_properties(bpy.types.PropertyGroup):
    
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
        

#   Operators

class MESH_OT_optimize(Operator):
    """Limited dissolve selected objects"""
    bl_label = "Optimize"
    bl_idname = "mesh.optimize"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.active_object.type == 'MESH' and context.mode == 'OBJECT' and context.active_object.select_get()
    
    def execute(self, context):
        
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        bpy.ops.object.make_links_data(type='MODIFIERS')
        bpy.ops.object.convert(target='MESH')
        
        return {'FINISHED'}

class MESH_OT_unwrap(Operator):
    """Unwrap mesh"""
    bl_label = "Unwrap"
    bl_idname = "mesh.unwrap"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.active_object.type == 'MESH' and context.active_object.select_get()
            
    def execute(self, context):
        mod = context.object.mode
        bpy.ops.object.mode_set_with_submode(mode='EDIT')
        
        bpy.ops.mesh.select_mode(type="EDGE")
        bpy.ops.mesh.select_all(action = 'DESELECT')
        
        seams = bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)

        #unwrap
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0)

        
        bpy.ops.object.mode_set_with_submode(mode=mod)
    
        return {'FINISHED'}

class MESH_OT_test_material(Operator):
    """Add test meterial"""
    bl_label = "Test Material"
    bl_idname = "mesh.test_material"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.active_object.type == 'MESH' and context.active_object.select_get()
            
    def execute(self, context):
        
        #create test material
        test_mat = bpy.data.materials.new(name="Test Material")
        test_mat.use_nodes = True
        test_mat.use_fake_user = True
        
        
        principled_node = test_mat.node_tree.nodes.get('Principled BSDF')
        test_image_node = test_mat.node_tree.nodes.new("ShaderNodeTexImage")
        test_image_node.location = (-350, 200)
        
        link  = test_mat.node_tree.links.new
        link(test_image_node.outputs[0], principled_node.inputs[0])
        test_image_node.interpolation = 'Closest'
        
        #append to selected objects
        for ob in bpy.context.selected_objects :
            ob.active_material = test_mat
                
        #activeObject = bpy.context.active_object
        

    
        return {'FINISHED'}
    
    
class MESH_OT_test_texture(Operator):
    """Add test texture"""
    bl_label = "Test Texture"
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
        return context.area.type == 'VIEW_3D' and context.active_object.type == 'MESH' and context.active_object.select_get()
            
    
    def invoke(self, context, event):
        scene = context.scene
        pixel_tool = scene.pixel_tool
        self.size = pixel_tool.tex_size
            
        return self.execute(context)
        
    def execute(self, context):
        bpy.ops.image.new(name="Test x" + self.size, width=int(self.size), height=int(self.size), generated_type='COLOR_GRID')
        
        return {'FINISHED'}


#     Panels

class VIEW3D_PT_Pixel(Panel):
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
        layout.operator("mesh.unwrap")
        layout.operator("mesh.test_material")
        
        row = layout.row(align = True)
        row.operator("mesh.test_texture")
        row.prop(pixel_tool, 'tex_size', text='')
        
        
        
        
                
        
classes = (
    my_properties,
    VIEW3D_PT_Pixel,
    MESH_OT_optimize,
    MESH_OT_unwrap,
    MESH_OT_test_material,
    MESH_OT_test_texture,
    
    )
                    
                
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.pixel_tool = bpy.props.PointerProperty(type = my_properties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.pixel_tool

if __name__ == "__main__":
    register()
