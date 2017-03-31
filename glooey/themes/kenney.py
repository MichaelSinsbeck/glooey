#!/usr/bin/env python3

import glooey
import pyglet
import autoprop

# Import everything from glooey into this namespace.  We'll overwrite the 
# widgets we want to overwrite and everything else will be directly available.
from glooey import *

# Create a resource loader that knows where the assets for this theme are 
# stored.
from glooey.themes import ResourceLoader
assets = ResourceLoader('kenney')
assets.add_font('font/kenvector_future.ttf')
assets.add_font('font/kenvector_future_thin.ttf')

glooey.drawing.colors = {
        'light blue': glooey.Color.from_hex('#35baf3'),
        'blue': glooey.Color.from_hex('#1ea7e1'),
        'dark blue': glooey.Color.from_hex('#166e93'),

        'light red': glooey.Color.from_hex('#fa8132'),
        'red': glooey.Color.from_hex('#e86a17'),
        'dark red': glooey.Color.from_hex('#aa4e11'),

        'light green': glooey.Color.from_hex('#88e060'),
        'green': glooey.Color.from_hex('#73cd4b'),
        'dark green': glooey.Color.from_hex('#47832c'),

        'light yellow': glooey.Color.from_hex('#ffd948'),
        'yellow': glooey.Color.from_hex('#ffcc00'),
        'dark yellow': glooey.Color.from_hex('#a88600'),

        'white': glooey.Color.from_hex('#ffffff'),
        'light grey': glooey.Color.from_hex('#eeeeee'),
        'dark grey': glooey.Color.from_hex('#aaaaaa'),
        'black': glooey.Color.from_hex('#000000'),
}


@autoprop
class BigLabel(glooey.Label):
    custom_color = 'dark grey'
    custom_font_name = 'KenVector Future'
    custom_font_size = 12

@autoprop
class Label(glooey.Label):
    custom_color = 'dark grey'
    custom_font_name = 'KenVector Future Thin'
    custom_font_size = 10


@autoprop
class Button(glooey.Button):
    custom_color = 'blue' # 'red', 'green', 'yellow', 'grey'
    custom_gloss = 'high' # 'low', 'matte'
    custom_font_color = 'white'

    class Label(Label):
        custom_alignment = 'center'
        custom_font_weight = 'bold'
        custom_horz_padding = 30

    def __init__(self, text=None):
        super().__init__(text)

        self._color = self.custom_color
        self._gloss = self.custom_gloss
        self._update_background()

        self.label.color = self.custom_font_color

    def on_rollover(self, new_state, old_state):
        if new_state == 'down':
            self.label.top_padding = 2 * 4
        if old_state == 'down':
            self.label.top_padding = 0

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color
        self._update_background()

    def get_gloss(self):
        return self._gloss

    def set_gloss(self, new_gloss):
        self._gloss = new_gloss
        self._update_background()

    def _update_background(self):
        gloss = {
                'high': 'high_gloss',
                'low': 'low_gloss',
                'matte': 'matte',
        }
        style = f'buttons/{self._color}/{gloss[self._gloss]}'
        self.set_background(
                base_left=assets.image(f'{style}/base_left.png'),
                base_center=assets.texture(f'{style}/base_center.png'),
                base_right=assets.image(f'{style}/base_right.png'),
                down_left=assets.image(f'{style}/down_left.png'),
                down_center=assets.texture(f'{style}/down_center.png'),
                down_right=assets.image(f'{style}/down_right.png'),
        )


@autoprop
class BlueButton(Button):
    custom_color = 'blue'

@autoprop
class RedButton(Button):
    custom_color = 'red'

@autoprop
class GreenButton(Button):
    custom_color = 'green'

@autoprop
class YellowButton(Button):
    custom_color = 'yellow'
    custom_font_color = 'dark yellow'

@autoprop
class GreyButton(Button):
    custom_color = 'grey'
    custom_font_color = 'dark grey'


@autoprop
class Frame(glooey.Frame):
    custom_color = 'grey'

    class Bin(glooey.Bin):
        custom_padding = 6

    def __init__(self):
        super().__init__()
        self.color = self.custom_color

    def get_color(self):
        return self._color

    def set_color(self, new_color):
        self._color = new_color
        style = f'frames/{self._color}'
        self.decoration.set_appearance(
                center=assets.texture(f'{style}/center.png'),
                top=assets.texture(f'{style}/top.png'),
                left=assets.texture(f'{style}/left.png'),
                bottom=assets.texture(f'{style}/bottom.png'),
                right=assets.texture(f'{style}/right.png'),
                top_left=assets.image(f'{style}/top_left.png'),
                top_right=assets.image(f'{style}/top_right.png'),
                bottom_left=assets.image(f'{style}/bottom_left.png'),
                bottom_right=assets.image(f'{style}/bottom_right.png'),
        )


@autoprop
class BlueFrame(Frame):
    custom_color = 'blue'

@autoprop
class RedFrame(Frame):
    custom_color = 'red'

@autoprop
class GreenFrame(Frame):
    custom_color = 'green'

@autoprop
class YellowFrame(Frame):
    custom_color = 'yellow'

@autoprop
class GreyFrame(Frame):
    custom_color = 'grey'


