"""
Docstring for geometry.greens_theorem
Area using greens theorem
"""

import numpy as np

def greens_area(polygon : np.ndarray) -> float:
    """
    Docstring for greens_area
    Computes area using shoelace formula
    :param polygon: An n by 2 array of (x,y) coords
    :type polygon: np.ndarray
    :return: Area in sq metres
    :rtype: float
    """

    polygon = np.array(polygon)

    x = polygon[:,0]
    y = polygon[:,1]
    xn = np.roll(x,-1)
    yn = np.roll(y,-1)

    area = 0.5 * np.sum(x*yn - xn*y)
    return abs(area)
