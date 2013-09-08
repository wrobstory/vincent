from copy import deepcopy

from .visualization import Visualization
from .data import Data
from .transforms import Transform
from .values import ValueRef
from .properties import PropertySet
from .scales import DataRef, Scale
from .marks import ValueRef, MarkProperties, MarkRef, Mark
from .axes import AxisProperties, Axis

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import numpy as np
except ImportError:
    np = None


# TODO: list of factories:
# - line
# - bar
# - stairs
# - stem
# - pie
# - area
# - polar
# - rose
# - compass
# - box
# - semilog / loglog
# - hist
# - contour
# - scatter
# - map


class BarFactory(object):

    def __init__(self, x_scale=None, y_scale=None, mark=None, width=None,
                 height=None):
        if x_scale:
            self.x_scale = x_scale
        else:
            self.x_scale = Scale(
                name='x', range='width', type='ordinal',
                domain=DataRef(data='table', field='data.x'))

        if y_scale:
            self.y_scale = y_scale
        else:
            self.y_scale = Scale(
                name='y', range='height', type='linear', nice=True,
                domain=DataRef(data='table', field='data.y'))

        if mark:
            self.mark = mark
        else:
            self.mark = Mark(
                type='rect', from_=MarkRef(data='table'),
                properties=MarkProperties(
                    enter=PropertySet(
                        x=ValueRef(scale='x', field='data.x'),
                        y=ValueRef(scale='y', field='data.y'),
                        width=ValueRef(scale='x', band=True, offset=-1),
                        y2=ValueRef(scale='y', value=0)),
                    update=PropertySet(fill=ValueRef(value='steelblue'))))

        self.width = width or 400
        self.height = height or 200
        self.padding = {'top': 10, 'left': 30, 'bottom': 20, 'right': 10}
        self.x_axis = Axis(type='x', scale='x')
        self.y_axis = Axis(type='y', scale='y')

    def __call__(self, x, y, color=None, make_copies=True):

        vis = Visualization(width=self.width, height=self.height,
                            padding=self.padding)

        vis.data.append(Data.from_iters(x=x, y=y))

        if make_copies:
            maybe_copy = deepcopy
        else:
            maybe_copy = lambda x: x

        vis.scales.extend(maybe_copy([self.x_scale, self.y_scale]))
        vis.axes.extend(maybe_copy([self.x_axis, self.y_axis]))
        vis.marks.extend(maybe_copy([self.mark]))

        if color:
            vis.marks[0].properties.update.fill.value = color

        return vis

    @property
    def color(self):
        return self.mark.properties.update.fill.value

    @color.setter
    def color(self, value):
        self.mark.properties.update.fill.value = value
