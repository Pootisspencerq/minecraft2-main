from ursina import *
from settings import *
from ursina.shaders import basic_lighting_shader
from perlin_noise import PerlinNoise
import pickle
from random import randint

# Sound setup
background_music = Audio('background_music.mp3', loop=True, autoplay=True)  # Background music
destroy_sound = Audio('metalbox-break3.mp3', autoplay=False)  # Destroy sound
place_sound = Audio('clash-royale-hog-rider.mp3', autoplay=False)  # Place block sound
scroll_sound = Audio('scroll_sound.mp3', autoplay=False)  # Scroll sound
save_sound = Audio('save_game.mp3', autoplay=False)  # Save game sound
load_sound = Audio('load_game.mp3', autoplay=False)  # Load game sound

scene.trees = {}

class Tree(Entity):
    def __init__(self, pos, **kwargs):
        super().__init__(
            parent=scene,
            model='assets\\minecraft_tree\\scene',  # Model of the tree
            scale=randint(3,5),
            collider='box',
            position=pos,
            shader=basic_lighting_shader,
            origin_y=0.6,
            **kwargs) 
        scene.trees[(self.x, self.y, self.z)] = self  

class Block(Button):
    id = 3  # Default block ID
    def __init__(self, pos, parent_world, block_id=3, **kwargs):
        super().__init__(
            parent=parent_world,
            model='cube',  # Block model
            texture=block_textures[block_id],
            scale=1,
            collider='box',
            position=pos,
            color=color.color(0,0, random.uniform(0.9, 1)),
            highlight_color=color.gray,
            shader=basic_lighting_shader,
            origin_y=-0.5,
            **kwargs)   
        parent_world.blocks[(self.x, self.y,self.z)] = self  
        self.id = block_id

class Chunk(Entity):
    def __init__(self, chunk_pos, **kwargs):
        super().__init__(model=None, collider=None, shader=basic_lighting_shader, **kwargs)
        self.chunk_pos = chunk_pos
        self.blocks = {}
        self.noise = PerlinNoise(octaves=2, seed=3504)
        self.is_simplify = False
        self.default_texture = 3
        self.generate_chunk()

    def simplify_chunk(self):
        """Simplify chunk to optimize performance."""
        if self.is_simplify:
            return
        
        self.model = self.combine()
        self.collider = 'mesh'
        self.texture = block_textures[self.default_texture]

        for block in self.blocks.values():
            destroy(block)

        self.is_simplify = True

    def detail_chunk(self):
        """Revert the chunk to detailed blocks when needed."""
        if not self.is_simplify:
            return

        self.model = None
        self.collider = None
        self.texture = None

        for pos, block in self.blocks.items():
            new_block = Block(pos, self, block_id=block.id)
        
        self.is_simplify = False

    def generate_chunk(self):
        cx, cz = self.chunk_pos 
        for x in range(CHUNKSIZE):
            for z in range(CHUNKSIZE):
                block_x = cx * CHUNKSIZE + x
                block_z = cz * CHUNKSIZE + z
                y = floor(self.noise([block_x/24, block_z/24])*6)
                block = Block((block_x, y, block_z), self)

                if randint(0, 200) == 52:
                    Tree((block_x, y+1, block_z))

class WorldEdit(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.chunks = {}
        self.current_chunk = None
        self.player = player

    def generate_world(self):
        for x in range(WORLDSIZE):
            for z in range(WORLDSIZE):
                chunk_pos = (x, z)
                if chunk_pos not in self.chunks:
                    chunk = Chunk(chunk_pos)
                    self.chunks[chunk_pos] = chunk

    def save_game(self):
        game_data = {
            "player_pos": (self.player.x, self.player.y, self.player.z),
            'chunks': [],
            'trees': [],
        }
        for chunk_pos, chunk in self.chunks.items():
            blocks_data = [(block_pos, block.id) for block_pos, block in chunk.blocks.items()]
            game_data["chunks"].append((chunk_pos, blocks_data))

        for tree_pos, tree in scene.trees.items():
            game_data['trees'].append((tree_pos, tree.scale))

        with open('save.dat', 'wb') as file:
            pickle.dump(game_data, file)
        save_sound.play()  # Play save sound when the game is saved

    def clear_world(self):
        for chunk in self.chunks.values():
            for block in chunk.blocks.values():
                destroy(block)
            destroy(chunk)

        for tree in scene.trees.values():
            destroy(tree)

        scene.trees.clear()
        self.chunks.clear()

    def load_world(self, chunk_data, tree_data):
        for chunk_pos, blocks in chunk_data:
            chunk = Chunk(chunk_pos)
            for block_pos, block_id in blocks:
                Block(block_pos, chunk, block_id)
            self.chunks[chunk_pos] = chunk

        for tree_pos, tree_scale in tree_data:
            tree = Tree(tree_pos)
            tree.scale = tree_scale

    def load_game(self):
        with open('save.dat', 'rb') as file:
            game_data = pickle.load(file)
        self.clear_world()
        self.player.x, self.player.y, self.player.z = game_data["player_pos"]
        self.load_world(game_data["chunks"], game_data['trees'])
        load_sound.play()  # Play load sound when the game is loaded
        print("Game loaded.")

    def input(self, key):
        if key == 'k':
            self.save_game()
        if key == 'l':
            self.load_game()

        if key == 'left mouse down':
            hit_info = raycast(camera.world_position, camera.forward, distance=10)
            if hit_info.hit:
                block = Block(hit_info.entity.position + hit_info.normal, hit_info.entity.parent, Block.id)
                place_sound.play()  # Play sound when placing a block

        if key == 'right mouse down' and mouse.hovered_entity:
            if isinstance(mouse.hovered_entity, Block):
                block = mouse.hovered_entity
                chunk = block.parent
                del chunk.blocks[(block.x, block.y, block.z)]
                destroy_sound.play()  # Play sound when destroying a block
                destroy(mouse.hovered_entity)
            if isinstance(mouse.hovered_entity, Tree):
                tree = mouse.hovered_entity
                del scene.trees[(tree.x, tree.y, tree.z)]
                destroy_sound.play()  # Play sound when destroying a tree
                destroy(tree)

        if key == "scroll up":
            Block.id += 1
            if len(block_textures) <= Block.id:
                Block.id = 0
            scroll_sound.play()  # Play sound when scrolling up

        if key == "scroll down":
            Block.id -= 1
            if Block.id < 0:
                Block.id = len(block_textures) - 1
            scroll_sound.play()  # Play sound when scrolling down

    def update(self):
        player_pos = self.player.position
        for chunk_pos, chunk in self.chunks.items():
            chunk_world_pos = Vec3(chunk_pos[0] * CHUNKSIZE, 0, chunk_pos[1] * CHUNKSIZE)
            d = distance(player_pos, chunk_world_pos)
            if d < DETAIL_DISTANCE and chunk.is_simplify:
                chunk.detail_chunk()
            elif d >= DETAIL_DISTANCE and not chunk.is_simplify:
                chunk.simplify_chunk()
