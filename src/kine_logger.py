import logging
import os
class KineLogger:
    name = "KineReducer"

    @classmethod
    def get_logger(cls):
        return logging.getLogger(cls.name)

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        logging.getLogger(cls.name).debug(msg, *args, **kwargs)

    @classmethod
    def info(cls, msg, *args, **kwargs):
        logging.getLogger(cls.name).info(msg, *args, **kwargs) 
    
    @classmethod
    def warn(cls, msg, *args, **kwargs):
        logging.getLogger(cls.name).warn(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs):
        logging.getLogger(cls.name).error(msg, *args, **kwargs)

    @classmethod
    def critical(cls, msg, *args, **kwargs):
        logging.getLogger(cls.name).critical(msg, *args, **kwargs)    

    @classmethod
    def set_logfile(cls, logfile_path, name='KineReducer'):
        # logpath, logname = os.path.split(logfile_path)
        # cls.logfile = name
        log_format = '%(asctime)s  %(name)8s  %(levelname)5s  %(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=log_format,
                            filename=logfile_path,
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter(log_format))
        cls.name = name
        logging.getLogger(name).addHandler(console)