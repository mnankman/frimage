#foreign
import asyncio
import json

#project
import lib.wxdyn.log as  log
from core.model import Model
import core.filemgmt as filemgmt

class Controller:
    def __init__(self, model):
        assert model
        assert isinstance(model, Model)
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

    async def startPreview(self, **setup):
        log.trace(function=self.startPreview)
        while self.getCurrentProject().getPreview():
            if self.getCurrentProject().isModified(True):
                await self.getModel().preview(**setup)
            await asyncio.sleep(3)
        log.trace("previewing stopped")

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

    def clearProjectModifications(self):
        self.model.clearProjectModifications()

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

    def home(self):
        self.model.home()

    def up(self):
        self.model.up()

    def down(self, genSet):
        self.model.down(genSet)
        
    def remove(self):
        self.model.remove()

    def makeRoot(self):
        self.model.makeRoot()
