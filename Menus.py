import bpy
#from .Operators import PIXEL_OT_simple_controls as scontrols


class ControlBonesMenu(bpy.types.Menu):
    bl_label = "Add Simple Control Bones Menu"
    bl_idname = "pixel.control_bones_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("wm.open_mainfile")
        layout.operator("wm.save_as_mainfile")



















def register():
    bpy.utils.register_class(ControlBonesMenu)


def unregister():
    bpy.utils.unregister_class(ControlBonesMenu)

if __name__ == "__main__":
    register()

    # The menu can also be called from scripts
    #bpy.ops.wm.call_menu(name=ControlBonesMenu.bl_idname)