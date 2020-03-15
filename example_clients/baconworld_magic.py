import base64
import requests

# --------------------------------------------------
#    Magic
# --------------------------------------------------
def update_object(baconworld_server, x, y, plane, newval):
    requests.get(baconworld_server + '/update', {'x': x, 'y': y, 'plane': plane, 'newval': newval})

def flush(baconworld_server):
    requests.get(baconworld_server + '/flush')

def get_keystates(baconworld_server):
    r = requests.get(baconworld_server + '/keystates')
    if r.text.strip() == '':
        keystates = []
    else:
        keystates = r.text.strip().split(' ')
        keystates = [int(x) for x in keystates]
    return keystates
    
def set_image(baconworld_server, plane, key, filename):
    # load the image
    f = open(filename, 'rb')
    s = f.read()
    f.close()
    
    # convert to base64
    s = 'data:image/png;base64,' + base64.b64encode(s)
    
    # send to baconworld_server
    requests.get(baconworld_server + '/set_image', {'plane': plane, 'key': key, 'data': s})

KEY_UP_ARROW = 38
KEY_RIGHT_ARROW = 39
KEY_DOWN_ARROW = 40
KEY_LEFT_ARROW = 37
KEY_W = 87
KEY_D = 68
KEY_S = 83
KEY_A = 65
