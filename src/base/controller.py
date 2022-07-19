import json
from lib import log
from base.model import Model, AbstractModel
import base.filemgmt as filemgmt

class Controller:
    def __init__(self, model):
        assert model
        assert isinstance(model, AbstractModel)
        self.model = model
        self.ps = filemgmt.ProjectStorage()

    def reset(self):
        self.model.init()

    def getModel(self):
        return self.model

    def newMandelbrotProject(self, name):
        name = self.ps.getNextName(name)
        self.model.newProject(Model.PROJECT_TYPE_MANDELBROT, name)

    def newJuliaProject(self, name):
        ps = filemgmt.ProjectStorage()
        name = self.ps.getNextName(name)
        self.model.newProject(Model.PROJECT_TYPE_JULIA, name)
        
    def resetProject(self):
        self.model.getCurrentProject().reset()

    def setAttribute(self, attrName, attrValue):
        self.model.setAttribute(attrName, attrValue)

    async def generate(self, progressHandler=None, **kw):
        await self.model.generate(progressHandler, **kw)

    def getGeneratedImage(self):
        return self.model.getGeneratedImage()

    def saveGeneratedImage(self, path):
        self.model.getGeneratedImage().save(path)

    def getProjectSourceImage(self):
        return self.model.getProjectSourceImage()

    def selectProjectSourceImage(self, path):
        self.model.selectProjectSourceImage(path)

    def getCurrentProject(self):
        return self.model.getCurrentProject()

    def saveProject(self):
        log.debug(function=self.saveProject)
        self.ps.setName(self.getCurrentProject().getName())
        self.ps.create()
        self.model.save(self.ps)
        
    def openProject(self, name=None):
        nm = name if name!=None else self.getCurrentProject().getName()
        self.ps.setName(nm)
        self.ps.create()
        self.model.load(self.ps)
        

