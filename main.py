from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor

app = Ursina()
from settings import *
from models import Block, WorldEdit
from ui import Menu
player  = FirstPersonController()
player.x = CHUNKSIZE/2
player.z = CHUNKSIZE/2
player.y = 10
player.gravity = 0

sky = Sky(texture="sky_sunset")
light = DirectionalLight(shadows=True)
light.look_at(Vec3(1,-1,1))


world = WorldEdit(player)

menu=Menu(world)
menu.toggle_menu()
mouse_locked =False
mouse_visible=True

def input(key):
    player.gravity = 0.5
# scene.fog_density = (5, 50)   # sets linear density start and end
# axe = Entity(model='assets\\minecraft_diamond-pickaxe\\scene', scale=0.05, collider='box')


window.fullscreen = True
app.run()
