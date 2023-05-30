import numpy as np
import cv2
from scipy.spatial.distance import cdist
from components.image_to_gcode.gcode_stats import get_gcode_stats
from components.image_to_gcode.params import resize_factor, fixed_epsilon, use_dynamic_epsilon, epsilon_factor, max_epsilon, min_epsilon, start_point, z_safe_hight, z_working_hight, z_zero_height, z_feed_height, z_feed, xy_feed, spindle_speed

def getDynamicEpsilon(contour, epsilon_factor, max_epsilon, min_epsilon):
       # Area könnte auch verwendet werden
       epsilon_tmp = epsilon_factor * cv2.arcLength(contour, True)
       
       if epsilon_tmp <= max_epsilon and epsilon_tmp >= min_epsilon:
              return epsilon_tmp
       elif epsilon_tmp > max_epsilon:
              return max_epsilon
       elif epsilon_tmp < min_epsilon:
              return min_epsilon
       
def getEdgeApprox(edge_image, fixed_epsilon):
       contours, _ = cv2.findContours(edge_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
       edge_approximations = []

       for i in range(len(contours)):
            epsilon = fixed_epsilon if use_dynamic_epsilon == False else getDynamicEpsilon(contours[i], epsilon_factor, max_epsilon, min_epsilon)

            edge_approx = cv2.approxPolyDP(contours[i], epsilon, True)
            
            # remove last element if it is already in contour
            if edge_approx[-1] in edge_approx[:len(edge_approx)-2]:
                edge_approx = edge_approx[:-1]
            
            edge_approximations.append(edge_approx)
       
       return edge_approximations

def getContourStartPoint(contours):
    contour_start_points = []
    contour_mapping = []
    for i, contour in enumerate(contours):
        contour_start_points.append(np.array(contour[0][0])) # start_point
        contour_start_points.append(np.array(contour[-1][0])) # end_point

        contour_mapping.append((i, False)) # start_point
        contour_mapping.append((i, True)) # end_point

    return np.array(contour_start_points), np.array(contour_mapping)

# Shortest Path
def optimize_contour_order(contours):
    contour_start_points, contour_mapping = getContourStartPoint(contours) 

    new_order = np.array([])
    contour_end_point = start_point # set the starting point as fist point

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

def generateGCODE(contours):
    gcode_lines = []

    # Drehgeschwindigkeit und initiale Höhe festlegen
    gcode_lines += [
        f'M03 S{spindle_speed}', 
        f'G00 Z{z_safe_hight}'
    ]

    # GCODE für die Kontouren
    for i, edge_approx in enumerate(contours):
        gcode_lines += [
            f'######## Contour {i+1} ########',
            f'G00 X{edge_approx[0][0][0] * resize_factor} Y{edge_approx[0][0][1] * resize_factor}',
            # f'G00 Z{z_working_hight}' if i == 0 else None,
            f'G00 Z{z_zero_height}',
            f'G01 Z{z_feed_height} F{z_feed}',
            f'G01 X{edge_approx[1][0][0] * resize_factor} Y{edge_approx[1][0][1] * resize_factor} F{xy_feed}' if len(edge_approx) > 1 else None,
            *[f'G01 X{edge[0][0] * resize_factor} Y{edge[0][1] * resize_factor}' for edge in edge_approx[2:]],
            f'G00 Z{z_working_hight}'
        ]

    # Fräßkopf zu initialer Position zurückbewegen
    gcode_lines += [
        '######## End ########',
        f'G00 Z{z_safe_hight}',
        'G00 X0 Y0',
        'M05',
        'M30'
    ]

    # None Elemente entfernen und GCODE erstellen
    return gcode_lines

def image_to_gcode(edge_image, params):
    # Resize Image
    # resized_edge_image = cv2.resize(edge_image, (edge_image.shape[1] // resize_factor, edge_image.shape[0] // resize_factor))

    # Edge Approximation
    edges_approx_contours = getEdgeApprox(edge_image, params['epsilon'])

    # Shortest Path
    ordered_contours = optimize_contour_order(edges_approx_contours)

    # Generate GCODE
    gcode_lines = generateGCODE(ordered_contours)
    gcode = '\n'.join([line for line in gcode_lines if line != None])

    # Total feeding time
    gcode_stats = get_gcode_stats(ordered_contours, gcode_lines)
    return gcode, ordered_contours, gcode_stats

    