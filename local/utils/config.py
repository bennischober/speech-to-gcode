import configparser
import pathlib

_config = configparser.ConfigParser()
_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent.absolute(), 'config.ini')
_config.read(_path)

_root_uri = _config.get('ENDPOINTS', 'RootUri')

SD_ENDPOINT = _root_uri + _config.get('ENDPOINTS', 'StableDiffusion')
STT_ENDPOINT = _root_uri + _config.get('ENDPOINTS', 'SpeechToText')
