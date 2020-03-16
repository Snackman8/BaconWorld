import time
from baconworld_magic import *
  
  
# initialize bacon world
init_baconworld_magic('linuxdev:8889')
clear()

# load image for animals / pig
# could also load things like ground / grass
set_image_solid_color('ground', 'grass', 'yellow')
set_image('animals', 'pig', 'pig.png')

# --------------------------------------------------
# TITLE SCREEN
# --------------------------------------------------
# wait for game to start
draw_text('TEXT1', 'THIS IS BACON WORLD!', 14, 2, font='64px Arial', color='white')
draw_text('TEXT2', 'PRESS SPACEBAR TO START', 14, 10, font='32px Arial', color='white')
flush()
while KEY_SPACE not in get_keystates():
    process_bacon_messages()
clear_text('TEXT1', 10, 2)
clear_text('TEXT2', 20, 2)


# --------------------------------------------------
# BEGIN GAME
# --------------------------------------------------
   
# draw some grass
for y in range(0, 10):
    for x in range(0, 10):
        update_object(x*2, y*2, 'ground', 'grass')

# flush the updates to the browser
flush()

# draw the initial pig
x = 30
y = 16
update_object(x, y, 'animals', 'pig')
flush()

# loop
while True:
    # process bacon events
    process_bacon_messages()

    # do some action based on keys    
    if KEY_RIGHT_ARROW in get_keystates():
        # erase the old pig
        update_object(x, y, 'animals', '')
        # update the location
        x = x + 1
        if x > 50:
            x = 0
        # draw the new pig
        update_object(x, y, 'animals', 'pig')
        flush()
    
    # delay or else the pig is too fast
    time.sleep(0.01)
