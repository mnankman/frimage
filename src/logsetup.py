import lib.wxdyn.log as log
import logging

LOGGER_LEVELS_DEBUG = {
    "lib.wxdyn.persistentobject": logging.INFO,
    "lib.wxdyn.modelobject": logging.ERROR,
    "gui.zoompanel": logging.ERROR,
    "gui.projectgallery": logging.ERROR,
    "core.filemgmt": logging.ERROR,
    "core.model.complex": logging.ERROR,
    "core.model.project": logging.ERROR,
    "core.model.model": logging.ERROR,
    "lib.wxdyn.pubsub": logging.ERROR,
}

LOGGER_LEVELS_PRODUCTION = {
}

SETUP_DEBUG = {
    "format": "[%(name)s] %(levelname)s:%(message)s",
    "level": logging.DEBUG,
    "loggerlevels": LOGGER_LEVELS_DEBUG
}

SETUP_PRODUCTION = {
    "format": "[%(name)s] %(levelname)s:%(message)s",
    "level": logging.ERROR,
    "loggerlevels": LOGGER_LEVELS_PRODUCTION
}

def setup(setup):
    logging.basicConfig(format=setup["format"], level=setup["level"])
    for module, level in setup["loggerlevels"].items():
        log.setLoggerLevel(module, level)