# --------------------------------------------------
# Imports
# --------------------------------------------------
import argparse
import base64
from collections import OrderedDict
import io
import json
import time
import tornado.ioloop
import tornado.web
import tornado.websocket
from PIL import Image


# --------------------------------------------------
# Constants
# --------------------------------------------------
PLANE_NAMES = ['ground', 'animals']
TILE_WIDTH = 16
TILE_HEIGHT = 16
WORLD_HEIGHT = 50
WORLD_WIDTH = 110


# --------------------------------------------------
# Globals
# --------------------------------------------------
gPLANES = OrderedDict()
gIMAGE_STRS = OrderedDict()
gKEY_STATES = set()
gRENDERQUEUE = OrderedDict()
gTEXT = OrderedDict()


# --------------------------------------------------
# Functions
# --------------------------------------------------
def clear():
    for y in range(0, WORLD_HEIGHT):
        for x in range(0, WORLD_WIDTH):
            for p in PLANE_NAMES:
                gPLANES[p][y][x] = ''
    refresh()


def img_to_str(img):
    with io.BytesIO() as output:
        img.save(output, format="PNG")
        return 'data:image/png;base64,' + base64.b64encode(output.getvalue())


def init_globals():
    for p in PLANE_NAMES:
        gPLANES[p] = [[''] * WORLD_WIDTH for _ in range(0, WORLD_HEIGHT)]
        gIMAGE_STRS[p] = OrderedDict()
    
    gIMAGE_STRS['ground'][''] = img_to_str(Image.new('RGB', (TILE_WIDTH, TILE_HEIGHT), color = 'black'))
    gIMAGE_STRS['ground']['grass'] = img_to_str(Image.new('RGB', (TILE_WIDTH, TILE_HEIGHT), color = 'green'))
    gIMAGE_STRS['animals']['pig'] = img_to_str(Image.new('RGB', (TILE_WIDTH, TILE_HEIGHT), color = 'pink'))
    gIMAGE_STRS['animals']['cow'] = img_to_str(Image.new('RGB', (TILE_WIDTH, TILE_HEIGHT), color = 'orange'))
    clear()


def refresh(x1=0, y1=0, x2=WORLD_WIDTH, y2=WORLD_HEIGHT, refresh_text=True):
#    send_update_message()
    gRENDERQUEUE.clear()
    for y in range(y1, y2):
        for x in range(x1, x2):
            update_render_queue(x, y)
    send_update_message()
    if refresh_text:
        # this is a really bad hack!
        time.sleep(0.1)
        for k in gTEXT:
            WSHandler.send_message(gTEXT[k])


def send_update_message():    
    WSHandler.send_message({'cmd': 'update_render', 'target': 'browser', 'data': gRENDERQUEUE})
    gRENDERQUEUE.clear()


def update_render_queue(x, y):
    # search for the first image that works
    for p in PLANE_NAMES[::-1]:
        if gPLANES[p][y][x] in gIMAGE_STRS[p]:
            img_str = gIMAGE_STRS[p][gPLANES[p][y][x]]
            gRENDERQUEUE.setdefault(img_str, []).append((x * TILE_WIDTH, y * TILE_HEIGHT))
            return


# --------------------------------------------------
# Tornado Handlers
# --------------------------------------------------
class MainHandler(tornado.web.RequestHandler):
    def get(self, matched):
        # process based on matched portion of url
        if matched == '':
            # main index page handler
            with open ('www/index.html', 'r') as f:
                s = f.read().replace('$$HOST$$', self.request.host)
                s = s.replace('$$CANVAS_HEIGHT$$', str(WORLD_HEIGHT * TILE_HEIGHT))
                s = s.replace('$$CANVAS_WIDTH$$', str(WORLD_WIDTH * TILE_WIDTH))
                self.write(s)
        else:
            raise tornado.web.HTTPError(404)


class WSHandler(tornado.websocket.WebSocketHandler):
    # class variable to keep track of all active websockets
    live_websockets = set()
    
    def open(self):
        # called when web socket opens
        self.set_nodelay(True)
        self.live_websockets.add(self)

    def on_message(self, message):
        js = json.loads(message)
        if js['cmd'] == 'set_target_mode':
            self.target_mode = js['mode']
        if js['cmd'] == 'event_keydown':
            if js['keycode'] not in gKEY_STATES:
                gKEY_STATES.add(js['keycode'])
                js['target'] = 'client'
                WSHandler.send_message(js)
        if js['cmd'] == 'event_keyup':
            gKEY_STATES.remove(js['keycode'])
            js['target'] = 'client'
            WSHandler.send_message(js)
        if js['cmd'] == 'clear':
            clear()
        if js['cmd'] == 'draw_text':
            js['target'] = 'browser'
            js['x'] = js['x'] * TILE_WIDTH
            js['y'] = js['y'] * TILE_HEIGHT
            gTEXT[js['tid']] = js
            WSHandler.send_message(js)
        if js['cmd'] == 'clear_text':
            if js['tid'] in gTEXT:
                txt = gTEXT[js['tid']]
                del gTEXT[js['tid']]
                x = txt['x'] / TILE_WIDTH
                y = txt['y'] / TILE_HEIGHT
                refresh(x, y, x + js['width'], y + js['height'], refresh_text=False)
        if js['cmd'] == 'flush':
            send_update_message()
        if js['cmd'] == 'refresh':
            refresh()
        if js['cmd'] == 'set_image':
            gIMAGE_STRS[js['plane']][js['key']] = js['data']
        if js['cmd'] == 'update_object':
            if js['x'] >=0 and js['x'] < WORLD_WIDTH and js['y'] >= 0 and js['y'] < WORLD_HEIGHT:
                gPLANES[js['plane']][js['y']][js['x']] = js['newval']
                update_render_queue(js['x'], js['y'])
    
    @classmethod
    def send_message(cls, d):
        js = json.dumps(d)
        for ws in list(cls.live_websockets):
            if not ws.ws_connection or not ws.ws_connection.stream.socket:
                cls.live_websockets.remove(ws)
            else:
                if d['target'] == ws.target_mode:
                    ws.write_message(str(len(js)) + js)


# --------------------------------------------------
# Tornado App
# --------------------------------------------------
def make_app():
    init_globals()
    return tornado.web.Application([
        (r"/websocket", WSHandler),
        (r"/(.*)", MainHandler),
    ])


if __name__ == "__main__":
    parser =argparse.ArgumentParser(description='Baconworld Server')
    parser.add_argument('--port', default=8889, help='Port to run the server on')
    parser.add_argument('--tile_height', type=int, default=TILE_HEIGHT, help='Height of a tile')
    parser.add_argument('--tile_width', type=int, default=TILE_WIDTH, help='Width of a tile')
    parser.add_argument('--world_height', type=int, default=WORLD_HEIGHT, help='Height of the world in tiles')
    parser.add_argument('--world_width', type=int, default=WORLD_WIDTH, help='Width of the world in tiles')
    args = parser.parse_args()
    TILE_WIDTH = args.tile_width
    TILE_HEIGHT = args.tile_height
    WORLD_WIDTH = args.world_width
    WORLD_HEIGHT = args.world_height

    print 'Starting Bacon World Server on port %d with tile size of %dx%d and world size of %dx%d' % (args.port, TILE_WIDTH, TILE_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)    
    app = make_app()
    app.listen(args.port)
    tornado.ioloop.IOLoop.current().start()
