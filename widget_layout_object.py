from widget import Widget
import dearpygui.dearpygui as dpg

from widget_config_item import ConfigItemType
from const import MATRIX_SCALE

from random import randint


class WidgetObjectLayout:

    widget: Widget = None
    layout_manager = None
    widget_id: int = None
    color = None
    showing_config = False

    def __init__(self, widget: Widget, layout_manager, wid: int, color = None):
        if not color: self.color = (randint(0, 255), randint(0, 255), randint(0, 255), 255)
        else: self.color = color
        self.widget = widget
        self.layout_manager = layout_manager
        self.widget_id = wid

    def get_tag(self):
        return "widget-" + str(self.widget_id)
    
    def get_current_size(self):
        size = self.widget.get_current_size()
        if self.widget.rotation == 90 or self.widget.rotation == 180: size.reverse()
        return size
    
    def create_first_widget_bounds(self):
        return (self.widget.position[0] * MATRIX_SCALE, self.widget.position[1] * MATRIX_SCALE)

    def create_second_widget_bounds(self):
        return ((self.widget.position[0] + self.get_current_size()[0]) * MATRIX_SCALE, (self.widget.position[1] + self.get_current_size()[1]) * MATRIX_SCALE)
    
    def update_config_value(self, sender, app_data):
        config_item = dpg.get_item_configuration(sender)["label"]
        self.widget.configuration[config_item].value = app_data
        self.layout_manager.render()
        self.update()
        self.layout_manager.flush_callback()

    def destroy(self):
        dpg.delete_item(self.get_tag())
        dpg.delete_item(self.get_tag() + "-config-parent")
    
    def remove(self, *_):
        self.layout_manager.remove(self)
        self.destroy()

    def edit_color(self, _, app_data):
        self.color = app_data
        for i in range(0, len(self.color)):
            self.color[i] *= 255
            self.color[i] = int(self.color[i])
        self.update()

    def move_manual(self, is_x, value):
        if is_x:
            self.widget.position[0] = value
        else:
            self.widget.position[1] = value
        self.layout_manager.render()
        self.update()
        self.layout_manager.flush_callback()
    
    def rotate(self, _, app_data):
        self.widget.rotation = int(app_data)
        self.layout_manager.render()
        self.update()
        self.layout_manager.flush_callback()

    def toggle_showing_config(self, *_):
        if not self.showing_config: self.layout_manager.collapse_all()
        self.showing_config = not self.showing_config
        
        dpg.configure_item(self.get_tag() + "-config-collapse", show=self.showing_config)
    
    def create_dpg(self):
        self.widget.get_frame() # Initialize the widget's size and other attributes in case it relies on frames to do so
        dpg.draw_rectangle(
            self.create_first_widget_bounds(), 
            self.create_second_widget_bounds(), 
            tag = self.get_tag(),
            fill = self.color,
            parent="widget-layout-parent"
        )
        with dpg.group(horizontal=True, parent="widget-configurations", tag=self.get_tag() + "-config-parent"):
            dpg.add_color_edit(self.color, tag=self.get_tag() + "-color", callback=self.edit_color, no_inputs=True)
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_button(label = str(self.widget_id + 1) + ": " + self.widget.name, callback=self.toggle_showing_config)
                    dpg.add_button(label = "Delete", callback = self.remove)
                with dpg.group(show=self.showing_config, tag=self.get_tag() + "-config-collapse"):
                    dpg.add_text("Transformation")
                    dpg.add_input_int(label="X", callback=lambda _, app_data: self.move_manual(True, app_data), tag=self.get_tag() + "-pos-x")
                    dpg.add_input_int(label="Y", callback=lambda _, app_data: self.move_manual(False, app_data), tag=self.get_tag() + "-pos-y")
                    if self.widget.allow_rotation:
                        dpg.add_combo([0, 90, 180, 270], label="Rotation (deg)", callback=self.rotate, default_value=self.widget.rotation)
                    dpg.add_text("Configuration")
                    for config_key in self.widget.configuration.keys():
                        value = self.widget.configuration[config_key]
                        args = {"label": config_key, "default_value": value.value, "callback": self.update_config_value}
                        if value.config_item_type == ConfigItemType.text:
                            dpg.add_input_text(**args)
                        elif value.config_item_type == ConfigItemType.integer:
                            dpg.add_input_int(**args, min_value=value.minimum, max_value=value.maximum, min_clamped=True, max_clamped=True)
                        elif value.config_item_type == ConfigItemType.float:
                            dpg.add_input_float(**args, min_value=value.minimum, max_value=value.maximum, min_clamped=True, max_clamped=True)
                        elif value.config_item_type == ConfigItemType.integer_list:
                            dpg.add_input_intx(**args, size=len(value), min_value=value.minimum, max_value=value.maximum, min_clamped=True, max_clamped=True)
                        elif value.config_item_type == ConfigItemType.float_list:
                            dpg.add_input_floatx(**args, size=len(value), min_value=value.minimum, max_value=value.maximum, min_clamped=True, max_clamped=True)
                        elif value.config_item_type == ConfigItemType.boolean:
                            dpg.add_checkbox(**args)
                        elif value.config_item_type == ConfigItemType.combo:
                            print(value.options)
                            dpg.add_combo(value.options, **args)
                        else:
                            raise TypeError("Config item type unaccounted for: " + str(value.config_item_type))
        
        self.update()
                    
    
    def update(self):

        dpg.configure_item(
            self.get_tag(), 
            pmin = self.create_first_widget_bounds(), 
            pmax = self.create_second_widget_bounds(),
            fill = self.color)
        
        dpg.set_value(
            self.get_tag() + "-pos-x",
            self.widget.position[0]
        )
        dpg.set_value(
            self.get_tag() + "-pos-y",
            self.widget.position[1]
        )