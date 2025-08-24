from ursina import *

class MainMenu(Entity):
    def __init__(self,player):
        super().__init__(
            parent = camera.ui
            )
        self.main_menu = Entity(parent = self, enabled = True)
        self.pause_menu = Entity(parent = self, enabled = False)
        self.player = player
        def start():
            self. player.enable()
            self.main_menu.disable()

        def resume():
            mouse.locked = True
            self.pause_menu.disable()

        def main_menu():
            self.main_menu.enable()
            self.pause_menu.disable()

        Everland = Text(text='E V E R L A N D', text_color=color.orange, position=Vec2(-0.25, 0.3), parent=self.main_menu, scale=3)

        BG = Entity(parent = self, image='brick')
        start_button = Button(text = "S t a r t - G a m e", color = color.black, scale_y = 0.1, scale_x = 0.3, y = 0.02, parent = self.main_menu)
        settings_button = Button(text = "S e t t i n g s", color = color.black, scale_y = 0.1, scale_x = 0.3, y = -0.1, parent = self.main_menu)
        Freinds_button = Button(text = "F r i e n d s", color = color.black, scale_y = 0.1, scale_x = 0.3, y = -0.22, parent = self.main_menu)
        quit_button = Button(text = "Q u i t", color = color.black, scale_y = 0.1, scale_x = 0.3, y = -0.34, parent = self.main_menu)
        quit_button.on_click = application.quit
        start_button.on_click = Func(start)

        p_resume_button = Button(text = "R e s u m e", color = color.black, scale_y = 0.1, scale_x = 0.3, y = 0.23, parent = self.pause_menu)
        p_settings_button = Button(text = "S e t t i n g s", color = color.black, scale_y = 0.1, scale_x = 0.3, y = -0.01, parent = self.pause_menu)
        quit_button = Button(text = "Q u i t", color = color.black, scale_y = 0.1, scale_x = 0.3, y = -0.22, parent = self.pause_menu)
        quit_button.on_click = application.quit
        p_resume_button.on_click = Func(resume)