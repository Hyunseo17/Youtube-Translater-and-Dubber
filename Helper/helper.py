import os
import ssl
import logging

class Helper:
  
    def __init__(self, log_level=logging.DEBUG):
        self.log = self.custom_logger(log_level)
    
    @staticmethod
    def create_unverified_https_context():
        # Create an unverified context
        ssl._create_default_https_context = ssl._create_unverified_context

    @staticmethod
    def define_delimiter():
        delim = "----------------------------------------"
        return delim
    
    @staticmethod
    def fresh_work_dir (dir):
        if not os.path.exists(f'{os.getcwd()}/{dir}'):
            os.makedirs(f'{os.getcwd()}/{dir}')
        work_dir = f'{os.getcwd()}/{dir}'
        os.system(f'rm -rf {work_dir}/*')
        return work_dir

    @staticmethod
    def custom_logger(level):
        # Create a custom logger
        logger = logging.getLogger(__name__)
        #logging.basicConfig(level=level.upper())
        logger.setLevel(level)
        
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(level)
        formatter = logging.Formatter('\x1b[33;20m' + '%(asctime)s - %(levelname)s: %(message)s' + '\x1b[0m', datefmt='%m/%d/%Y %I:%M:%S%p')
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)
        # logger.debug('debug message')
        # logger.info('info message')
        # logger.warn('warn message')
        # logger.error('error message')
        # logger.critical('critical message')

        return logger
            