""" 
Widgets whose primary role is to contain other widgets.  Most of these widgets 
don't draw anything themselves, they just position children widgets.
"""

import pyglet
import vecrec

from vecrec import Vector, Rect
from collections import defaultdict
from . import drawing
from .widget import Widget
from .helpers import *

def fill(child_rect, parent_rect):
    child_rect.set(parent_rect)

def top_left(child_rect, parent_rect):
    child_rect.top_left = parent_rect.top_left

def top_center(child_rect, parent_rect):
    child_rect.top_center = parent_rect.top_center

def top_right(child_rect, parent_rect):
    child_rect.top_right = parent_rect.top_right

def center_left(child_rect, parent_rect):
    child_rect.center_left = parent_rect.center_left

def center(child_rect, parent_rect):
    child_rect.center = parent_rect.center

def center_right(child_rect, parent_rect):
    child_rect.center_right = parent_rect.center_right

def bottom_left(child_rect, parent_rect):
    child_rect.bottom_left = parent_rect.bottom_left

def bottom_center(child_rect, parent_rect):
    child_rect.bottom_center = parent_rect.bottom_center

def bottom_right(child_rect, parent_rect):
    child_rect.bottom_right = parent_rect.bottom_right

placement_functions = {
        'fill': fill,
        'top_left': top_left,
        'top_center': top_center,
        'top_right': top_right,
        'center_left': center_left,
        'center': center,
        'center_right': center_right,
        'bottom_left': bottom_left,
        'bottom_center': bottom_center,
        'bottom_right': bottom_right,
}

def place_child_in_box(child, box_rect, key_or_function, child_rect=None):
    try:
        placement_function = placement_functions[key_or_function]
    except KeyError:
        placement_function = key_or_function

    if child_rect is None:
        child_rect = child.min_rect

    placement_function(child_rect, box_rect)
    child.resize(child_rect)


def make_grid(rect, cells={}, num_rows=0, num_cols=0, padding=0,
        row_heights={}, col_widths={}, default_row_height='expand',
        default_col_width='expand'):
    """
    Return rectangles for each cell in the specified grid.  The rectangles are 
    returned in a dictionary where the keys are (row, col) tuples.
    """
    num_rows, num_cols = _deduce_grid_shape(cells, num_rows, num_cols)
    min_row_heights, min_col_widths = _find_min_grid_dimensions(
            cells, num_rows, num_cols, row_heights, col_widths, 
            default_row_height, default_col_width)

    # Figure out which rows and columns are expanded and how big those rows and 
    # columns need to be.

    expandable_row_height = (
            + rect.height
            - sum(min_row_heights.fixed.values())
            - padding * (num_rows + 1)
            ) / len(min_row_heights.expandable)
    expandable_col_width = (
            + rect.width
            - sum(min_col_widths.fixed.values())
            - padding * (num_cols + 1)
            ) / len(min_col_widths.expandable)

    # Create the grid.

    grid = {}
    top_cursor = rect.top
    left_cursor = rect.left

    for i in range(num_rows):
        top_cursor += padding
        row_height = min_row_heights.fixed.get(i, expandable_row_height)

        for j in range(num_cols):
            left_cursor += padding
            col_width = min_col_widths.fixed.get(j, expandable_col_width)

            grid[i,j] = Rect.from_size(col_width, row_height)
            grid[i,j].top_left = top_cursor, left_cursor

            left_cursor += col_width
        top_cursor += row_height

    return grid

def claim_grid(cells={}, num_rows=0, num_cols=0, padding=0,
        row_heights={}, col_widths={}, default_row_height='expand',
        default_col_width='expand'):
    
    num_rows, num_cols = _deduce_grid_shape(cells, num_rows, num_cols)
    min_row_heights, min_col_widths = _find_min_grid_dimensions(
            cells, num_rows, num_cols, row_heights, col_widths, 
            default_row_height, default_col_width)

    min_expandable_width = max(min_col_widths.expandable.values())
    min_expandable_height = max(min_row_heights.expandable.values())

    min_width = \
            + sum(min_col_widths.fixed.values())  \
            + min_expandable_width * len(min_col_widths.expandable) \
            + padding * (num_cols + 1)
    min_height = \
            + sum(fixed_min_dims.row_heights.values())  \
            + min_expandable_height * len(expandable_min_dims.row_heights) \
            + padding * (num_rows + 1)

    return min_width, min_height

def _deduce_grid_shape(cells, num_rows, num_cols):
    """
    Return the number of rows and columns in the grid.  More specifically, if 
    the given number of rows or columns is falsey, deduce the number of rows or 
    columns from the indices in the given dictionary of cells.
    """
    if not num_rows:
        for row, col in cells:
            num_rows = max(row + 1, num_rows)

    if not num_cols:
        for row, col in cells:
            num_cols = max(col + 1, num_cols)

    return num_rows, num_cols

def _find_min_grid_dimensions(cells, num_rows, num_cols,
        row_heights, col_widths, default_row_height, default_col_width):
    """
    Return the minimum size needed for by each row and column, considering the 
    widths and heights set by the user and the sizes of the cells in those rows 
    and columns.
    """
    # Make sure the caller didn't forget to use _deduce_grid_shape() to deal 
    # with falsey grid shape values.

    assert num_rows, num_cols

    # Find the width and height of the largest cell in each row and column.
    
    max_cell_heights = defaultdict(int)
    max_cell_widths = defaultdict(int)

    for i,j in cells:
        max_cell_heights[i] = max(cells[i,j].height, max_cell_heights[i])
        max_cell_widths[j]  = max(cells[i,j].width,  max_cell_widths[j])

    # Find the smallest size each row and column can be before the cells won't 
    # fit anymore.

    @attrs # (no fold)
    class MinDimensions:
        fixed = attrib(default=Factory(dict))
        expandable = attrib(default=Factory(dict))

    min_row_heights = MinDimensions()
    min_col_widths = MinDimensions()

    for i in range(num_rows):
        row_height = row_heights.get(i, default_row_height)
        max_cell_height = max_cell_heights.get(i, 0)

        if isinstance(row_height, int):
            min_row_heights.fixed[i] = max(row_height, max_cell_height)
        elif row_height == 'extend':
            min_row_heights.expandable[i] = max_cell_height
        else:
            raise UsageError("illegal row height: {:r}".format(row_height))

    for j in range(num_cols):
        col_width = col_widths.get(j, default_col_width)
        max_cell_width = max_cell_widths.get(j, 0)

        if isinstance(col_width, int):
            min_col_widths.fixed[j] = max(col_width, max_cell_width)
        elif col_width == 'extend':
            min_col_widths.expandable[j] = max_cell_width
        else:
            raise UsageError("illegal col width: {:r}".format(col_width))

    return min_row_heights, min_col_widths


class BinMixin:
    """
    Provide add() and clear() methods for containers that can only have one 
    child widget at a time.  The add() method will automatically remove the 
    existing child if necessary.

    This mixin is intended for classes that are like Bins in the sense that 
    they can only have one child, but don't want to inherit the rest of the 
    actual Bin class's interface, namely support for padding and custom child 
    placement.
    """

    def __init__(self):
        self._child = None

    def add(self, child):
        if self._child is not None:
            self._detach_child(self._child)

        self._child = self._attach_child(child)
        assert self._num_children == 1
        self._resize_and_regroup_children()

    def clear(self):
        self._detach_child(self.child)
        self.child = None
        assert self._num_children == 0
        self._resize_and_regroup_children()

    def get_child(self):
        return self._child

    child = late_binding_property(get_child)


class PaddingMixin:

    def __init__(self, padding=0):
        self._padding = padding

    def get_padding(self):
        return self._padding

    def set_padding(self, new_padding):
        if new_padding is not None:
            self._padding = new_padding
            self.repack()

    padding = late_binding_property(get_padding, set_padding)


class PlacementMixin:

    def __init__(self, placement='fill'):
        self._default_placement = placement
        self._custom_placements = {}

    def get_placement(self):
        return self._default_placement

    def set_placement(self, new_placement):
        self._default_placement = new_placement
        self.repack()

    placement = late_binding_property(get_placement, set_placement)

    def _get_placement(self, key):
        return self._custom_placements.get(key, self._default_placement)

    def _set_custom_placement(self, key, new_placement, repack=True):
        if new_placement is not None:
            self._custom_placements[key] = new_placement
            if repack: self.repack()

    def _unset_custom_placement(self, key, repack=True):
        self._custom_placements.pop(key, None)
        if repack: self.repack()



class Bin (Widget, BinMixin, PaddingMixin, PlacementMixin):

    def __init__(self, padding=0, placement='fill'):
        Widget.__init__(self)
        BinMixin.__init__(self)
        PaddingMixin.__init__(self, padding)
        PlacementMixin.__init__(self, placement)

    def add(self, child, placement=None):
        self._set_custom_placement(child, placement, repack=False)
        BinMixin.add(self, child)

    def clear(self):
        self._unset_custom_placement(child, placement, repack=False)
        BinMixin.clear(self)

    def do_claim(self):
        min_width = 2 * self.padding
        min_height = 2 * self.padding

        if self.child is not None:
            min_width += self.child.min_width
            min_height += self.child.min_height

        return min_width, min_height

    def do_resize_children(self):
        if self.child is not None:
            place_child_in_box(
                    self.child,
                    self.rect.get_shrunk(self.padding),
                    self._get_placement(self.child))


class Frame (Bin):

    def __init__(self, padding=0, placement='fill'):
        super().__init__(padding, placement)
        self.edge_image = None
        self.edge_orientation = None
        self.corner_image = None
        self.corner_orientation = None
        self.vertex_lists = ()

    def set_edge(self, image, orientation='left', autopad=True):
        self.edge_image = image
        self.edge_orientation = orientation

        if autopad and orientation in ('top', 'bottom'):
            self.padding = image.height
        if autopad and orientation in ('left', 'right'):
            self.padding = image.width

    def set_corner(self, image, orientation='top left'):
        if self.edge_image is None:
            raise RuntimeError("Frame.set_corner() cannot be called until Frame.set_edge() has been.")

        self.corner_image = image
        self.corner_orientation = orientation

    def do_draw(self):
        if self.edge_image is None:
            raise ValueError("Must call Frame.set_edge() before Frame.draw().")

        self.vertex_lists = drawing.draw_frame(
                self.rect,
                self.edge_image, self.edge_orientation,
                self.corner_image, self.corner_orientation,
                batch=self.batch, group=self.group, usage='static')

    def do_undraw(self):
        for vertex_list in self.vertex_lists:
            vertex_list.delete()
        self.vertex_lists = ()


class Viewport (Widget, BinMixin):

    class PanningGroup (pyglet.graphics.Group):

        def __init__(self, viewport, parent=None):
            pyglet.graphics.Group.__init__(self, parent)
            self.viewport = viewport

        def set_state(self):
            translation = -self.viewport.get_child_coords(0, 0)
            pyglet.gl.glPushMatrix()
            pyglet.gl.glTranslatef(translation.x, translation.y, 0)

        def unset_state(self):
            pyglet.gl.glPopMatrix()

    def __init__(self, sensitivity=3):
        Widget.__init__(self)
        BinMixin.__init__(self)

        # The panning_vector is the displacement between the bottom-left corner 
        # of this widget and the bottom-left corner of the child widget.

        self._panning_vector = Vector.null()
        self._deferred_center_of_view = None
        self.sensitivity = sensitivity

        # The stencil_group, mask_group, and visible_group members manage the 
        # clipping mask to make sure the child is only visible inside the 
        # viewport.  The panning_group member is used to translate the child in 
        # response to panning events.

        self.stencil_group = None
        self.mask_group = None
        self.visible_group = None
        self.panning_group = None
        self.mask_artist = None

    def do_attach(self):
        # If this line raises a pyglet EventException, you're probably trying 
        # to attach this widget to a GUI that doesn't support mouse pan events.  
        # See the Viewport documentation for more information.
        self.root.push_handlers(self.on_mouse_pan)

    def do_detach(self):
        self.window.remove_handler(self.on_mouse_pan)

    def do_claim(self):
        # The widget being displayed in the viewport can claim however much 
        # space it wants.  The viewport doesn't claim any space, because it can 
        # be as small as it needs to be.
        return 0, 0

    def do_resize(self):
        # Set the center of view if it was previously specified.  The center of 
        # view cannot be directly set until the size of the viewport is known, 
        # but this limitation is hidden from the user by indirectly setting the 
        # center of view as soon as the viewport has a size.
        if self._deferred_center_of_view is not None:
            self.set_center_of_view(self._deferred_center_of_view)

    def do_resize_children(self):
        # Make the child whatever size it wants to be.
        if self.child is not None:
            self.child.resize(self.child.min_rect)

    def do_regroup(self):
        self.stencil_group = drawing.StencilGroup(self.group)
        self.mask_group = drawing.StencilMask(self.stencil_group)
        self.visible_group = drawing.WhereStencilIs(self.stencil_group)
        self.panning_group = Viewport.PanningGroup(self, self.visible_group)

        if self.mask_artist is not None:
            self.mask_artist.group = self.mask_group

    def do_regroup_children(self):
        self.child.regroup(self.panning_group)

    def do_draw(self):
        if self.mask_artist is None:
            self.mask_artist = drawing.Rectangle(
                    self.rect,
                    batch=self.batch,
                    group=self.mask_group)

        self.mask_artist.rect = self.rect

    def do_undraw(self):
        if self.mask_artist is not None:
            self.mask_artist.delete()

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_motion(x, y, dx, dy)

    def on_mouse_enter(self, x, y):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_enter(x, y)

    def on_mouse_leave(self, x, y):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_leave(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_drag_enter(self, x, y):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_drag_enter(x, y)

    def on_mouse_drag_leave(self, x, y):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_drag_leave(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        x, y = self.get_child_coords(x, y)
        super().on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_mouse_pan(self, direction, dt):
        self.panning_vector += direction * self.sensitivity * dt


    @vecrec.accept_anything_as_vector
    def get_child_coords(self, screen_coords):
        viewport_origin = self.rect.bottom_left
        viewport_coords = screen_coords - viewport_origin
        child_origin = self.child.rect.bottom_left
        child_coords = child_origin + self.panning_vector + viewport_coords
        return child_coords

    @vecrec.accept_anything_as_vector
    def get_screen_coords(self, child_coords):
        child_origin = self.child.rect.bottom_left
        viewport_origin = self.rect.bottom_left
        viewport_coords = child_coords - child_origin - self.panning_vector
        screen_coords = view_port_coords + viewport_origin
        return screen_coords

    def get_visible_area(self):
        left, bottom = self.get_child_coords(self.rect.left, self.rect.bottom)
        return Rect.from_dimensions(
                left, bottom, self.rect.width, self.rect.height)

    def get_panning_vector(self):
        return self._panning_vector

    def set_panning_vector(self, vector):
        self._panning_vector = vector

        if self._panning_vector.x < self.child.rect.left:
            self._panning_vector.x = self.child.rect.left

        if self._panning_vector.x > self.child.rect.right - self.rect.width:
            self._panning_vector.x = self.child.rect.right - self.rect.width

        if self._panning_vector.y < self.child.rect.bottom:
            self._panning_vector.y = self.child.rect.bottom

        if self._panning_vector.y > self.child.rect.top - self.rect.height:
            self._panning_vector.y = self.child.rect.top - self.rect.height

    @vecrec.accept_anything_as_vector
    def set_center_of_view(self, child_coords):
        # In order to set the center of view, the size of the viewport widget 
        # is needed.  Unfortunately this information is not available until the 
        # viewport has been attached to a root widget.  To allow this method to 
        # be called at any time, the _deferred_center_of_view member is used in 
        # conjunction with do_resize() to cache the desired center of view.

        if self.rect is None:
            self._deferred_center_of_view = child_coords
        else:
            viewport_center = self.rect.center - self.rect.bottom_left
            self.panning_vector = child_coords - viewport_center
            self._deferred_center_of_view = None


    # Properties (fold)
    panning_vector = property(get_panning_vector, set_panning_vector)


Viewport.register_event_type('on_mouse_pan')

class Grid (Widget, PaddingMixin, PlacementMixin):

    def __init__(self, rows=0, cols=0, padding=0, placement='fill'):
        Widget.__init__(self)
        PaddingMixin.__init__(self, padding)
        PlacementMixin.__init__(self, placement)
        self._grid = dict()
        self._num_rows = rows
        self._num_cols = cols
        self._row_heights = {}
        self._col_widths = {}
        self._default_row_heights = {}
        self._default_col_widths = {}

    def __iter__(self):
        yield from self._grid.values()

    def __len__(self):
        return len(self._grid)

    def __getitem__(self, row_col):
        return self._grid[row_col]

    def __setitem__(self, row_col, child):
        row, col = row_col
        self.add(row, col, child)

    def add(self, row, col, child, placement=None):
        if (row, col) in self._grid:
            self._detach_child(self._grid[row, col])

        self._attach_child(child)
        self._grid[row, col] = child
        self._set_custom_placement((row, col), placement, repack=False)
        self._resize_and_regroup_children()

    def remove(self, row, col):
        self._detach_child(self._grid[row, col])
        del self._grid[row, col]
        self._unset_custom_placement((row, col), placement, repack=False)
        self._resize_and_regroup_children()

    def do_claim(self):
        return claim_grid(
                cells={w.min_rect for w in self},
                num_rows=self._num_rows,
                num_cols=self._num_cols,
                padding=self.padding,
                row_heights=self._row_heights,
                col_widths=self._col_widths,
                default_row_height=self._default_row_height,
                default_col_width=self._default_col_width,
        )

    def do_resize_children(self):
        cell_rects = make_grid(
                rect=self.rect,
                cells={w.min_rect for w in self},
                num_rows=self._num_rows,
                num_cols=self._num_cols,
                padding=self.padding,
                row_heights=self._row_heights,
                col_widths=self._col_widths,
                default_row_height=self._default_row_height,
                default_col_width=self._default_col_width,
        )
        for ij in self._grid:
            child = self._grid[ij]
            placement = self._get_placement(ij)
            place_widget_in_box(child, cell_rects[ij], placement)

    def get_num_rows(self):
        return self._num_rows

    num_rows = late_binding_property(get_num_rows)

    def get_num_cols(self):
        return self._num_cols

    num_cols = late_binding_property(get_num_cols)

    def set_row_height(self, row, new_height):
        """
        Set the width of the given column.  You can provide the width as an 
        integer or the string 'expand'.
        
        If you provide an integer, the column will be that many pixels wide, so 
        long as all the cells in that column fit in that space.  If the cells 
        don't fit, the column will be just wide enough to fit them.  For this 
        reason, it is common to specify a width of "0" to make the column as 
        narrow as possible.

        If you provide the string 'expand', the column will grow to take up any 
        extra space allocated to the grid but not used by any of the other 
        columns.  If multiple columns are set the expand, the extra space will 
        be divided evenly between them.
        """
        self._row_heights[row] = new_height

    def set_col_width(self, col, new_width):
        """
        Set the width of the given column.  You can provide the width as an 
        integer or the string 'expand'.
        
        If you provide an integer, the column will be that many pixels wide, so 
        long as all the cells in that column fit in that space.  If the cells 
        don't fit, the column will be just wide enough to fit them.  For this 
        reason, it is common to specify a width of "0" to make the column as 
        narrow as possible.

        If you provide the string 'expand', the column will grow to take up any 
        extra space allocated to the grid but not used by any of the other 
        columns.  If multiple columns are set the expand, the extra space will 
        be divided evenly between them.
        """
        self._column_widths[col] = new_width

    def unset_row_height(self, row):
        """
        Unset the width of the specified column.  The default width will be 
        used for that column instead.
        """
        del self._row_heights[row]

    def unset_col_width(self, col):
        """
        Unset the width of the specified column.  The default width will be 
        used for that column instead.
        """
        del self._column_widths[col]

    def set_default_row_height(self, new_height):
        """
        Set the default column width.  This width will be used for any columns 
        that haven't been given a specific width.  The meaning of the width are 
        the same as for set_row_height().
        """
        self._default_row_height = new_height

    def set_default_col_width(self, new_width):
        """
        Set the default column width.  This width will be used for any columns 
        that haven't been given a specific width.  The meaning of the width are 
        the same as for set_column_width().
        """
        self._default_column_width = new_width


class HVBox (Widget, PaddingMixin, PlacementMixin):

    def __init__(self, padding=0, placement='fill'):
        Widget.__init__(self)
        PaddingMixin.__init__(self, padding)
        PlacementMixin.__init__(self, placement)
        self._children = list()
        self._expandable = set()

    def add(self, child, expand=False, placement=None):
        self.add_back(child, expand, placement)

    def add_front(self, child, expand=False, placement=None):
        self.insert(child, 0, expand, placement)

    def add_back(self, child, expand=False, placement=None):
        self.insert(child, len(self._children), expand, placement)

    def insert(self, child, index, expand=False, placement=None):
        if expand: self._expandable.add(child)
        self._attach_child(child)
        self._children.insert(index, child)
        self._set_custom_placement(child, placement, repack=False)
        self._resize_and_regroup_children()

    def replace(self, index, child):
        self.remove(self._children[index])
        self.insert(child, index)

    def remove(self, child):
        self._expandable.discard(child)
        self._detach_child(child)
        self._children.remove(child)
        self._unset_custom_placement(child)
        self._resize_and_regroup_children()

    def do_claim(self):
        raise NotImplementedError

    def do_resize_children(self, rect):
        raise NotImplementedError

    def get_children(self):
        return self._children

    children = late_binding_property(get_children)

    def get_expandable_children(self):
        return self._expandable

    expandable_children = late_binding_property(get_expandable_children)


    _dimensions = {     # (fold)
            'horizontal': ('width', 'height'),
            'vertical':   ('height', 'width'),
    }
    _coordinates = {    # (fold)
            'horizontal': ('left', 'top'),
            'vertical':   ('top', 'left'),
    }


    def _help_claim(self, orientation):
        min_width = 0
        min_height = 0
        
        # Account for children

        for child in self.children:
            child.claim()

            if orientation == 'horizontal':
                min_width += child.min_width
                min_height = max(min_height, child.min_height)
            elif orientation == 'vertical':
                min_height += child.min_height
                min_width = max(min_width, child.min_width)
            else:
                raise ValueError("Unknown orientation: {}".format(orientation))

        # Account for padding

        primary_padding = self.padding * (1 + len(self.children))
        secondary_padding = self.padding * 2

        if orientation == 'horizontal':
            min_width += primary_padding
            min_height += secondary_padding
        elif orientation == 'vertical':
            min_width += secondary_padding
            min_height += primary_padding
        else:
            raise ValueError("Unknown orientation: {}".format(orientation))

        return min_width, min_height

    def _help_resize_children(self, orientation):
        if not self.children:
            return

        dimension = self._dimensions[orientation]
        coordinate = self._coordinates[orientation]
        min_dimension = tuple('min_' + x for x in dimension)

        # Figure out how much space is available for expandable children.

        available_space = getattr(self.rect, dimension[0]) - self.padding

        for child in self.children:
            available_space -= getattr(child, min_dimension[0]) + self.padding

        # Resize each child.

        cursor, anchor = self._place_cursor(orientation)

        for child in self.children:
            box_coord_0 = cursor
            box_coord_1 = anchor
            box_dimension_0 = getattr(child, min_dimension[0])
            box_dimension_1 = getattr(self.rect, dimension[1]) - 2 * self.padding

            if child in self.expandable_children:
                box_dimension_0 += available_space / len(self.expandable_children)

            cursor = self._update_cursor(cursor, box_dimension_0, orientation)

            box_rect = Rect(0, 0, 0, 0)
            setattr(box_rect, dimension[0], box_dimension_0)
            setattr(box_rect, dimension[1], box_dimension_1)
            setattr(box_rect, coordinate[0], box_coord_0)
            setattr(box_rect, coordinate[1], box_coord_1)

            place_child_in_box(child, box_rect, self._get_placement(child))

    def _place_cursor(self, orientation):
        top = self.rect.top - self.padding
        left = self.rect.left + self.padding

        if orientation == 'horizontal': return left, top
        elif orientation == 'vertical': return top, left
        else: raise ValueError("Unknown orientation: {}".format(orientation))

    def _update_cursor(self, cursor, child_size, orientation):
        if orientation == 'horizontal':
            return cursor + child_size + self.padding
        elif orientation == 'vertical':
            return cursor - child_size - self.padding
        else:
            raise ValueError("Unknown orientation: {}".format(orientation))


class HBox (HVBox):

    def do_claim(self):
        return HVBox._help_claim(self, 'horizontal')

    def do_resize_children(self):
        HVBox._help_resize_children(self, 'horizontal')


class VBox (HVBox):

    def do_claim(self):
        return HVBox._help_claim(self, 'vertical')

    def do_resize_children(self):
        HVBox._help_resize_children(self, 'vertical')


class Stack (Widget, PaddingMixin, PlacementMixin):
    """
    Have any number of children, claim enough space for the biggest one, and 
    just draw them all in the order they were added.
    """

    def __init__(self, padding=0, placement='fill'):
        Widget.__init__(self)
        PaddingMixin.__init__(self, padding)
        PlacementMixin.__init__(self, placement)
        self._children = []

    def add(self, child, placement=None):
        self.add_back(child, placement)

    def add_front(self, child, placement=None):
        self.insert(child, 0, placement)

    def add_back(self, child, placement=None):
        self.insert(child, len(self.children), placement)

    def insert(self, child, index, placement=None):
        self._attach_child(child)
        self._children.insert(index, child)
        self._set_custom_placement(child, placement, repack=False)
        self._resize_and_regroup_children()

    def replace(self, index, child):
        old_child = self._children[index]
        old_placement = self._get_placement(old_child)
        self.remove(old_child)
        self.insert(child, index, old_placement)

    def remove(self, child):
        self._detach_child(child)
        self._children.remove(child)
        self._unset_custom_placement(child, repack=False)
        self._resize_and_regroup_children()

    def clear(self):
        for child in self.children:
            self._detach_child(child)
        self._children = []
        self._custom_placements = {}
        self._resize_and_regroup_children()

    def do_claim(self):
        max_child_width = 0
        max_child_height = 0

        for child in self.children:
            max_child_width = max(max_child_height, child.min_width)
            max_child_height = max(max_child_height, child.min_height)

        min_width = max_child_width + 2 * self.padding
        min_height = max_child_height + 2 * self.padding

        return min_width, min_height

    def do_resize_children(self):
        for child in self.children:
            place_child_in_box(
                    child,
                    self.rect.get_shrunk(self.padding),
                    self._get_placement(child))

    def do_regroup_children(self):
        for i, child in enumerate(self.children):
            child.regroup(pyglet.graphics.OrderedGroup(i, self.group))

    def get_children(self):
        return self._children

    children = late_binding_property(get_children)

