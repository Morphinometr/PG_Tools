import bpy
from bpy.types import Panel
from .Utils import addon_installed

#   Layout
       
class VIEW3D_PT_pg_layout(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Setup"
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
        
        if addon_installed("Texel_Density") or addon_installed("TexTools"): 
            column = layout.column(align=True)
            row = column.row(align = True)
            
            row.operator("pg.set_tex_density")
            row.prop(pg_tool, 'px_density', text='')
            
            if scene.pg_tool.px_density == 'custom':
                column.prop(pg_tool, 'px_density_custom', text='')     
        else:
            layout.label(text = '"Texel Density" or "TexTools" addon not found')
            
        row = layout.row(align = True)
        row.operator("pg.unwrap_all", text = "", icon = "SNAP_VOLUME")
        row.operator("pg.unwrap_selected")

        layout.operator("pg.reload_textures")

#   Rigging
       
class VIEW3D_PT_pg_rigging(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Rigging"
    bl_idname = "VIEW3D_PT_pg_rigging"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PG_Tools"
    
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        active_bone = context.active_pose_bone
        
        col = layout.column(align=False)

        col.operator("pg.add_bone")
        col.operator("pg.create_simple_controls")
        if active_bone and active_bone.get(context.active_pose_bone.name + "_space") is None:
            col.operator("pg.add_space_switching")
        else:
            col.operator("pg.add_space_switching", text="Edit Space Switching")
        

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
    VIEW3D_PT_pg_rigging,
    #VIEW3D_PT_dev_panel,

)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        

if __name__ == "__main__":
    register()