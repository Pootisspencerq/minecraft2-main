import os
from ursina import load_texture

CHUNKSIZE = 4
WORLDSIZE = 10

DETAIL_DISTANCE = 20

BASE_DIR = os.getcwd()
IMG_DIR = os.path.join(BASE_DIR, 'assets/block_textures')

block_textures = []

file_list = os.listdir(IMG_DIR)
for image in file_list:
    texture  = load_texture('assets/block_textures' + os.sep + image)
    block_textures.append(texture)
