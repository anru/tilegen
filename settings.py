DEBUG = True
TILES_DIR = 'tiles'

# rendering defaults for tiles
TEXT_COLOR = 'black'
FONT_SIZE = 24
BG_COLOR = 'white'
OUTLINE_COLOR = 'red'
TEXT_REPEAT = 'none'

# settings for TEXT_REPEAT = repeat
TX_PADDING = 5
WORD_SPACING = 10
LINE_SPACING = 14

try:
    from settings_local import *
except ImportError:
    pass
