import bpy
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty, IntProperty, FloatProperty, StringProperty, BoolVectorProperty

#   Custom properties

class PG_properties(bpy.types.PropertyGroup):
    
    tex_size : EnumProperty(
        name = 'Texture Dimensions', 
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
    
    px_density : EnumProperty(
        name = 'Pixel Density',
        items = [('10', '10 px/m', ''),
                 ('16', '16 px/m', ''),
                 ('32', '32 px/m', ''),
                 ('1000', '1000 px/m', ''),
                 ('custom', 'Custom', ''),
                ],
        default = '16'
        )
        
    px_density_custom : FloatProperty(name="Custom Pixel Density", min = 0 )
    tex_size_custom_y : IntProperty(name="Custom texture size Y", min = 1, default = 64 )
    tex_size_custom_x : IntProperty(name="Custom texture size X", min = 1, default = 64 )
    reset_colors : BoolProperty(name="Reset Colors", default = False)
    
    weapon_tag : StringProperty(name="Weapon Tag", default = "")
    weapon_number : StringProperty(name="Weapon Number", default = "")
    avatar_tag : StringProperty(name="Avatar Tag", default = "")

    noise_mode: EnumProperty(
        items=(
            ("LOCATION", "Location", ""),
            ("ROTATION", "Rotation", ""),
            ("SCALE", "Scale", "")
        ),
        name="Noise Mode",
        description="F-Curve type to be affected. Usually it will be different values for Location, Rotation and scale Noise",
        default="LOCATION"
    )
    noise_scale_mid: FloatProperty(name="Scale mid", description="Midpoint of the noise 'Scale' random value", default=1.0)
    noise_scale_range: FloatProperty(name="Scale range", description="Plus minus range of the 'Scale' random value", default=2.0)
    noise_strength_mid: FloatProperty(name="Strength mid", description="Midpoint of the noise 'Strength' random value", default=1.0)
    noise_strength_range: FloatProperty(name="Strength range", description="Plus minus range of the 'Strength' random value", default=2.0)
    
classes = (
    PG_properties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.pg_tool = bpy.props.PointerProperty(type = PG_properties)


def unregister():
    del bpy.types.Scene.pg_tool
    for cls in classes:
        bpy.utils.unregister_class(cls)