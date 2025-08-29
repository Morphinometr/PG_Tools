import bpy
from mathutils import Vector

corners = {
    'LEFT_UP' : Vector((0, 1)),
    'LEFT_DOWN' : Vector((0, 0)),
    'RIGHT_UP' : Vector((1, 1)),
    'RIGHT_DOWN' : Vector((1, 0)),
}

objects = bpy.context.selected_objects
cur_mode = mod = bpy.context.object.mode

old_image = Vector((64, 64))
new_image = Vector((32, 64))

scale = Vector(x / y for x, y in zip(old_image, new_image))
anchor = corners['LEFT_UP']



bpy.ops.object.mode_set_with_submode(mode='OBJECT')

for ob in objects:
    for point in ob.data.uv_layers.active.data.values():
        uv = point.uv
        point.uv = (uv - anchor) * scale + anchor


bpy.ops.object.mode_set_with_submode(mode=cur_mode)
