import numpy as np
import cv2
from scipy.spatial.distance import cdist
from components.image_to_gcode.gcode_stats import get_gcode_stats
from utils.config import FIXED_PARAMS
from components.image_to_gcode.edge_approximation import getContourApproxDeduplicated, getEdgeApproxBasic

# The converter.py converts the edge image to the gcode

def getContourStartPoint(contours):
    contour_start_points = []
    contour_mapping = []
    for i, contour in enumerate(contours):
        contour_start_points.append(np.array(contour[0][0])) # start_point
        contour_start_points.append(np.array(contour[-1][0])) # end_point

        contour_mapping.append((i, False)) # start_point
        contour_mapping.append((i, True)) # end_point

    return np.array(contour_start_points), np.array(contour_mapping)

# Shortest Path k-nearest-neighbor
def optimize_contour_order(contours, params):
    contour_start_points, contour_mapping = getContourStartPoint(contours) 

    new_order = np.array([])
    contour_end_point = np.array(FIXED_PARAMS["start_point"]) # set the starting point as fist point

    while True:
        nn_index = np.argmin(cdist([contour_end_point], contour_start_points)) # get nearest neighbor index
        nn_p_index = nn_index + 1 if nn_index % 2 == 0 else nn_index - 1 # get partner index
        contour_end_point = contour_start_points[nn_p_index] # Set new contour end

        new_order = np.append(new_order, contour_mapping[nn_index], axis=0) # Update Order

        contour_start_points = np.delete(contour_start_points, [nn_index, nn_p_index], axis=0) # Remove used Kontours
        contour_mapping = np.delete(contour_mapping, [nn_index, nn_p_index], axis=0) # Remove used Kontours

        if len(contour_start_points) == 0:
            break

    # use new_order for contour and reverse some contours
    return [contours[int(c_task[0])] if int(c_task[1]) == 0 else contours[int(c_task[0])][::-1] for c_task in new_order.reshape((-1, 2))] 

def generateGCODE(contours, params):
    # calc resize factor
    rf = params['gcode_size'] / FIXED_PARAMS['image_size']

    gcode_lines = []

    # Set spindle speed and initial altitude
    gcode_lines += [
        f'M03 S{params["spindle_speed"]}', 
        f'G00 Z{params["z_safe_hight"]}'
    ]

    # GCODE for contours
    for i, edge_approx in enumerate(contours):
        gcode_lines += [
            # f'######## Contour {i+1} ########',
            f'G00 X{edge_approx[0][0][0] * rf} Y{edge_approx[0][0][1] * rf}',
            # f'G00 Z{z_working_hight}' if i == 0 else None,
            f'G00 Z{params["z_zero_height"]}',
            f'G01 Z{params["z_feed_height"]} F{params["z_feed"]}',
            f'G01 X{edge_approx[1][0][0] * rf} Y{edge_approx[1][0][1] * rf} F{params["xy_feed"]}' if len(edge_approx) > 1 else None,
            *[f'G01 X{edge[0][0] * rf} Y{edge[0][1] * rf}' for edge in edge_approx[2:]],
            f'G00 Z{params["z_working_hight"]}'
        ]

    # Move the milling head back to the initial position
    gcode_lines += [
        # '######## End ########',
        f'G00 Z{params["z_safe_hight"]}',
        'G00 X0 Y0',
        'M05',
        'M30'
    ]

    # Remove None elements and create GCODE
    return gcode_lines

def image_to_gcode(edge_image, params):
    # Flip Image horizontal
    flipped_image = cv2.flip(edge_image, 0)

    # Edge Approximation
    edges_approx_contours = getEdgeApproxBasic(flipped_image, params)

    # Shortest Path
    ordered_contours = optimize_contour_order(edges_approx_contours, params)

    # Generate GCODE
    gcode_lines = generateGCODE(ordered_contours, params)
    gcode = '\n'.join([line for line in gcode_lines if line != None])

    # Get GCODE statistics
    gcode_stats = get_gcode_stats(ordered_contours, gcode_lines, params)
    return gcode, ordered_contours, gcode_stats

    