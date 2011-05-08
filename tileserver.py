#!/usr/bin/python

import os, sys
import re
reload(sys)
sys.setdefaultencoding('utf-8')

from hashlib import md5
from time import sleep

from PIL import Image, ImageDraw, ImageFont

from flask import Flask, request, make_response, Response
app = Flask(__name__)
app.config.from_pyfile(os.environ.get('TILE_CONF', 'settings.py'))

@app.route("/")
def hello():
    return "<h2>Simple tile server what replay given request text on tiles</h2>"

r_color_split = re.compile(r'\s*,\s*')

def parse_color(c):
    if c.startswith('('):
        v = r_color_split.split(c[1:-1])
        if v:
            return tuple( (int(k) for k in v) )
        return 'white'
    return c

def get_tiles_dir():
    tiles_dir = app.config['TILES_DIR']
    if not os.path.isabs(tiles_dir):
        tiles_dir = os.path.join(app.config.root_path, tiles_dir)
    return tiles_dir

@app.route("/tile")
def tile():
    w = int(request.args.get('w', app.config['TILE_WIDTH']))
    h = int(request.args.get('h', app.config['TILE_HEIGHT']))
    text = request.args.get('t', 'T-X')
    text_repeat = request.args.get('tr', app.config['TEXT_REPEAT'])
    bg_color = parse_color(request.args.get('bg', app.config['BG_COLOR']))
    font_size = int(request.args.get('fs', app.config['FONT_SIZE']))
    tx_color = parse_color(request.args.get('c', app.config['TEXT_COLOR']))
    outline_color = parse_color(request.args.get('b', app.config['OUTLINE_COLOR']))
    
    timeout = request.args.get('tm')

    hash_key = md5('_'.join( (unicode(a) for a in [w, h, text, bg_color, font_size, \
                                                    tx_color, outline_color, text_repeat, \
                                                    app.config['TX_PADDING'], app.config['WORD_SPACING'], app.config['LINE_SPACING']]) )).hexdigest()
    
    if not timeout and hash_key == request.headers.get('If-None-Match'):
        return Response(status=304)
    
    tile_path = os.path.join(get_tiles_dir(), hash_key + '.png')
    
    generated = False
    
    if not os.path.exists(tile_path) or request.args.get('d'):
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        draw.rectangle( [1, 1, img.size[0] -1, img.size[1] -1], fill=bg_color, outline=outline_color)
        
        # load font
        font = ImageFont.truetype("FreeSans.ttf", font_size)
        #font = ImageFont.load_default()
        textsize = font.getsize(text)
        
        if text_repeat == 'none':
            tx = (w - textsize[0])/2
            ty = (h - textsize[1])/2
            draw.text( (tx, ty), text, font=font, fill=tx_color)
        elif text_repeat == 'repeat':
            padding = app.config['TX_PADDING']
            word_spacing = app.config['WORD_SPACING']
            line_spacing = app.config['LINE_SPACING']
            wc = max((w - padding) / (textsize[0] + word_spacing) + 1, 1)
            hc = max((h - padding) / (textsize[1] + line_spacing), 1)

            xmargin = abs((w - ((textsize[0] + word_spacing)*wc - word_spacing))/2)
            ymargin = abs((h - ((textsize[1] + line_spacing)*hc - line_spacing))/2)
            
            for i in xrange(0, wc):
                tx = xmargin + i*(textsize[0] + word_spacing)
                for j in xrange(0, hc):
                    ty = ymargin + j*(textsize[1] + line_spacing)
                    draw.text( (tx, ty), text, font=font, fill=tx_color)
            
        del draw
        img.save(tile_path, 'PNG')
        generated = True
    
    if timeout:
        sleep(float(timeout))

    f = open(tile_path, 'r')
    image_data = f.read()
    f.close()
    
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    response.headers['ETag'] = hash_key
    response.headers['X-Tile-Generated'] = 'Yes' if generated else 'No'
    return response
    

if __name__ == "__main__":
    if not os.path.exists(get_tiles_dir()):
        os.mkdir(get_tiles_dir())
    app.run()
