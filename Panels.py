import bpy
from bpy.types import Panel
from .Operators import addon_installed

#   Layout
       
class VIEW3D_PT_pixel_layout(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Layout"
    bl_idname = "VIEW3D_PT_pixel_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PixelGun"
    
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column(align=False)
        
        col.prop(scene.pixel_tool, "weapon_tag")
        col.prop(scene.pixel_tool, "weapon_number")
        col.prop(scene.pixel_tool, "avatar_tag")
        
        layout.operator("pixel.import_weapon")
        layout.operator("pixel.fix_import")
        layout.operator("pixel.combine_rigs")

#   Modeling

class VIEW3D_PT_pixel_modeling(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Modeling"
    bl_idname = "VIEW3D_PT_pixel_modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PixelGun"
    
    
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
            
        layout.operator("mesh.reload_textures")

#   Riging
       
class VIEW3D_PT_pixel_riging(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Riging"
    bl_idname = "VIEW3D_PT_pixel_riging"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PixelGun"
    
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column(align=False)

        col.operator("pixel.add_bone")
        col.operator("pixel.create_simple_controls")
        

#   Dev

class VIEW3D_PT_dev_panel(Panel):
    """Used for testing things"""
    
    bl_label = "***Dev***"
    bl_idname = "VIEW3D_PT_dev_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PixelGun"

    def draw(self, context):
        layout = self.layout
        layout.operator("pixel.test")


        

#   Registration

classes = (
    VIEW3D_PT_pixel_modeling,
    VIEW3D_PT_pixel_layout,
    VIEW3D_PT_pixel_riging,
    VIEW3D_PT_dev_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        

if __name__ == "__main__":
    register()