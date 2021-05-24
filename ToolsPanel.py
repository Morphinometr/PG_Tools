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
                 ('custom', 'Custom', ''),
                ],
        default = '10'
        )
        
    tex_size_custom_x : bpy.props.IntProperty(name="Custom texture size X", min = 1, default = 64 )
    tex_size_custom_y : bpy.props.IntProperty(name="Custom texture size Y", min = 1, default = 64 )
    px_density_custom : bpy.props.FloatProperty(name="Custom Pixel Density", min = 0 )
    
              
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
    test_image_node.interpolation = 'Closest'

    
    return test_mat

def texture_pixel_filter(self, context):
    materials = []
    textures = []
    
    for ob in context.selected_objects:
        for slot in ob.material_slots:
            if slot.material not in materials:
                materials.append(slot.material) 

    for mat in materials:
        for node in mat.node_tree.nodes:
             if node.type == 'TEX_IMAGE':
                 textures.append(node)
           
    for tex in textures:   
         tex.interpolation = 'Closest'

def addon_installed(name):
    addons = bpy.context.preferences.addons.keys()
    for ad in addons:
        if ad.find(name) > -1:
            return True
    return False




    
    

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
        test_image_node         #???
        
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
        if len(context.selected_objects) < 1:
            return False
        
        return (context.area.type == 'VIEW_3D' 
                
                )
            
    def execute(self, context):
        texture_pixel_filter(self, context)
        
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
                 ('custom', 'custom', ''),
                ],
        default = '10'
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
                


#   Panels

class VIEW3D_PT_Pixel_Model(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Modeling"
    bl_idname = "VIEW3D_PT_Pixel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pixel"
    
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pixel_tool = scene.pixel_tool

        layout.operator("mesh.texture_pixel_filter")  
        layout.operator("mesh.optimize")
        layout.operator("mesh.test_material")
                
        column = layout.column(align=True)
        row = column.row(align = True)
        
        row.operator("mesh.test_texture")
        row.prop(pixel_tool, 'tex_size', text='')
        if scene.pixel_tool.tex_size == 'custom':
            row = column.row(align = True) 
            row.prop(pixel_tool, 'tex_size_custom_x', text='')
            row.prop(pixel_tool, 'tex_size_custom_y', text='')
        
        layout.operator("mesh.unwrap")
        
        box = layout.box()
        if addon_installed('Texel_Density'): 
            column = box.column(align=True)
            row = column.row(align = True)
            
            row.operator("mesh.set_tex_desity")
            row.prop(pixel_tool, 'px_density', text='')
            
            if scene.pixel_tool.px_density == 'custom':
                column.prop(pixel_tool, 'px_density_custom', text='')
            
            
            
            
        else:
            box.label(text = '"Texel Density" addon not found')
        
        
        
        
                
#   Registration

classes = (
    pixel_properties,
    VIEW3D_PT_Pixel_Model,
    MESH_OT_optimize,
    MESH_OT_unwrap,
    MESH_OT_test_material,
    MESH_OT_test_texture,
    MESH_OT_texture_pixel_filter,
    MESH_OT_set_tex_desity,
    
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
