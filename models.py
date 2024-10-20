from ursina import *
from settings import *
from ursina.shaders import basic_lighting_shader
from perlin_noise import PerlinNoise
import pickle
from random import randint

# Background music and sound effects
background_music = Audio('background_music.mp3', volume=1.5, loop=True, autoplay=True)
destroy_sound = Audio('metalbox-break3.mp3', autoplay=False)
place_sound = Audio('clash-royale-hog-rider.mp3', autoplay=False)
scroll_sound = Audio('scroll_sound.mp3', autoplay=False)
save_sound = Audio('save_game.mp3', autoplay=False)
load_sound = Audio('load_game.mp3', autoplay=False)

scene.trees = {}

class Tree(Entity):
    def __init__(self, pos, **kwargs):
        super().__init__(
            parent=scene,
            model='assets\\minecraft_tree\\scene',
            scale=clamp(randint(3, 5), 3, 5),  
            collider='box',
            position=pos,
            shader=basic_lighting_shader,
            origin_y=0.6,
            **kwargs) 
        scene.trees[(self.x, self.y, self.z)] = self  

class Block(Button):
    id = 3  
    def __init__(self, pos, parent_world, block_id=3, **kwargs):
        super().__init__(
            parent=parent_world,
            model='cube',
            texture=block_textures[block_id],  
            scale=1,
            collider='box',
            position=pos,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            highlight_color=color.gray,
            shader=basic_lighting_shader,
            origin_y=-0.5,
            **kwargs)   
        parent_world.blocks[(self.x, self.y, self.z)] = self  
        self.id = block_id 

class Chunk(Entity):
    def __init__(self, chunk_pos, **kwargs):
        super().__init__(model=None, collider=None, shader=basic_lighting_shader, **kwargs)
        self.chunk_pos = chunk_pos
        self.blocks = {}  
        self.noise = PerlinNoise(octaves=2, seed=3504)
        self.is_simplify = False  
        self.default_texture = 3  
        

    def simplify_chunk(self):
        """Simplify the chunk for performance optimization."""
        if self.is_simplify:
            return
        
        self.model = self.combine()  
        self.collider = 'mesh'
        self.texture = block_textures[self.default_texture]

        for block in self.blocks.values():
            destroy(block)

        self.is_simplify = True  

    def detail_chunk(self):
        """Revert the chunk to detailed blocks when the player is nearby."""
        if not self.is_simplify:
            return

        self.model = None  
        self.collider = None
        self.texture = None

        
        for pos, block in self.blocks.items():
            Block(pos, self, block_id=block.id)
        
        self.is_simplify = False  

    def generate_chunk(self):
        """Generate blocks in the chunk using Perlin noise."""
        cx, cz = self.chunk_pos
        for x in range(CHUNKSIZE):
            for z in range(CHUNKSIZE):
                block_x = cx * CHUNKSIZE + x
                block_z = cz * CHUNKSIZE + z
                y = floor(self.noise([block_x / 24, block_z / 24]) * 6)
                block = Block((block_x, y, block_z), self)

                
                if randint(0, 200) == 52:
                    Tree((block_x, y + 1, block_z))

class WorldEdit(Entity):
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.chunks = {}  
        self.current_chunk = None
        self.player = player
        self.held_block = Entity(model='cube', scale=(0.2, 0.2, 0.2), parent=camera.ui, rotation = Vec3(3, -32, 3),
                                position=(0.6, -0.4), texture=block_textures[Block.id], shader=basic_lighting_shader)
        
        
    def generate_world(self):
        """Generate the entire world."""
        def generate_world(self):
            self.clear_world()
            for x in range (WORLDSIZE):
                for z in range (WORLDSIZE):
                    chunk_pos = (x,z)
                    if chunk_pos not in self.chunks:
                        chunk = Chunk(chunk_pos)
                    chunk.generate_chunk()
                    self.chunks [chunk_pos] = chunk
            self.menu.toggle_menu()
                    
    def save_game(self):
        """Save the current game state to a file."""
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
        save_sound.play()  
        self.menu.toggle_menu()  

    def clear_world(self):
        """Clear all blocks and trees from the world."""
        for chunk in self.chunks.values():
            for block in chunk.blocks.values():
                destroy(block)
            destroy(chunk)
        for tree in scene.trees.values():
            destroy(tree)
        scene.trees.clear()
        self.chunks.clear()

    def load_world(self, chunk_data, tree_data):
        """Load the chunks and trees from saved game data."""
        for chunk_pos, blocks in chunk_data:
            chunk = Chunk(chunk_pos)
            for block_pos, block_id in blocks:
                Block(block_pos, chunk, block_id)
            self.chunks[chunk_pos] = chunk

        for tree_pos, tree_scale in tree_data:
            tree = Tree(tree_pos)
            tree.scale = tree_scale

    def load_game(self):
        """Load a previously saved game."""
        with open('save.dat', 'rb') as file:
            game_data = pickle.load(file)
        self.clear_world()  # Clear the current world
        self.player.x, self.player.y, self.player.z = game_data["player_pos"]
        self.load_world(game_data["chunks"], game_data['trees'])
        load_sound.play()  # Play load sound when the game is loaded
        print("Game loaded.")
        self.menu.toggle_menu()

    def input(self, key):
        if key == "escape":
            self.menu.toggle_menu()
        if key == 'k':
            self.save_game()
        if key == 'l':
            self.load_game()

        if key == 'left mouse down':
            hit_info = raycast(camera.world_position, camera.forward, distance=10)
            if hit_info.hit:
                block = Block(hit_info.entity.position + hit_info.normal, hit_info.entity.parent, Block.id)
                place_sound.play()

        if key == 'right mouse down' and mouse.hovered_entity:
            if isinstance(mouse.hovered_entity, Block):
                block = mouse.hovered_entity
                chunk = block.parent
                del chunk.blocks[(block.x, block.y, block.z)]
                destroy_sound.play()
                destroy(mouse.hovered_entity)
            if isinstance(mouse.hovered_entity, Tree):
                tree = mouse.hovered_entity
                del scene.trees[(tree.x, tree.y, tree.z)]
                destroy_sound.play()
                destroy(tree)

        if key == "scroll up":
            Block.id += 1
            if len(block_textures) <= Block.id:
                Block.id = 0
            scroll_sound.play()
            self.held_block.texture = block_textures[Block.id]
            
        if key == "scroll down":
            Block.id -= 1
            if Block.id < 0:
                Block.id = len(block_textures) - 1
            scroll_sound.play()
            self.held_block.texture = block_textures[Block.id]
            
    def update(self):
        """Update the chunks based on player proximity."""
        if self.player.y < -30:
            self.generate_world()
            self.player.position = (0,0,0)
            self.player.y = 30
        player_pos = self.player.position
        for chunk_pos, chunk in self.chunks.items():
            chunk_world_pos = Vec3(chunk_pos[0] * CHUNKSIZE, 0, chunk_pos[1] * CHUNKSIZE)
            d = distance(player_pos, chunk_world_pos)
            if d < DETAIL_DISTANCE and chunk.is_simplify:
                chunk.detail_chunk()
            elif d >= DETAIL_DISTANCE and not chunk.is_simplify:
                chunk.simplify_chunk()
