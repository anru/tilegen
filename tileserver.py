#!/usr/bin/python

import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')

from hashlib import md5

from PIL import Image, ImageDraw, ImageFont

from flask import Flask, request, make_response
app = Flask(__name__)
app.config.from_pyfile(os.environ.get('TILE_CONF', 'settings.py'))

@app.route("/")
def hello():
    return "<h2>Simple tile server what replay given request text on tiles</h2>"

@app.route("/tile")
def tile():
    w = int(request.args.get('w', 256))
    h = int(request.args.get('h', 256))
    text = request.args.get('t', 'T-X')
    
    hash_key = md5('_'.join( (unicode(a) for a in [w, h, text]) )).hexdigest()
    
    cache_dir = app.config['CACHE_DIR']
    if not os.path.isabs(cache_dir):
        cache_dir = os.path.join(app.config.root_path, cache_dir)
    
    tile_path = os.path.join(cache_dir, hash_key + '.png')
    
    if not os.path.exists(tile_path) or app.config['DEBUG']:
    
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # load font
        font = ImageFont.truetype("FreeSans.ttf", 24)        
        #font = ImageFont.load_default()
        textsize = font.getsize(text)
        
        tx = (w - textsize[0])/2
        ty = (h - textsize[1])/2
        
        draw.rectangle( [1, 1, img.size[0] -1, img.size[1] -1], fill=(0,0,0,0), outline='red')
        draw.text( (tx, ty), text, font=font, fill=app.config['TEXT_COLOR'])
        img.save(tile_path, 'PNG')
    
    f = open(tile_path, 'r')
    image_data = f.read()
    f.close()
    
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    return response
    

if __name__ == "__main__":
    app.run()
