from gui import projectgallery
import os
from lib import log

def makeDirs(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def nextDirName(dir):
    i=1
    nm = "{d}_{i}"
    while os.path.exists(nm.format(d=dir, i=i)): i+=1
    return nm.format(d=dir, i=i)

class FileOperation:
    def __init__(self, path):
        self.path = path

    def do(self, io, handler):
        try:
            handler(io)
        except IOError:
            log.error("IOError", function=self.startWriteSession)
        finally:
            io.close()

    def write(self, writeHandler):
        self.do(open(self.path, "w"), writeHandler)

    def read(self, readHandler):
         self.do(open(self.path, "r"), readHandler)


class ProjectStorage:
    def __init__(self, rootPath="storage"):
        self.rootPath = rootPath
        self.path = os.curdir + os.sep + self.rootPath

    def getPath(self):
        return self.path

    def setName(self, name):
        self.name = name
        self.path = os.curdir + os.sep + self.rootPath + os.sep + self.name

    def getNextName(self, name):
        nrStr=""
        path = os.curdir + os.sep + self.rootPath + os.sep + name
        i=0
        while os.path.exists(path+nrStr): 
            i+=1
            nrStr = "_"+str(i)
        return name + nrStr

    def create(self):
        makeDirs(self.getPath())

    def toPath(self, fileName, mustExist=True):
        if self.path == None: return None
        p = self.path + os.sep + fileName
        if mustExist:
            if os.path.exists(p): return p
        else:
            return p
        return None

    def write(self, fileName, doWrite):
        if self.path == None: return
        fo = FileOperation(self.toPath(fileName, False))
        fo.write(doWrite)

    def read(self, fileName, doRead):
        if self.path == None: return
        fo = FileOperation(self.toPath(fileName))
        fo.read(doRead)

    def validProject(self, prjPath):
        log.debug(function=self.validProject, args=prjPath)
        if not os.path.exists(prjPath): return False
        if not os.path.exists(prjPath+os.sep+"source.png"): return False
        if not os.path.exists(prjPath+os.sep+"plots.npz"): return False
        if not os.path.exists(prjPath+os.sep+"properties.json"): return False
        return True

    def getProjects(self):
        projects = {}
        list = os.listdir(self.path)
        for item in list:
            prjPath = self.toPath(item)
            if self.validProject(prjPath):
                log.debug("item: ", item, function=self.getProjects)
                projects[item] = prjPath
        return projects







    