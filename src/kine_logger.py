import logging
import os
class KineLogger:
    logfile = "log.txt"

    @classmethod
    def get_logger(cls):
        return logging.getLogger(cls.logfile)

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        logging.getLogger(cls.logfile).debug(msg, *args, **kwargs)

    @classmethod
    def info(cls, msg, *args, **kwargs):
        logging.getLogger(cls.logfile).info(msg, *args, **kwargs) 
    
    @classmethod
    def warn(cls, msg, *args, **kwargs):
        logging.getLogger(cls.logfile).warn(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs):
        logging.getLogger(cls.logfile).error(msg, *args, **kwargs)

    @classmethod
    def critical(cls, msg, *args, **kwargs):
        logging.getLogger(cls.logfile).critical(msg, *args, **kwargs)    

    @classmethod
    def set_logfile(cls, name):
        logpath, logname = os.path.split(name)
        cls.logfile = name
        log_format = '%(asctime)s  %(module)8s  %(levelname)5s  %(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=log_format,
                            filename=cls.logfile,
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter(log_format))
        logging.getLogger(cls.logfile).addHandler(console)