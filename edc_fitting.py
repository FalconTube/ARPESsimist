from __future__ import print_function
from matplotlib.widgets import RectangleSelector
import numpy as np
import matplotlib.pyplot as plt


class EDCfitter:
    # def __init__(self, data, x1, y1, x2, y2):
    def __init__(self, data):
        self.data = data
        
        