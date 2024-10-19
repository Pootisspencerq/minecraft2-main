from ursina import *
from ursina import Default, camera

Text.default_font = "assets/F77MinecraftRegular-0VYv.ttf"  # Ensure correct path to the font

class MenuButton(Button):
    def __init__(self, text, action, x, y, parent):
        super().__init__(text=text, on_click=action, x=x, y=y, parent=parent,
                        texture='assets//block_textures/dirt.png',
                        scale=(0.6, 0.1),
                        origin=(0, 0),
                        ignore_paused=True,
                        color=color.color(0, 0, random.uniform(0.9, 1)),
                        highlight_color=color.gray,
                        pressed_scale=1.05)

        class GameMenu (Entity):
            def __init__(self, menu, **kwargs):
                super()._init__(ignore_paused=True, **kwargs)
                self.menu = menu
                
            def input(self, key):
                if key =='escape':
                    self.menu.toggle_menu()
class Menu(Entity):
    def __init__(self, game, **kwargs):
        super().__init__(parent=camera.ui, ignore_paused=True, **kwargs)
        game.menu = self
        self.bg = Sprite(texture="assets/bg.jpg", parent=self, z=1, color=color.white, scale=0.15)
        self.title = Text(text="MINECUM", scale=5, parent=self, origin=(0, 0), x=0, y=0.35)

        MenuButton('NEW GAME', game.generate_world, 0, 0.15, self)
        MenuButton("SAVE", game.save_game, 0, 0, self)
        MenuButton("LOAD", game.load_game, 0, -0.15, self)
        MenuButton("QUIT", application.quit, 0, -0.3, self)  # Fixed exit button


    def toggle_menu(self):
        application.paused = not application.paused
        self.enabled = application.paused
        mouse.locked = not mouse.locked
        mouse.visible = not mouse.visible  # Fixed mouse visibility logic

if __name__ == "__main__":
    app = Ursina()
    menu = Menu(app)
    app.run()
