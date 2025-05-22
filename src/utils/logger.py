import json
import logging
import logging.config
import os
import colorlog

from src.settings.logger_settings import LoggerSettings


class Logger:
    def __init__(self):
        self.logger_settings = LoggerSettings()
        self.log_level = self.logger_settings.log_level
        self.log_directory = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir,
                                          self.logger_settings.log_directory)
        self.config_file = os.path.join(os.path.dirname(__file__), os.pardir, self.logger_settings.config_file_path)
        self.setup_logging()

    def setup_logging(self):
        with open(self.config_file, 'r') as f:
            config = json.load(f)

            config['handlers']['warning_file']['filename'] = os.path.join(self.log_directory, 'warnings.log')
            config['handlers']['error_file']['filename'] = os.path.join(self.log_directory, 'errors.log')

            colorlog_handler = {
                'class': 'colorlog.StreamHandler',
                'formatter': 'colored',
                'level': self.log_level
            }
            config['handlers']['console'] = colorlog_handler

            config['formatters']['colored'] = {
                '()': 'colorlog.ColoredFormatter',
                'format': '%(log_color)s%(asctime)s [%(levelname)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'log_colors': {
                    'DEBUG': 'blue',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white'
                }
            }

            logging.config.dictConfig(config)


log_config = Logger()
logger = logging.getLogger('proj_logger')

