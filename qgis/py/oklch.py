from qgis.core import *
from qgis.gui import *

# https://github.com/color-js/color.js/blob/main/src/spaces/oklch.js

import numpy as np

# Converts OKLCH to OKLAB
def oklch_to_oklab(l, c, h):
    if np.isnan(h):
        a = 0
        b = 0
    else:
        h_rad = np.deg2rad(h)
        a = c * np.cos(h_rad)
        b = c * np.sin(h_rad)
    return np.array([l, a, b])

# Converts OKLAB to XYZ
def oklab_to_xyz(lab):
    M1 = np.array([
        [1,  0.3963377773761749,  0.2158037573099136],
        [1, -0.1055613458156586, -0.0638541728258133],
        [1, -0.0894841775298119, -1.2914855480194092]
    ])
    LMSg = np.dot(M1, lab)
    LMS = LMSg ** 3

    M2 = np.array([
        [ 1.2268798758459243, -0.5578149944602171,  0.2813910456659647],
        [-0.0405757452148008,  1.1122868032803170, -0.0717110580655164],
        [-0.0763729366746601, -0.4214933324022432,  1.5869240198367816]
    ])
    return np.dot(M2, LMS)

# Converts XYZ to linear RGB
def xyz_to_rgb_linear(xyz):
    M = np.array([
        [ 3.2409699419045226,  -1.537383177570094,   -0.4986107602930034],
        [-0.9692436362808796,   1.8759675015077202,   0.04155505740717559],
        [ 0.05563007969699366, -0.20397695888897652,  1.0569715142428786]
    ])
    return np.dot(M, xyz)

# Converts linear RGB to sRGB
def srgb_linear_to_rgb(rgb):
    def linear_to_srgb(c):
        if np.abs(c) > 0.0031308:
            return (1.055 * (np.abs(c) ** (1 / 2.4)) - 0.055) * (1 if c >= 0 else -1)
        else:
            return 12.92 * c
    return np.array([linear_to_srgb(c) for c in rgb])

# Main function to convert OKLCH to RGB
@qgsfunction(group='Custom', referenced_columns=[])
def oklch(l, c, h):
    oklab = oklch_to_oklab(l, c, h)
    xyz = oklab_to_xyz(oklab)
    rgb_linear = xyz_to_rgb_linear(xyz)
    rgb = srgb_linear_to_rgb(rgb_linear)
    
    # Clamp values to ensure they are within the RGB range 0-255
    rgb = np.clip(rgb, 0, 1) 
    return [int(round(val * 255)) for val in rgb]
