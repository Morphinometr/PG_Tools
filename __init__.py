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

import bpy
import os
from bpy.props import (
    BoolProperty,
    PointerProperty,
)
from bpy.types import (
    PropertyGroup,
    AddonPreferences,
)


bl_info = {
    "name": "PixelGun Tools",
    "author": "Morphin",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "description": "PixelGun pipeline tools",
    "location": "Addons Preferences",
    "warning": "",
    "doc_url": "https://github.com/Morphinometr/Pixel_Tools",
    "category": "3D View"
    }

from . import ToolsPanel 
    
def register():
    ToolsPanel.register()


def unregister():
    ToolsPanel.unregister()


if __name__ == "__main__":
    register()



