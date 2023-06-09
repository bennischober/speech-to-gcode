import numpy as np
from utils.config import FIXED_PARAMS

def calculate_g0_distance(contours, params):
    # calc resize factor
    rf = params['gcode_size'] / FIXED_PARAMS['image_size']

    total_distance = 0
    start_end_point = np.array([0, 0])
    recent_contour_end = start_end_point

    for contour in contours:
        contour_points = contour.squeeze()
        start = contour_points[0] # set startPoint of Contour
        total_distance += np.linalg.norm(start * rf - recent_contour_end * rf)  # Calc euklidian dinstance
        recent_contour_end = contour_points[-1] # set endPoint of Contour

    total_distance += np.linalg.norm(np.array([0, 0]) - recent_contour_end)

    return total_distance

def calculate_g1_distance(contours, params):
    # calc resize factor
    rf = params['gcode_size'] / FIXED_PARAMS['image_size']
    
    total_distance = 0

    for contour in contours:
        contour = contour.squeeze()
        recent_point = contour[0]

        for point in contour[1:]:
            total_distance += np.linalg.norm(recent_point * rf - point * rf)
            recent_point = point

    return total_distance

def calculate_z_distance(contours, params):
    g0_z_distance = params['z_safe_hight'] - params['z_working_hight'] + (params['z_working_hight'] - params['z_zero_height']) * 2 * len(contours)
    g1_z_distance = (params['z_zero_height'] - params['z_feed_height']) * len(contours)

    return g0_z_distance, g1_z_distance

def convert_min_to_time(minutes):
    total_time_seconds = int((minutes) * 60)
    total_time_hours = total_time_seconds // 3600
    remaining_seconds = total_time_seconds % 3600
    total_time_minutes = remaining_seconds // 60
    remaining_seconds = remaining_seconds % 60

    return f'{total_time_hours:02d}:{total_time_minutes:02d}:{remaining_seconds:02d}'

def get_gcode_stats(contours, gcode, params):
    g0_xy_distance = calculate_g0_distance(contours, params)
    g1_xy_distance = calculate_g1_distance(contours, params)
    g0_z_distance, g1_z_distance = calculate_z_distance(contours, params)

    total_feeding_time = (g0_xy_distance / params['g0_feed']) + (g1_xy_distance / params['xy_feed']) + (g0_z_distance / params['g0_feed']) + (g1_z_distance / params['z_feed'])
    g0_feeding_time = (g0_xy_distance / params['g0_feed']) + (g0_z_distance / params['g0_feed'])
    g1_feeding_time = (g1_xy_distance / params['xy_feed']) + (g1_z_distance / params['z_feed'])

    return {
        'total_feeding_time': convert_min_to_time(total_feeding_time),
        'amt_contours': len(contours),
        'amt_gcode_lines': len(gcode),
        'g0_xy_distance': round(g0_xy_distance, 2),
        'g0_z_distance': round(g0_z_distance, 2),
        'g0_feeding_time': convert_min_to_time(g0_feeding_time),
        'g1_xy_distance': round(g1_xy_distance, 2),
        'g1_z_distance': round(g1_z_distance, 2),
        'g1_feeding_time': convert_min_to_time(g1_feeding_time)
    }