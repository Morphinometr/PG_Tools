import typing
import bpy, random
from bpy.types import Context, Operator, Panel, PropertyGroup
from bpy.props import EnumProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, StringProperty, BoolVectorProperty

def random_value(value_mid, value_range):
    return value_mid + (2 * value_range * random.random() - value_range)


class PG_OT_add_fcurve_noise(Operator):
    """Adds Noise modifiers to selected bones of active object"""
    bl_label = "Add Noise"
    bl_idname = "pg.add_fcurve_noise"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        items=(
            ("LOCATION", "Location", ""),
            ("ROTATION", "Rotation", ""),
            ("SCALE", "Scale", "")
        ),
        name="Noise Mode",
        description="F-Curve type to be affected. Usually it will be different values for Location, Rotation and scale Noise",
        default="LOCATION"
    )

    scale_mid: FloatProperty(name="Scale mid", description="Midpoint of the noise 'Scale' random value", default=1.0)
    scale_range: FloatProperty(name="Scale range", description="Plus minus range of the 'Scale' random value", default=2.0)
    strength_mid: FloatProperty(name="Strength mid", description="Midpoint of the noise 'Strength' random value", default=1.0)
    strength_range: FloatProperty(name="Strength range", description="Plus minus range of the 'Strength' random value", default=2.0)

    def invoke(self, context, event):
        scene = context.scene
        pg_tool = scene.pg_tool
        self.mode = pg_tool.noise_mode
        self.scale_mid = pg_tool.noise_scale_mid
        self.scale_range = pg_tool.noise_scale_range
        self.strength_mid = pg_tool.noise_strength_mid
        self.strength_range = pg_tool.noise_strength_range
                          
        return context.window_manager.invoke_props_dialog(self) 
    
    def draw(self, context):
        pg_tool = context.scene.pg_tool
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        

        col = layout.column(align=False)
        row = col.row(align=True)
        row.prop(self, 'mode', expand=True)
        col.prop(self, 'scale_mid')
        col.prop(self, 'scale_range')
        col.prop(self, 'strength_mid')
        col.prop(self, 'strength_range')
        #return self.execute(context)
    
    def execute(self, context):
        scene = context.scene
        pg_tool = scene.pg_tool
        pg_tool.noise_mode = self.mode
        pg_tool.noise_scale_mid = self.scale_mid
        pg_tool.noise_scale_range = self.scale_range
        pg_tool.noise_strength_mid = self.strength_mid
        pg_tool.noise_strength_range = self.strength_range

        bones = context.selected_pose_bones
        action_groups = context.object.animation_data.action.groups
        
        for bone in bones:
            group = action_groups.get(bone.name)
            if group is not None:
                for curve in group.channels:
                    if curve.data_path.split(sep='.')[-1].startswith(self.mode.lower()):
                        
                        mod = None
                        for modifier in curve.modifiers:
                            if modifier.name == "$PGT_Noise":
                                mod = modifier
                        if not mod:
                            mod = curve.modifiers.new(type="NOISE")
                            mod.name = "$PGT_Noise"
                        
                        mod.scale = random_value(self.scale_mid, self.scale_range)
                        mod.strength = random_value(self.strength_mid, self.strength_range)
                        mod.offset = random.random() * 200 - 100
                        mod.phase = random.random() * 200 - 100
        
        return {'FINISHED'}


class PG_OT_remove_fcurve_noise(Operator):
    """Removes Noise modifiers from selected bones of active object"""
    bl_label = "Remove Noise"
    bl_idname = "pg.remove_fcurve_noise"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(
        items=(
            ("LOCATION", "Location", ""),
            ("ROTATION", "Rotation", ""),
            ("SCALE", "Scale", "")
        ),
        name="Noise Mode",
        description="F-Curve type to be affected. Usually it will be different values for Location, Rotation and scale Noise",
        default="LOCATION"
    )

    def invoke(self, context, event):
        scene = context.scene
        pg_tool = scene.pg_tool
        self.mode = pg_tool.noise_mode
        
        return context.window_manager.invoke_props_dialog(self) 
    
    def draw(self, context):
        pg_tool = context.scene.pg_tool
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        

        col = layout.column(align=False)
        row = col.row(align=True)
        row.prop(self, 'mode', expand=True)

    def execute(self, context):
        bones = context.selected_pose_bones
        action_groups = context.object.animation_data.action.groups
        
        for bone in bones:
            group = action_groups.get(bone.name)
            if group is not None:
                for curve in group.channels:
                    if curve.data_path.split(sep='.')[-1].startswith(self.mode.lower()):
                        for modifier in curve.modifiers:
                            if modifier.name == "$PGT_Noise":
                                curve.modifiers.remove(modifier)
                        curve.modifiers.update()
        
        # force update graph editor
        bpy.ops.object.mode_set_with_submode(mode='EDIT')
        bpy.ops.object.mode_set_with_submode(mode='POSE')
        
        return {'FINISHED'}

    
class VIEW3D_PT_pg_animation(Panel):
    """Used for testing things"""
    
    bl_label = "Animation"
    bl_idname = "VIEW3D_PT_pg_animation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PG_Tools"

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def draw(self, context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        col = layout.column(align=False)
        col.operator("pg.add_fcurve_noise")
        col.operator("pg.remove_fcurve_noise")


classes = (
    PG_OT_add_fcurve_noise,
    PG_OT_remove_fcurve_noise,
    VIEW3D_PT_pg_animation,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
        
if __name__ == "__main__":
    register()

                
