from widget import Widget

from widget_config_item import ConfigItemType
from const import MATRIX_SCALE

from random import randint


class WidgetObjectLayout:

    widget: Widget
    layout_manager = None
    color = None
    showing_config = False

    def __init__(self, widget: Widget, layout_manager, color = None):
        if not color: self.color = (randint(0, 255), randint(0, 255), randint(0, 255), 255)
        else: self.color = color
        self.widget = widget
        self.layout_manager = layout_manager
    
    def get_current_size(self):
        size = self.widget.get_current_size()
        if self.widget.rotation == 90 or self.widget.rotation == 270: size.reverse()
        return size
    
    def create_first_widget_bounds(self):
        return (self.widget.position[0] * MATRIX_SCALE, self.widget.position[1] * MATRIX_SCALE)

    def create_second_widget_bounds(self):
        return ((self.widget.position[0] + self.get_current_size()[0]) * MATRIX_SCALE, (self.widget.position[1] + self.get_current_size()[1]) * MATRIX_SCALE)
    
    def update_config_value(self, sender, app_data):
        #config_item = dpg.get_item_configuration(sender)["label"]
        #self.widget.configuration[config_item].value = app_data
        #self.layout_manager.render()
        self.update()
        #self.layout_manager.flush_callback()

    def destroy(self):
        #dpg.delete_item(self.get_tag())
        #dpg.delete_item(self.get_tag() + "-config-parent")
        pass
    
    def remove(self, *_):
        #self.layout_manager.remove(self)
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
        #self.layout_manager.render()
        self.update()
        #self.layout_manager.flush_callback()
    
    def rotate(self, _, app_data):
        self.widget.rotation = int(app_data)
        #self.layout_manager.render()
        self.update()
        #self.layout_manager.flush_callback()

    def toggle_showing_config(self, *_):
        #if not self.showing_config: self.layout_manager.collapse_all()
        self.showing_config = not self.showing_config
        
        #dpg.configure_item(self.get_tag() + "-config-collapse", show=self.showing_config)
    
    def create_dpg(self):
        self.widget.get_frame() # Initialize the widget's size and other attributes in case it relies on frames to do so
        
        self.update()
                    
    
    def update(self):
        pass