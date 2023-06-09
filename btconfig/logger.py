import logging
import logging.handlers
import os
import sys

class Logger:

  def __init__(self, **kwargs):
    self.debug = kwargs.get('debug', False)
    self.is_main_logger = kwargs.get('is_main_logger', False)

  def init_logger(self, name=None, debug=False):
    # Setup Logging
    logger = logging.getLogger(name)
    # TODO Find a better approach to this hacky method
    BTCONFIG_DEBUG = os.environ.get('BTCONFIG_DEBUG','').lower()
    if BTCONFIG_DEBUG in ['true','yes','on','1'] or self.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s [%(levelname)s]: %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    )
    # logger.propagate = False
    if self.is_main_logger:
      logger.addHandler(streamhandler)
    return logger