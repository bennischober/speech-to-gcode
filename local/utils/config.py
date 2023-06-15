import configparser
import pathlib

_config = configparser.ConfigParser()
_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent.absolute(), 'config.ini')
_config.read(_path)

_root_uri = _config.get('ENDPOINTS', 'RootUri')

SD_ENDPOINT = _root_uri + _config.get('ENDPOINTS', 'StableDiffusion')
STT_ENDPOINT = _root_uri + _config.get('ENDPOINTS', 'SpeechToText')

# prompts
POSITIVE_PROMPTS = _config.get('PROMPTS', 'Positive').split(',')
NEGATIVE_PROMPTS = _config.get('PROMPTS', 'Negative').split(',')

# params
float_params = ['epsilon', 'gcode_size', 'z_safe_hight', 'z_working_hight', 'z_zero_height', 'z_feed_height', 'est_time_corr_factor']
int_params = ['min_contour_len', 'blurr_kernel_size', 'z_feed', 'xy_feed', 'g0_feed', 'spindle_speed', 'image_size']
list_params = ['start_point']

def convertType(key, value):
    if key in float_params:
        return float(value)
    elif key in int_params:
        return int(value)
    elif key in list_params:
        return [int(x) for x in value.split(',')]
    else:
        return value

DYNAMIC_PARAMS = {key: convertType(key, value) for key, value in dict(_config.items('DYNAMIC_PARAMS')).items()}
FIXED_PARAMS = {key: convertType(key, value) for key, value in dict(_config.items('FIXED_PARAMS')).items()}

# GCODE Default Stats
DEFAUL_GCODE_STATS = dict(_config.items('DEFAUL_GCODE_STATS'))
