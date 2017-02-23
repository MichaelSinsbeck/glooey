#!/usr/bin/env python3

import pyglet
import demo_helpers
from glooey import *
from glooey.drawing import *
from pprint import pprint

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

root = Gui(window, batch=batch)
hbox = HBox()
root.add(hbox)

@demo_helpers.interactive_tests(window, batch) #
def interactive_hbox_tests():

    # Test adding and removing widgets.
    for i in range(2):
        hbox.add(EventLogger(50, 50))
    yield "Make an HBox with 2 cells."

    left = EventLogger(50, 50, orange)
    hbox.add_left(left)
    yield "Add a orange widget on the left."

    right = EventLogger(50, 50, orange)
    hbox.add_right(right)
    yield "Add a orange widget on the right."

    middle = EventLogger(50, 50, orange)
    hbox.insert(middle, 2)
    yield "Insert a orange widget in the middle."

    hbox.replace(middle, EventLogger(50, 50, green))
    yield "Replace the orange widget in the middle with a green one."

    hbox.remove(left)
    yield "Remove the widget on the left."

    hbox.remove(right)
    yield "Remove the widget on the right."
    
    # Test padding.
    hbox.padding = 10
    yield "Pad the widgets by 10px."
    hbox.padding = 0

    hbox.cell_padding = 10
    yield "Only pad between the widgets."
    hbox.cell_padding = 0

    # Test alignment.
    hbox.alignment = 'center'
    yield "Center-align the whole HBox."
    hbox.alignment = 'fill'

    hbox.cell_alignment = 'center'
    yield "Center-align the widgets."
    hbox.cell_alignment = 'fill'

    # Get ready to restart the tests (and make sure clear() works).
    hbox.clear()
    yield "Clear the HBox."

pyglet.app.run()


