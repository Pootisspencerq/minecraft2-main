from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor

app = Ursina()
from settings import *
from models import Block, WorldEdit
from ui import Menu

player = FirstPersonController()
player.x = CHUNKSIZE / 2
player.z = CHUNKSIZE / 2
player.y = 10
player.gravity = 0

sky = Sky(texture="sky_sunset")
light = DirectionalLight(shadows=True)
light.look_at(Vec3(1, -1, 1))

world = WorldEdit(player)

menu = Menu(world)
menu.toggle_menu()
mouse_locked = True
mouse_visible = False

def input(key):
    if key == 'space':  # Example: apply gravity with space key press
        player.gravity = 0.5

window.fullscreen = True
app.run()
