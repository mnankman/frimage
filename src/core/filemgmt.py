from gui import projectgallery
import os
import json
import time
import lib.wxdyn.log as  log

def makeDirs(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def nextDirName(dir):
    i=1
    nm = "{d}_{i}"
    while os.path.exists(nm.format(d=dir, i=i)): i+=1
    return nm.format(d=dir, i=i)

def getFileTimes(path):
    tc = os.path.getctime(path)
    tm = os.path.getmtime(path)
    return(time.ctime(tc), time.ctime(tm))

def toPath(path, fileName, mustExist=True):
    log.debug(function=toPath, args=(path, fileName))
    if path == None: return None
    p = path + os.sep + fileName
    if mustExist:
        if os.path.exists(p): return p
    else:
        return p
    return None

class FileOperation:
    def __init__(self, path):
        self.path = path

    def do(self, io, handler):
        result = None
        try:
            result = handler(io)
        except IOError:
            log.error("IOError", function=self.startWriteSession)
        finally:
            io.close()
            return result

    def write(self, writeHandler):
        return self.do(open(self.path, "w"), writeHandler)

    def read(self, readHandler):
        return self.do(open(self.path, "r"), readHandler)


class ProjectStorage:
    def __init__(self, rootPath="storage"):
        self.rootPath = os.curdir + os.sep + rootPath
        self.reset()

    def reset(self):
        self.path = self.rootPath
        self.name = None

    def getRootPath(self):
        return self.rootPath

    def getPath(self):
        return self.path

    def getNextName(self, name):
        nrStr=""
        path = self.rootPath + os.sep + name
        i=0
        while os.path.exists(path+nrStr): 
            i+=1
            nrStr = "_"+str(i)
        return name + nrStr
    
    # sets the focus to the indicated project name
    # this impacts the behaviour of most of the methods of this class
    def setName(self, name):
        self.name = name
        self.path = self.rootPath + os.sep + self.name

    # create the folder for the name that was set with self.setName
    def create(self):
        makeDirs(self.getPath())

    # returns a path to the indicated filename, starting from the current project path
    def toPath(self, fileName, mustExist=True):
        return toPath(self.path, fileName, mustExist)

    # creates a write session for the current focus
    def write(self, fileName, writer):
        if self.path == None: return None
        fo = FileOperation(self.toPath(fileName, False))
        return fo.write(writer)

    # creates a read session for the current focus
    def read(self, fileName, reader):
        if self.path == None: return None
        fo = FileOperation(self.toPath(fileName))
        return fo.read(reader)

    def validProject(self, prjPath):
        log.debug(function=self.validProject, args=prjPath)
        if not os.path.exists(prjPath): return False
        if not os.path.exists(prjPath+os.sep+"source.png"): return False
        if not os.path.exists(prjPath+os.sep+"plots.npz"): return False
        if not os.path.exists(prjPath+os.sep+"properties.json"): return False
        return True

    def getProjectStorageData(self, prjPath=None):
        p = prjPath if prjPath!=None else self.getPath()
        if os.path.exists(p+os.sep+"properties.json"):
            return (p, *getFileTimes(p+os.sep+"properties.json"))
        else:
            return (p, *getFileTimes(p))

    '''
    Returns a list of valid project paths, including creation and modification times
    '''
    def getProjects(self):
        projects = {}
        list = os.listdir(self.rootPath)
        for item in list:
            prjPath = toPath(self.rootPath, item)
            if self.validProject(prjPath):
                log.debug("item: ", item, function=self.getProjects)
                projects[item] = prjPath
        return projects

    def propertiesLoader(self, io):
        log.debug(function=self.propertiesLoader)
        return json.load(io)

    def loadProperties(self):
        prjPath, ct, mt = self.getProjectStorageData()
        prjProps = self.read("properties.json", self.propertiesLoader)
        prjProps["created"] = ct
        prjProps["modified"] = mt
        return prjProps







    