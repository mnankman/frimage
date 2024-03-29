import logging
import inspect
import traceback
from lib.wxdyn import util
from .colored import colored

class ColorLog(object):

    colormap = dict(
        debug=dict(color='white'),
        info=dict(color='cyan', attrs=['bold']),
        warn=dict(color='yellow'),
        warning=dict(color='yellow'),
        error=dict(color='red'),
        critical=dict(color='red', attrs=['bold']),
    )

    def __init__(self, logger):
        self._log = logger

    def __getattr__(self, name):
        if name in ['debug', 'info', 'warn', 'warning', 'error', 'critical']:
            return lambda s, *args: getattr(self._log, name)(
                colored(s, **self.colormap[name]), *args)

        return getattr(self._log, name)


loggers = {}

def argsToString(args):
    s = ""
    n=0
    for item in args:
        if isinstance(item, (tuple, list)):
            s += util.collectionToString(item)
        else:
            s += util.toString(item)
        n+=1
        if n<len(args): s += " "
    return s

def log(logger_method, msg, *args, **kwargs):
    func = None
    fargs = None
    returns = None
    kwargs2 = {}
    args2 = args
    for k,v in kwargs.items():
        if k=="stacktrace":
            stack = inspect.stack()
            i=len(stack)
            while i>3:
                info = stack[i-1]
                s='''File "{}", line {} in {}'''
                print(s.format(info.filename, info.lineno, info.function))
                i-=1
        if k=="function": 
            try:
                func = v.__qualname__
            except:
                func = v
            finally:
                pass
        elif k=="args": 
            fargs = util.collectionToString(v) if isinstance(v, (tuple,list)) else "(" + util.toString(v) + ")"
        elif k=="returns": 
            returns = util.collectionToString(v) if isinstance(v, (tuple,list)) else util.toString(v)
        elif k=="var":
            assert isinstance(v, tuple) and len(v)==2
            varName, varValue = v
            args2 += (varName, "=", varValue)
        else: kwargs2[k] = v
    msg += argsToString(args2)
    if len(msg)>0: msg += " | "
    if func:
        msg += func + (fargs if fargs else "()")
        if returns: 
            msg += " --> " + returns
    #logger_method(util.collectionToString(args))
    logger_method(msg)

def getLogger():
    frm = inspect.stack()[2]
    modName = inspect.getmodule(frm[0]).__name__
    if modName in loggers:
        logger = loggers[modName]
    else:
        logger = ColorLog(logging.getLogger(modName))
        loggers[modName] = logger
        #logging.debug('new logger:', modName)
    return logger

def setLoggerLevel(modName, level):
    if modName in loggers:
        logger = loggers[modName]
    else:
        logger = ColorLog(logging.getLogger(modName))
        loggers[modName] = logger
    logger.setLevel(level)


def debug(*args, **kwargs):
    log(getLogger().debug, "", *args, **kwargs)

def warning(*args, **kwargs):
    log(getLogger().warning, "", *args, **kwargs)

def error(*args, **kwargs):
    log(getLogger().error, "", *args, **kwargs)

def trace(*args, **kwargs):
    log(getLogger().info, "", *args, **kwargs)


