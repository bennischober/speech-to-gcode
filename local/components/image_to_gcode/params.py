import numpy as np

# Image Preprocessing Params
blurr_kernel_size = 5

image_size = 720
gcode_size = 120
resize_factor = gcode_size / image_size

# Line Approximation Params
fixed_epsilon = 2.5

use_dynamic_epsilon = False
epsilon_factor = 0.02
max_epsilon = 2.5
min_epsilon = 1.5

# Shortest Path
start_point = np.array([0, 0])

# GCODE Params
z_safe_hight = 10.0
z_working_hight = 1.5
z_zero_height = 0.1
z_feed_height = 0
z_feed = 500
xy_feed = 1000
spindle_speed = 24000

# Maximaler Vorschub ist ca. 3000 (immer bei G0) (3000mm pro Minute)
g0_feed = 3000