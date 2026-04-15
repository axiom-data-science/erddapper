# -*- coding: utf-8 -*-
"""Logging configuration."""
import importlib.resources
import logging
import logging.config
import os


logger = logging.getLogger("erddapper")


def setup_logging():
    """Initializes the project logging."""
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
    ref = importlib.resources.files("erddapper") / "logging.conf"
    with importlib.resources.as_file(ref) as path:
        logging.config.fileConfig(path)
