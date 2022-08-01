import lib.wxdyn.log as log
import logging

LOGGER_LEVELS_DEBUG = {
    "lib.wxdyn.persistentobject": logging.ERROR,
    "lib.wxdyn.modelobject": logging.ERROR,
    "gui.zoompanel": logging.ERROR,
    "gui.projectgallery": logging.ERROR,
    "gui.projectpanels": logging.ERROR,
    "core.filemgmt": logging.ERROR,
    "core.model.complex": logging.INFO,
    "core.model.project": logging.INFO,
    "core.model.projectsource": logging.INFO,
    "core.model.model": logging.INFO,
    "lib.wxdyn.pubsub": logging.INFO,
    "lib.wxdyn.styler": logging.ERROR,
    "lib.wxdyn.tabctrl": logging.ERROR,
    "lib.wxdyn.dynctrl": logging.INFO,
    "PIL.PngImagePlugin": logging.ERROR,
    "asyncio": logging.ERROR,
    "lib.imgbox": logging.ERROR,
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