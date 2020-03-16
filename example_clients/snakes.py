import time
from baconworld_magic import *
  
  
# initialize bacon world
(TILE_WIDTH, TILE_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT) = init_baconworld_magic('linuxdev:8889')
clear()

# load image for animals / pig
# could also load things like ground / grass
set_image_solid_color('ground', 'floor', 'darkgrey')
set_image_solid_color('ground', 'wall', 'red')
set_image_solid_color('animals', 'snake', 'green')

# draw the walls
for x in range(0, WORLD_WIDTH):
    update_object(x, 0, 'ground', 'wall')
    update_object(x, WORLD_HEIGHT - 1, 'ground', 'wall')
for y in range(0, WORLD_HEIGHT):
    update_object(0, y, 'ground', 'wall')
    update_object(WORLD_WIDTH-1, y, 'ground', 'wall')

for x in range(1, WORLD_WIDTH - 1):
    for y in range(1, WORLD_HEIGHT - 1):
        update_object(x, y, 'ground', 'floor')
flush()
time.sleep(0.5)

# wait for game to start
draw_text('TEXT1', 'SNAKE!', 14, 2, font='64px Arial', color='white')
flush()

draw_text('TEXT2', 'PRESS SPACEBAR TO START', 14, 10, font='32px Arial', color='white')
flush()

while KEY_SPACE not in get_keystates():
    process_bacon_messages()
print 'DONE'

clear_text('TEXT1', 10, 2)
clear_text('TEXT2', 20, 2)

# start the snake
direction = 0
x = WORLD_WIDTH / 2
y = WORLD_HEIGHT / 2
#world_map = [[''] * WORLD_WIDTH for _ in range(0, WORLD_HEIGHT)]
while True:
    # process bacon events
    process_bacon_messages()

    if KEY_LEFT_ARROW in get_keystates():
        direction = direction - 1
        if direction < 0:
            direction = 3
    if KEY_RIGHT_ARROW in get_keystates():
        direction = direction + 1
        if direction > 3:
            direction = 0
    
    
    if direction == 0:
        y = y - 1
    if direction == 1:
        x = x + 1
    if direction == 2:
        y = y + 1
    if direction == 3:
        x = x - 1
            
    update_object(x, y, 'animals', 'snake')
    flush()
#     
#     
#         
# 
#     # do some action based on keys    
#     if KEY_RIGHT_ARROW in get_keystates():
#         # erase the old pig
#         update_object(x, y, 'animals', '')
#         # update the location
#         x = x + 1
#         if x > 50:
#             x = 0
#         # draw the new pig
#         update_object(x, y, 'animals', 'pig')
#         flush()
    
    # delay or else the pig is too fast
    time.sleep(0.05)
