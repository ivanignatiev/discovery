import logging

def get_logger(name) -> logging.Logger:
  """
  Get a specific logger
  """

  return logging.getLogger(name)