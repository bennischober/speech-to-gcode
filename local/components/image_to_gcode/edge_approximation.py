import cv2
import numpy as np

# Normal Edge Approximation
def getEdgeApproxBasic(edge_image, params):
       contours, _ = cv2.findContours(edge_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
       edge_approximations = []

       for c, contour in enumerate(contours):
            # Remove contours smaller than min length
            if len(contour) < params['min_contour_len']:
                continue

            # Dynamic Epsilon
            # epsilon = fixed_epsilon if use_dynamic_epsilon == False else getDynamicEpsilon(contour, epsilon_factor, max_epsilon, min_epsilon)

            # The False parameter is important, so the vertices are in the same order as the contour
            edge_approx = cv2.approxPolyDP(contour, params['epsilon'], False)
            
            # Remove last element if it is already in contour
            if edge_approx[-1] in edge_approx[:len(edge_approx)-2]:
                edge_approx = edge_approx[:-1]
            
            edge_approximations.append(edge_approx)
       
       return edge_approximations

# --------------------- Not implemented yet ------------------------

# Not implemented yet
def getDynamicEpsilon(contour, epsilon_factor, max_epsilon, min_epsilon):
       epsilon_tmp = epsilon_factor * cv2.arcLength(contour, True)
       
       if epsilon_tmp <= max_epsilon and epsilon_tmp >= min_epsilon:
              return epsilon_tmp
       elif epsilon_tmp > max_epsilon:
              return max_epsilon
       elif epsilon_tmp < min_epsilon:
              return min_epsilon

# Deduplicated Edge Approximation (Not implemented yet)
def dropDuplicateContours(segment, feed_points):
    splitted_segments = []
    current_segment = []

    for edge_point, feed in zip(segment, feed_points):
        if not feed:
            if current_segment:
                splitted_segments.append(current_segment)
                current_segment = []
        else:
            current_segment.append([list(edge_point)])

    if current_segment:
        splitted_segments.append(current_segment)

    return splitted_segments

def initialize_indexes(start_point_indexes, indexes, contour_lenth):
    closest_pair = None
    min_distance = float('inf')

    for rescent_index in start_point_indexes:
        for index in indexes:
            distace = min([dist for dist in [contour_lenth - rescent_index + index, index - rescent_index] if dist > 0])
            if distace < min_distance:
                closest_pair = (rescent_index, index)
                min_distance = distace
                
    return closest_pair

def getContourApproxDeduplicated(edge_image, params):

    contours, _ = cv2.findContours(edge_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    contour_segments = []
    for c, contour in enumerate(contours):
        # Remove contours smaller than min length
        if len(contour) < params['min_contour_len']:
            continue

        # Edge Approximation
        approx = [tuple(point[0]) for point in cv2.approxPolyDP(contour, params['epsilon'], True).tolist()]
        contour = [tuple(point[0]) for point in contour.tolist()]

        rescent_index = 0
        used_contour_points = None
        start_point = None

        feed_points = []
        segment = []
        for i in range(len(approx)):
            if i == 0:
                start_point = approx[i]
                segment.append(start_point)
                feed_points.append(True)

            end_point = approx[(i+1) % len(approx)]

            # Reset indexes
            indexes = np.where((np.array(contour) == end_point).all(axis=1))[0]
            if indexes.size == 0:
                break

            if i == 0:
                start_point_indexes = np.where((np.array(contour) == start_point).all(axis=1))[0]

                if len(start_point_indexes) != 1:
                    rescent_index, index = initialize_indexes(start_point_indexes, indexes, len(contour))
                else:
                    rescent_index = start_point_indexes[0]
                    closest_index = min((x for x in indexes if x >= rescent_index), default=None, key=lambda x: abs(x - rescent_index))
                    index = closest_index if closest_index != None else min((x for x in indexes if x >= 0 or x == 0), default=None, key=lambda x: abs(x - 0))
            else:
                closest_index = min((x for x in indexes if x >= rescent_index), default=None, key=lambda x: abs(x - rescent_index))
                index = closest_index if closest_index != None else min((x for x in indexes if x >= 0 or x == 0), default=None, key=lambda x: abs(x - 0))

            # Get the contour points of the segment
            segment_contour_points = None
            if rescent_index == index:
                segment_contour_points = [contour[index]]
            elif i == len(approx) - 1:
                segment_contour_points = contour[rescent_index:] + contour[:index]
            elif rescent_index < index:
                segment_contour_points = contour[rescent_index: index]
            elif rescent_index > index:
                 segment_contour_points = contour[rescent_index: len(contours)] + contour[0: index]
            
            # Check if Contour Points are already used
            if not set(used_contour_points).issuperset(segment_contour_points) if i != 0 else True:
                if i == 0:
                    used_contour_points = segment_contour_points
                else:
                    used_contour_points += segment_contour_points
                feed_points.append(True)
            else:
                feed_points.append(False)

            rescent_index = index + 1
            segment.append(end_point)

        contour_segments += dropDuplicateContours(segment, feed_points)

    return [np.array(contour_segment) for contour_segment in contour_segments]