import bpy
from bpy.types import (Panel)
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

    
    

class MESH_OT_Optimize(bpy.types.Operator):
    bl_label = "Optimize"
    bl_idname = "mesh.optimize"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.active_object.type == 'MESH'
            
            
    
    def execute(self, context):
        
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        bpy.ops.object.modifier_apply(modifier="Decimate", report=True)

        
        return {'FINISHED'}


class VIEW3D_PT_Pixel(Panel):
    """Creates a Panel in the scene context of the 3D view N panel"""
    
    bl_label = "Model"
    bl_idname = "VIEW3D_PT_Pixel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pixel"
    
    
    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        
        row = column.row(align=True)
        
        column.operator("mesh.optimize", text='Optimize')
        
                
        
classes = (
    VIEW3D_PT_Pixel,
    MESH_OT_Optimize
    
    )
                    
                
def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
