from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

def update():
    ppos = f'x = {round(player.x)}, y = {round(player.y)}, z = {round(player.z)}'
    player_pos_txt.text = str(ppos)

app = Ursina()
player = FirstPersonController(jump_height=2)
player_pos_txt = Text(text='' , scale = 0.7,)
player_pos_txt.position = (-0.87,0.485)
player_pos_txt.font = 'pix-pixelfjverdana12pt.regular.ttf'
e = Entity(model='plane', scale=30, collider='box',texture = 'white_cube',scale_y = 0.5,color = color.blue)

app.run()