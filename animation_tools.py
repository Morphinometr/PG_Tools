import bpy, random
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import EnumProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, StringProperty, BoolVectorProperty

class pg_anim_noise_properties(PropertyGroup):
    
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

    scale_mid: FloatProperty(name="Scale", description="Midpoint of the noise 'Scale' random value", default=1.0)
    scale_range: FloatProperty(name="± Scale", description="Plus minus range of the 'Scale' random value", subtype="PERCENTAGE", default=5.0, min=0, soft_max=100)
    strength_mid: FloatProperty(name="Strength", description="Midpoint of the noise 'Strength' random value", default=1.0)
    strength_range: FloatProperty(name="± Strength", description="Plus minus range of the 'Strength' random value", subtype="PERCENTAGE", default=5.0, min=0, soft_max=100)
    


def random_value(value_mid, value_range):
    return value_mid + (2 * value_range * random.random() - value_range)


class PG_OT_add_fcurve_noise(Operator):
    """Adds Noise modifiers to selected bones of active object"""
    bl_label = "Add Noise"
    bl_idname = "pg.add_fcurve_noise"
    bl_options = {'REGISTER', 'UNDO'}

    action: EnumProperty(
        items=(
            ("ADD", "Add", ""),
            ("REMOVE", "Remove", ""),
            ("UPDATE", "Update", "")
        )
    )

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

    scale_mid: FloatProperty(name="Scale", description="Midpoint of the noise 'Scale' random value", default=1.0)
    scale_range: FloatProperty(name="± Scale", description="Plus minus range of the 'Scale' random value", subtype="PERCENTAGE", default=5.0, min=0, soft_max=100)
    strength_mid: FloatProperty(name="Strength", description="Midpoint of the noise 'Strength' random value", default=1.0)
    strength_range: FloatProperty(name="± Strength", description="Plus minus range of the 'Strength' random value", subtype="PERCENTAGE", default=5.0, min=0, soft_max=100)

    def invoke(self, context, event):
        scene = context.scene        
        try:
            pg_tool = scene.pg_anim_noise_properties
        except (AttributeError):
            bpy.types.Scene.pg_anim_noise_properties = bpy.props.PointerProperty( type = pg_anim_noise_properties)
            pg_tool = scene.pg_anim_noise_properties

        self.mode = pg_tool.noise_mode
        self.scale_mid = pg_tool.scale_mid
        self.scale_range = pg_tool.scale_range
        self.strength_mid = pg_tool.strength_mid
        self.strength_range = pg_tool.strength_range
                          
        return context.window_manager.invoke_props_dialog(self) 
    
    def draw(self, context):
        pg_tool = context.scene.pg_tool
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = False
        

        row = layout.row(align=True)
        row.prop(self, 'mode', expand=True)
        
        layout.use_property_split = True
        col = layout.column(align=False)
        row = col.row(align=True)
        row.prop(self, 'scale_mid')
        #row.label(text=" ")
        row.prop(self, 'scale_range', text="±")

        row = col.row(align=True)
        row.prop(self, 'strength_mid')
        row.prop(self, 'strength_range', text="±")
        
    
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
        try:
            pg_tool = scene.pg_anim_noise_properties
        except (AttributeError):
            return {"CANCELLED"}
        
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
        row = col.row(align=True)
        row.operator("pg.add_fcurve_noise").action = "ADD"
        row.operator("pg.add_fcurve_noise", text="", icon="DECORATE_OVERRIDE").action = "UPDATE"
        #row.label(text="±")
        row.operator("pg.remove_fcurve_noise", text="", icon="CANCEL")


classes = (
    PG_OT_add_fcurve_noise,
    PG_OT_remove_fcurve_noise,
    VIEW3D_PT_pg_animation,
    pg_anim_noise_properties
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
        
if __name__ == "__main__":
    register()

                
'''
class MultiDataPanel(bpy.types.Panel):
    """testing panel showing multiple subpanels"""
    bl_label = 'Multi data Panel'
    bl_idname = 'OBJECT_PT_multidata'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scn = context.scene
        layout = self.layout

        box = layout.box()
        col = box.column()
        row = col.row()
        if scn.show_options_01:
            row.prop(scn, "show_options_01", icon="DOWNARROW_HLT", text="", emboss=False)
        else:
            row.prop(scn, "show_options_01", icon="RIGHTARROW", text="", emboss=False)

        row.label('First sub panel')
        if scn.show_options_01:
            # Add items from other panels draw method here
            row = col.row()
            row.label('Render resolution')
            row = col.row()
            col = row.column(align=True)
            col.prop(scn.render, 'resolution_x', text='X')
            col.prop(scn.render, 'resolution_y', text='Y')

            row = col.row()
            row.label('and more rows for other data')
            # end of other panels draw method

        box = layout.box()
        col = box.column()
        row = col.row()
        if scn.show_options_02:
            row.prop(scn, "show_options_02", icon="DOWNARROW_HLT", text="", emboss=False)
        else:
            row.prop(scn, "show_options_02", icon="RIGHTARROW", text="", emboss=False)

        row.label('Second sub panel')
        if scn.show_options_02:
            # Add items from other panels draw method here
            row = col.row()
            row.label('Frame range')
            row = col.row()
            col = row.column(align=True)
            col.prop(scn, 'frame_start', text='Start Frame')
            col.prop(scn, 'frame_end', text='End Frame')
            col.prop(scn, 'frame_step', text='Frame Step')
            row = col.row()
            row.label('and more rows for other data')
            # end of other panels draw method

        box = layout.box()
        col = box.column()
        row = col.row()
        if scn.show_options_03:
            row.prop(scn, "show_options_03", icon="DOWNARROW_HLT", text="", emboss=False)
        else:
            row.prop(scn, "show_options_03", icon="RIGHTARROW", text="", emboss=False)

        row.label('Third sub panel')
        if scn.show_options_03:
            # Add items from other panels draw method here
            row = col.row()
            row.label('Render output')
            row = col.row()
            col = row.column(align=True)
            col.prop(scn.render, 'filepath')
            row = col.row()
            row.label('and more rows for other data')
            # end of other panels draw method


def register():
    bpy.utils.register_class(MultiDataPanel)
    bpy.types.Scene.show_options_01 = bpy.props.BoolProperty(name='Show 1st panel', default=False)
    bpy.types.Scene.show_options_02 = bpy.props.BoolProperty(name='Show 2nd panel', default=False)
    bpy.types.Scene.show_options_03 = bpy.props.BoolProperty(name='Show 3rd panel', default=False)

def unregister():
    del bpy.types.Scene.show_options_01
    del bpy.types.Scene.show_options_02
    del bpy.types.Scene.show_options_03
    bpy.utils.unregister_class(MultiDataPanel)
'''