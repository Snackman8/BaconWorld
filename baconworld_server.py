# --------------------------------------------------
# Imports
# --------------------------------------------------
import base64
from collections import OrderedDict
import io
import tornado.ioloop
import tornado.web
import tornado.websocket
from PIL import Image


# --------------------------------------------------
# Constants
# --------------------------------------------------
WORLD_WIDTH = 120
WORLD_HEIGHT = 60
PLANE_NAMES = ['ground', 'animals']


# --------------------------------------------------
# Globals
# --------------------------------------------------
gPLANES = OrderedDict()
gIMAGE_STRS = OrderedDict()
gRENDERQUEUE = OrderedDict()
gKEYSTATES = set()

# --------------------------------------------------
# Functions
# --------------------------------------------------
def clear():
    global gPLANES
    
    for y in range(0, WORLD_HEIGHT):
        for x in range(0, WORLD_WIDTH):
            for p in PLANE_NAMES:
                gPLANES[p][y][x] = ''
    
    refresh()
#             gPLAN
#             
#             update_render_queue(x, y, 'ground', 'grass')
#     send_update_message()

def handle_keydown(keycode):
    global gKEYSTATES
    gKEYSTATES.add(keycode)

def handle_keyup(keycode):
    global gKEYSTATES
    gKEYSTATES.remove(keycode)


def img_to_str(img):
    with io.BytesIO() as output:
        img.save(output, format="PNG")
        return 'data:image/png;base64,' + base64.b64encode(output.getvalue())


def init_globals():
    global gPLANES
    global gIMAGE_STRS    
    for p in PLANE_NAMES:
        gPLANES[p] = [[''] * WORLD_WIDTH for _ in range(0, WORLD_HEIGHT)]
        gIMAGE_STRS[p] = OrderedDict()
    
    gIMAGE_STRS['ground'][''] = img_to_str(Image.new('RGB', (16, 16), color = 'black'))
    gIMAGE_STRS['ground']['grass'] = img_to_str(Image.new('RGB', (16, 16), color = 'green'))
    gIMAGE_STRS['animals']['pig'] = img_to_str(Image.new('RGB', (16, 16), color = 'pink'))
    gIMAGE_STRS['animals']['cow'] = img_to_str(Image.new('RGB', (16, 16), color = 'orange'))
    clear()


def refresh():
#    send_update_message()
    global gRENDERQUEUE
    gRENDERQUEUE = {}
    for y in range(0, WORLD_HEIGHT):
        for x in range(0, WORLD_WIDTH):
            update_render_queue(x, y)
#             sent = False
#             for p in PLANE_NAMES[::-1]:
#                 if gPLANES[p][y][x] != '':
#                     update_render_queue(x, y, p, gPLANES[p][y][x])
#                     sent = True
#             if not sent:
#                 update_render_queue(x, y, p, 'grass')
    send_update_message()


def send_update_message():
    global gRENDERQUEUE
    EchoWebSocket.send_message(gRENDERQUEUE)
    gRENDERQUEUE = {}


def update_render_queue(x, y):
    global gRENDERQUEUE
    if x >=0 and x < WORLD_WIDTH and y >= 0 and y < WORLD_HEIGHT:
        # search for the first image that works
        for p in PLANE_NAMES[::-1]:
            if gPLANES[p][y][x] in gIMAGE_STRS[p]:
                img_str = gIMAGE_STRS[p][gPLANES[p][y][x]]
                if img_str not in  gRENDERQUEUE:
                    gRENDERQUEUE[img_str] = []
                gRENDERQUEUE[img_str].append((x * 16, y * 16))
                return


# --------------------------------------------------
# Handlers
# --------------------------------------------------
class EchoWebSocket(tornado.websocket.WebSocketHandler):
    live_websockets = set()
    
    def open(self):
        self.set_nodelay(True)
        self.live_websockets.add(self)

    def on_message(self, message):
        if message == 'refresh':
            refresh()
        if message.startswith('keyup '):
            print 'KEYUP!'
            handle_keyup(message.partition(' ')[2])
        if message.startswith('keydown '):
            handle_keydown(message.partition(' ')[2])

    def on_close(self):
        print("WebSocket closed")
    
    @classmethod
    def send_message(cls, message):
        removable = set()
        for ws in cls.live_websockets:
            if not ws.ws_connection or not ws.ws_connection.stream.socket:
                removable.add(ws)
            else:
                ws.write_message(message)
        for ws in removable:
            cls.live_websockets.remove(ws)        


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        f = open('www/index.html', 'r')
        s = f.read()
        f.close()
        self.write(s)


class UpdateHandler(tornado.web.RequestHandler):
    def get(self):
        x = int(self.get_argument('x'))
        y = int(self.get_argument('y'))
        if x >=0 and x < WORLD_WIDTH and y >= 0 and y < WORLD_HEIGHT:
            plane = self.get_argument('plane')
            newval = self.get_argument('newval')
            gPLANES[plane][y][x] = newval
            update_render_queue(x, y)

class SetImageHandler(tornado.web.RequestHandler):
    def get(self):
        global gIMAGE_STRS
        plane = self.get_argument('plane')
        key = self.get_argument('key')
        data = self.get_argument('data')
        gIMAGE_STRS[plane][key] = data

class KeystatesHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(' '.join(list(gKEYSTATES)))

class FlushHandler(tornado.web.RequestHandler):
    def get(self):
        send_update_message()

class ClearHandler(tornado.web.RequestHandler):
    def get(self):
        clear()


def make_app():
    init_globals()
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/update", UpdateHandler),
        (r"/flush", FlushHandler),
        (r"/clear", ClearHandler),
        (r"/keystates", KeystatesHandler),
        (r"/set_image", SetImageHandler),
        (r"/websocket", EchoWebSocket),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8889)
    tornado.ioloop.IOLoop.current().start()
