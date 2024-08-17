import logging

__all__ = ['lib_logger']




log = logging.getLogger(__name__)
lib_logger= logging.getLogger(name='Lib')
lib_logger.setLevel(logging.INFO)
class CustomFormatter(logging.Formatter):

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    # format = "%(asctime)s %(name)s-%(levelname)s : %(message)s"
    def __init__(self, fmt):
        super().__init__(fmt)
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.grey + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

handler = logging.StreamHandler()
fmt = "%(asctime)s %(name)s-%(levelname)s : %(message)s"
handler.setFormatter(logging.Formatter(fmt))
lib_logger.addHandler(handler)



