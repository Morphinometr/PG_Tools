import bpy
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

    
    




class VIEW3D_PT_Pixel(bpy.types.Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Pixel"
    bl_idname = "VIEW3D_PT_Pixel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    
    
    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        
        row = column.row(align=True)
        
        
                
        column.prop(context.preferences.inputs, "use_rotate_around_active")
        
        column.prop(context.preferences.edit, "use_mouse_depth_cursor")
        
        column.prop(context.preferences.inputs, "use_mouse_emulate_3_button")
        
classes = (
    VIEW3D_PT_Pixel,
    
    )
                    
                
def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

