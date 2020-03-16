import base64
import json
import socket
import time
import websocket

# --------------------------------------------------
#    Magic
# --------------------------------------------------

gWS = None
gJSON_BUFFER = ''
gKEY_STATES = set()
gSETTINGS = {}

KEY_UP_ARROW = 38
KEY_RIGHT_ARROW = 39
KEY_DOWN_ARROW = 40
KEY_LEFT_ARROW = 37
KEY_SPACE = 32
KEY_W = 87
KEY_D = 68
KEY_S = 83
KEY_A = 65

def draw_text(tid, text, x, y, color='white', font='16px Arial'):
    _send_message({'cmd': 'draw_text', 'text': text, 'x': x, 'y': y, 'color': color, 'tid': tid, 'font': font})


def clear_text(tid, width, height):
    _send_message({'cmd': 'clear_text', 'tid': tid, 'width': width, 'height': height})


def _send_message(d):
    s = json.dumps(d)
    gWS.send(s)

def clear():
    gWS.send(json.dumps({'cmd': 'clear'}))

def flush():
    gWS.send(json.dumps({'cmd': 'flush'}))


def get_keystates():
    return gKEY_STATES


def init_baconworld_magic(baconworld_server):
    global gWS
    gWS = websocket.create_connection("ws://%s/websocket" % baconworld_server,
                                      sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))
    gWS.settimeout(0.05)
    _send_message({'cmd': 'set_target_mode', 'mode': 'client'})
    _send_message({'cmd': 'request_settings'})

    while len(gSETTINGS) == 0:
        process_bacon_messages()
    return (gSETTINGS['tile_width'], gSETTINGS['tile_height'], gSETTINGS['world_width'], gSETTINGS['world_height'])

    
def set_image(plane, key, filename):
    with open (filename, 'rb') as f:
        _send_message({'cmd': 'set_image', 'plane': plane, 'key': key,
                       'data': 'data:image/png;base64,' + base64.b64encode(f.read())})


def set_image_solid_color(plane, key, color):
    _send_message({'cmd': 'set_image_solid_color', 'plane': plane, 'key': key, 'color': color})


def update_object(x, y, plane, newval):
        _send_message({'cmd': 'update_object', 'plane': plane, 'x': x, 'y': y, 'newval': newval})

def process_bacon_messages():
    global gJSON_BUFFER
    global gSETTINGS
    
    # try to get new data
    try:
        gJSON_BUFFER = gJSON_BUFFER + gWS.recv()
    except websocket._exceptions.WebSocketTimeoutException:
        return

    # process the messages        
    while True:
        # extract the message, exit if not enough data
        i = gJSON_BUFFER.find('{')
        if i < 0:
            break            
        json_length = int(gJSON_BUFFER[:i])
        if len(gJSON_BUFFER) < (i + json_length):
            break
        js = json.loads(gJSON_BUFFER[i:i + json_length])
        gJSON_BUFFER = gJSON_BUFFER[i + json_length:]

        # process the message
        if js['cmd'] == 'event_keydown':
            gKEY_STATES.add(js['keycode'])
        if js['cmd'] == 'event_keyup':
            gKEY_STATES.remove(js['keycode'])
        if js['cmd'] == 'settings':
            gSETTINGS = js['settings']
