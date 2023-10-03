import bpy, random

operation = 'location'
#operation = 'rotation'
#operation = 'scale'

scale_mid = 1
scale_range = 2
strength_mid = 1
strength_range = 2

scale = scale_mid + (scale_range * random.random() - scale_range/2)

C = bpy.context
D = bpy.data
arm = C.object

bones = C.selected_pose_bones
action_groups = arm.animation_data.action.groups

def random_value(value_mid, value_range):
    return value_mid + (value_range * random.random() - value_range/2)

print('--')
for bone in bones:
    group = action_groups.get(bone.name)
    if group is not None:
        for curve in group.channels:
            if curve.data_path.split(sep='.')[-1] == operation:
                #print(curve.array_index)
                mod = curve.modifiers.new(type="NOISE")
                mod.scale = random_value(scale_mid, scale_range)
                mod.strength = random_value(strength_mid, strength_range)
                mod.offset = random.random() * 200 - 100
                mod.phase = random.random() * 200 - 100
                
