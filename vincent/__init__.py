# -*- coding: utf-8 -*-
import legacy
from charts import Bar, Line, Area, Scatter, StackedBar, StackedArea
from visualization import Visualization
from data import Data
from transforms import Transform
from values import ValueRef
from properties import PropertySet
from scales import DataRef, Scale
from marks import ValueRef, MarkProperties, MarkRef, Mark
from axes import AxisProperties, Axis
from factories import (BarFactory)
from ipynb import init_d3, init_vg, display_vega
