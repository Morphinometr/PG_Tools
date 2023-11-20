# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# Contributed to by meta-androcto, pitiwazou, chromoly, italic, morphin

if "bpy" in locals():
    import importlib
    importlib.reload(Operators)
    importlib.reload(Panels)
    importlib.reload(localization)
    importlib.reload(animation_tools)
    importlib.reload(properties)

else:
    from . import Operators
    from . import Panels
    from . import localization
    from . import animation_tools
    from . import properties

import bpy
import os
from bpy.props import (
    BoolProperty,
    PointerProperty,
    StringProperty,
    IntProperty
)
from bpy.types import (
    PropertyGroup,
    AddonPreferences,
    Operator
)

bl_info = {
    "name": "PG Tools",
    "author": "Kharkovschenko Konstantin",
    "version": (0, 3, 0),
    "blender": (4, 0, 0),
    "description": "PixelGun pipeline tools",
    "location": "Addons Preferences",
    "warning": "",
    "doc_url": "https://github.com/Morphinometr/Pixel_Tools",
    "category": "3D View"
    }

class PGToolsPreferences(AddonPreferences):
    bl_idname = __package__

    project_filepath : StringProperty(
        name="PixelGun Project directory",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "project_filepath")


class OBJECT_OT_pg_tools_prefs(Operator):
    """Display preferences"""
    bl_idname = "pg.pg_tools_prefs"
    bl_label = "Add-on Preferences"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        info = ("Path: %s" % addon_prefs.project_filepath)

        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}

modules = (
    Operators,
    Panels,
    animation_tools,
    properties,

)

classes = (
    OBJECT_OT_pg_tools_prefs,
    PGToolsPreferences,

)
    
def register():
    for mod in modules:
        mod.register()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.translations.register(__name__, localization.langs)

def unregister():
    for mod in modules:
        mod.unregister()
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.translations.unregister(__name__)

if __name__ == "__main__":
    register()



