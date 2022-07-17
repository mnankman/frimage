import json
from lib import log
from .model import Model, AbstractModel

class Controller:
    def __init__(self, model):
        assert model
        assert isinstance(model, AbstractModel)
        self.model = model

    def reset(self):
        self.model.init()

    def getModel(self):
        return self.model

    def newMandelbrotProject(self, name=None):
        self.model.newProject(Model.PROJECT_TYPE_MANDELBROT, name)
        self.resetProject()

    def newJuliaProject(self, name=None):
        self.model.newProject(Model.PROJECT_TYPE_JULIA, name)
        self.resetProject()
        
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
        self.saveProjectAs(self.getCurrentProject().getPath())

    def saveProjectAs(self, path):
        log.debug(function=self.saveProject, args=path)
        p = self.getCurrentProject()
        p.setPath(path)
        log.debug(p.__dict__)
        saved = json.dumps(p.serialize(), indent=4)
        f=open(path,"w")
        f.write(saved)
        f.close()
        log.trace("project saved to:", path)

    def openProject(self, path):
        log.debug(function=self.openProject, args=path)
        f=open(path,"r")
        try:
            data = json.load(f)
            self.model.openProject(data)
            self.model.getCurrentProject().setPath(path)
        except TypeError:
            log.error(_("Unable to load project file"), function=self.openProject)
        finally:            
            pass
        f.close()


