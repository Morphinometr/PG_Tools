import bpy
from bpy.types import Panel
from .Utils import addon_installed

#   Layout
       
class VIEW3D_PT_pg_layout(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Layout"
    bl_idname = "VIEW3D_PT_pg_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PG_Tools"
    
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column(align=False)
        
        col.prop(scene.pg_tool, "avatar_tag")
        col.prop(scene.pg_tool, "weapon_tag")
        col.prop(scene.pg_tool, "weapon_number")
                
        layout.operator("pg.import_avatar")
        layout.operator("pg.import_weapon")
        layout.operator("pg.fix_import")

        if not addon_installed('space_view3d_copy_attributes'):
            layout.label(text='Please enable "Interface: Copy Attributes Menu" addon to automatically rotate avatar arms to match weapon arms', icon = 'ERROR')
        layout.operator("pg.combine_rigs")

#   Modeling

class VIEW3D_PT_pg_modeling(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Modeling"
    bl_idname = "VIEW3D_PT_pg_modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PG_Tools"
    
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pg_tool = scene.pg_tool

        row = layout.row(align = True)
        row.operator("pg.find_instances")
        row.operator("pg.reset_ob_colors", text = "", icon = "CANCEL") 

        layout.operator("pg.texture_pixel_filter")  
        layout.operator("pg.optimize")
        layout.operator("pg.test_material")
                
        column = layout.column(align=True)
        row = column.row(align = True)
        
        row.operator("pg.test_texture")
        row.prop(pg_tool, 'tex_size', text='')
        if scene.pg_tool.tex_size == 'custom':
            row = column.row(align = True) 
            row.prop(pg_tool, 'tex_size_custom_x', text='')
            row.prop(pg_tool, 'tex_size_custom_y', text='')
        
        layout.operator("pg.unwrap")
        
        
        box = layout.box()
        if addon_installed('Texel_Density'): 
            column = box.column(align=True)
            row = column.row(align = True)
            
            row.operator("pg.set_tex_desity")
            row.prop(pg_tool, 'px_density', text='')
            
            if scene.pg_tool.px_density == 'custom':
                column.prop(pg_tool, 'px_density_custom', text='')     
        else:
            box.label(text = '"Texel Density" addon not found')
            
        layout.operator("pg.reload_textures")

#   Riging
       
class VIEW3D_PT_pg_riging(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Riging"
    bl_idname = "VIEW3D_PT_pg_riging"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PG_Tools"
    
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column(align=False)

        col.operator("pg.add_bone")
        col.operator("pg.create_simple_controls")
        col.operator("pg.add_space_switching")
        

#   Dev

class VIEW3D_PT_dev_panel(Panel):
    """Used for testing things"""
    
    bl_label = "***Dev***"
    bl_idname = "VIEW3D_PT_dev_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PG_Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("pg.test")
        

        

#   Registration

classes = (
    VIEW3D_PT_pg_modeling,
    VIEW3D_PT_pg_layout,
    VIEW3D_PT_pg_riging,
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