from baconworld_magic import *

# --------------------------------------------------
#    Magic
# --------------------------------------------------


baconworld_server = 'http://linuxdev:8889'

# draw some grass
for y in range(0, 10):
    for x in range(0, 10):
        update_object(baconworld_server, x, y, 'ground', 'grass')
flush(baconworld_server)

# move a pig around
x = 50
y = 50
update_object(baconworld_server, x, y, 'animals', 'pig')
flush(baconworld_server)

while True:
    keys_down = get_keystates(baconworld_server)
    
    if KEY_D in keys_down:
        update_object(baconworld_server, x, y, 'animals', '')
        x = x + 1
        if x > 100:
            x = 0
        update_object(baconworld_server, x, y, 'animals', 'cow')
        flush(baconworld_server)
