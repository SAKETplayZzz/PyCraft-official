
from random import randrange
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor,abs,sin,cos,radians
import time
from perlin_noise import PerlinNoise  
from nMap import nMap
from cave_system import Caves
from mining_system import Mining_system

app = Ursina()

coal_oar_texture = load_texture('assets/coal_block.png')
log_texture = load_texture('assets/log_texture.png')
stone_texture = load_texture('assets/stone_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')
sky_texture = load_texture('assets/skybox.png')
arm_texture = load_texture('assets/arm_texture.png')
leaf_texture = load_texture('assets/leaf_block.png')
sand_texture = load_texture('assets/sand_block.png')
glass_texture = load_texture('assets/glass_block.png')

# Our main character.
player = FirstPersonController()
player.cursor.visible = False
player.gravity = 0
grav_speed = 0
grav_acc = 0.1
player.x = player.z = 5
player.y = 32
prevZ = player.z
prevX = player.x
origin = player.position # Vec3 object? .x .y .z

# Load in textures and models.
monoTex = 'stroke_mono.png'
cubeTex = 'grasstexture.png'
cubeModel = 'moonCube'

# Important variables (e.g. for terrain generation).
noise = PerlinNoise(octaves=1,seed=int(randrange(99,111)))
seedMouth = Text(   text='<white><bold>Your seed, today, sir, is ' +
                    str(noise.seed),background=True)
seedMouth.background.color = color.orange
seedMouth.scale *= 1.4
seedMouth.x = -0.52
seedMouth.y = 0.4
seedMouth.appear(speed=0.15)

# print('seed is ' + str(noise.seed))

megasets = []
subsets = []
subCubes = []
# New variables :)
generating = 1 # -1 if off.
canGenerate = 1 # -1 if off.
genSpeed = 0
perCycle = 64
currentCube = 0
currentSubset = 0
numSubCubes = 64
numSubsets = 420 # I.e. how many combined into a megaset?
theta = 0
rad = 0
# Dictionary for recording whether terrain blocks exist
# at location specified in key.
subDic = {}

# Instantiate our empty subsets.
for i in range(numSubsets):
    bud = Entity(model=cubeModel)
    bud.texture = cubeTex
    bud.disable()
    subsets.append(bud)

anush = Caves()
varch = Mining_system(player, camera, subsets)

window.color = color.rgb(0,200,211)
window.exit_button.visible = False

prevTime = time.time()

scene.fog_color = color.rgb(0,222,0)
scene.fog_density = 0.02


def input(key):
    global generating, canGenerate
    varch.input(key)
    if varch.buildMode == 1:
        generating = -1
        canGenerate = -1

    if key == 'q' or key == 'escape':
        quit()
    if key == 'g':
        generating *= -1
        canGenerate *= -1

def update():
    global prevZ, prevX, prevTime, genSpeed, perCycle
    global rad, origin, generating, canGenerate
    if  abs(player.z - prevZ) > 1 or \
        abs(player.x - prevX) > 1:
            origin=player.position
            rad=0
            theta=0
            generating = 1 * canGenerate
            prevZ = player.z
            prevX = player.x


    generateShell()

    if time.time() - prevTime > genSpeed:
        for i in range(perCycle):
            genTerrain()
        prevTime = time.time()
    varch.buildTool()



# Instantiate our 'ghost' subset cubes.
for i in range(numSubCubes):
    bud = Entity(model=cubeModel,texture=cubeTex)
    bud.scale *= 0.99999
    bud.rotation_y = random.randint(1,4)*90
    bud.disable()
    subCubes.append(bud)



def genPerlin(_x, _z, plantTree=False):
    y = 0
    freq = 64
    amp = 42      
    y += ((noise([_x/freq,_z/freq]))*amp)
    freq = 32
    amp = 21
    y += ((noise([_x/freq,_z/freq]))*amp)

    # Is there are cave-gap here?
    # If so, lower the cube by 32...or something ;)
    whatCaveHeight = anush.checkCave(_x, _z)
    if whatCaveHeight != None:
        y = whatCaveHeight

    return floor(y)

def genTerrain():
    global currentCube, theta, rad, currentSubset
    global generating

    if generating==-1: return

    # Decide where to place new terrain cube!
    x = floor(origin.x + sin(radians(theta)) * rad)
    z = floor(origin.z + cos(radians(theta)) * rad)
    # Check whether there is terrain here already...
    if subDic.get('x'+str(x)+'z'+str(z))!='i':
        subCubes[currentCube].enable()
        subCubes[currentCube].x = x
        subCubes[currentCube].z = z
        subCubes[currentCube].parent = subsets[currentSubset]
        y = subCubes[currentCube].y = genPerlin(x,z,True)
        # Record position of this terrain in both
        # the subDic and the mining system's dictionary.
        subDic['x'+str(x)+'z'+str(z)] = 'i'
        varch.tDic['x'+str(x)+'y'+str(y)+'z'+str(z)]=y
        # OK -- time to decide colours :D
        c = nMap(y,-8,21,132,212)
        c += random.randint(-32,32)
        subCubes[currentCube].color = color.rgb(c,c,c)
        subCubes[currentCube].disable()
        currentCube+=1

        # Ready to build a subset?
        if currentCube==numSubCubes:
            subsets[currentSubset].combine(auto_destroy=False)
            subsets[currentSubset].enable()
            currentSubset+=1
            currentCube=0
            
            # And ready to build a megaset?
            if currentSubset==numSubsets:
                currentSubset=0
                print('Hey -- is everything working?')
                print('*** Check the megaset stuff! :)')
                """
                megasets.append(Entity( model=cubeModel,
                                        texture=cubeTex))
                # Parent all subsets to our new megaset.
                for s in subsets:
                    s.parent=megasets[-1]
                # In case user has Ursina version 3.6.0.
                # safe_combine(megasets[-1],auto_destroy=False)
                megasets[-1].combine(auto_destroy=False)
                for s in subsets:
                    s.parent=scene
                currentSubset=0
                print('Megaset #' + str(len(megasets))+'!')
                """
    else:
        pass
        # There was terrain already there, so
        # continue rotation to find new terrain spot.
    
    if rad > 0:
        theta += 45/rad
    else: rad+=0.5
    
    if theta >= 360:
        theta = 0
        rad += 0.5


# Our new gravity system for moving the player :)
def generateShell():
    global player, grav_speed, grav_acc

    # New 'new' system :D
    # How high or low can we step/drop?
    step_height = 3
    subjectHeight = 2
    gravityON = True
    
    target_y = player.y

    for i in range(step_height,-step_height,-1):
        # What y is the terrain at this position?
        # terra = genPerlin(player.x,player.z)
        terra = varch.tDic.get( 'x'+str((floor(player.x+0.5)))+
                                'y'+str((floor(player.y+i)))+
                                'z'+str((floor(player.z+0.5))))
        # *** Tower algorithm -- to prevent being sucked up
        # beyond step-height -- bug is that it may force us
        # through the bottom of terrain.
        terraTop = varch.tDic.get( 'x'+str((floor(player.x+0.5)))+
                                'y'+str((floor(player.y+i+1)))+
                                'z'+str((floor(player.z+0.5))))
        if terra != None and terra != 'gap':
            gravityON = False
            if terraTop == None or terraTop == 'gap':
                # print('TERRAIN FOUND! ' + str(terra + 2))
                target_y = floor(player.y+i) + subjectHeight
                break
            
            # If here, then tower is too tall.
            # So, move player from this position.
            player.x -= 0.6
            player.z -= 0.6

    if gravityON==True:
        # This means we're falling!
        grav_speed += (grav_acc * time.dt)
        player.y -= grav_speed
    else:
        player.y = lerp(player.y, target_y, 9.807*time.dt)
        grav_speed = 0 # Reset gravity speed: gfloored.

generateShell()

app.run()

