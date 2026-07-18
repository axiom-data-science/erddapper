# -*- coding: utf-8 -*-
"""Logging configuration."""
import importlib.resources
import logging
import logging.config
import os

from httpx import URL

from erddapper.datasets import redact_flag_key


logger = logging.getLogger("erddapper")
httpx_logger = logging.getLogger("httpx")


class FlagKeyLoggingFilter(logging.Filter):
    """Logging filter to remove flagKey secret from httpx logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Method to filter flagKey secrets from log lines."""

        if record.args:
            args = []
            for index, arg in enumerate(record.args):
                if isinstance(arg, URL) and "flagKey=" in str(arg):
                    args.append(URL(redact_flag_key(arg)))
                else:
                    args.append(arg)
            record.args = tuple(args)
        return True


def setup_logging():
    """Initializes the project logging."""
    ref = importlib.resources.files("erddapper") / "logging.conf"
    with importlib.resources.as_file(ref) as path:
        logging.config.fileConfig(path, disable_existing_loggers=False)
    level = os.environ.get("LOGLEVEL", "INFO").upper()
    logging.getLogger("erddapper").setLevel(level)

    httpx_logger.addFilter(FlagKeyLoggingFilter())
