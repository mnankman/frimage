#foreign
import json

#local
from lib import log
from lib.pubsub import Publisher
from lib.modelobject import ModelObject
from .project import JuliaProject, MandelbrotProject

class Application(ModelObject):
    def __init__(self):
        super().__init__()
        self.__name__ = "FriMage Studio"
        self.__version__ = "0.2"
        self.__storageDir__ = "storage"

    def getName(self):
        return self.__name__

    def getVersion(self):
        return self.__version__

    def getStorageDir(self):
        return self.__storageDir__

class AbstractModel():
    def __init__(self): pass
    def getApplication(self): pass    
    def getApplicationTitle(self): pass    
    def newProject(self, projectType, name=None): pass
    async def generate(self, progressHandler=None, **kw): pass
    async def preview(self, **kw): pass
    def selectProjectSourceImage(self, path): pass
    def getGeneratedImage(self): pass
    def getProjectSourceImage(self): pass
    def getCurrentProject(self): pass
    def setAttribute(self, attrName, attrValue): pass
    def load(self, storage): pass
    def save(self, storage): pass
 
class Model(AbstractModel, Publisher):
    PROJECT_TYPE_JULIA = 1
    PROJECT_TYPE_MANDELBROT = 2
    VALID_PROJECT_TYPES = [PROJECT_TYPE_JULIA, PROJECT_TYPE_MANDELBROT]
    EVENTS = ["msg_new_project", "msg_generate_complete", "msg_open_project", "msg_project_saved", "msg_sourceimage_selected"]
    def __init__(self):
        self.__application__ = Application()
        self.__currentProject__ = None
        Publisher.__init__(self, Model.EVENTS)

    def getApplication(self):
        return self.__application__

    def getApplicationTitle(self):
        title = "{} {}"
        return title.format(self.__application__.getName(), self.__application__.getVersion())

    def newProject(self, projectType, name=None):
        log.trace(function=self.newProject, args=(name, projectType))
        assert projectType in Model.VALID_PROJECT_TYPES
        if self.__currentProject__:
            del self.__currentProject__
        if projectType==Model.PROJECT_TYPE_JULIA: 
            self.__currentProject__ = JuliaProject()
        elif projectType==Model.PROJECT_TYPE_MANDELBROT: 
            self.__currentProject__ = MandelbrotProject()
        if name!=None: 
            self.__currentProject__.setName(name)
        self.__currentProject__.setVersion(self.getApplication().getVersion())
        self.getCurrentProject().clearModified(True)
        self.dispatch("msg_new_project", {"project": self.__currentProject__})
        return self.__currentProject__

    def saveProperties(self, io):
        data = json.dumps(self.__currentProject__.serialize(), indent=4)
        io.write(data)
        self.dispatch("msg_project_saved", {"project": self.__currentProject__})

    def loadProperties(self, io):
        data = json.load(io)
        if self.__currentProject__:
            del self.__currentProject__
        if data["type"] == "MandelbrotProject": 
            self.__currentProject__ = MandelbrotProject()
        elif data["type"] == "JuliaProject": 
            self.__currentProject__ = JuliaProject()
        else:
            return
        self.__currentProject__.deserialize(data)
        self.dispatch("msg_open_project", {"project": self.__currentProject__})

    def load(self, storage):
        storage.read("properties.json", self.loadProperties)
        self.getCurrentProject().loadPlots(storage)
        self.getCurrentProject().clearModified(True)

    def save(self, storage):
        self.getCurrentProject().setVersion(self.getApplication().getVersion())
        self.getCurrentProject().saveThumbnail(storage)
        self.getCurrentProject().savePlots(storage)
        storage.write("properties.json", self.saveProperties)
        self.getCurrentProject().clearModified(True)

    def setAttribute(self, attrName, attrValue):
        self.getCurrentProject().setAttribute(attrName, attrValue)

    async def preview(self, **kw):
        await self.getCurrentProject().preview(**kw)

    async def generate(self, progressHandler=None, **kw):
        await self.getCurrentProject().generate(progressHandler, **kw)
        self.dispatch("msg_generate_complete", {"generated": self.getCurrentProject().getGeneratedImage()})

    def getGeneratedImage(self):
        return self.getCurrentProject().getGeneratedImage()

    def getProjectSourceImage(self):
        return self.getCurrentProject().getProjectSourceImage()

    def selectProjectSourceImage(self, path):
        log.trace(function=self.selectProjectSourceImage, args=path)
        if self.getCurrentProject():
            self.getCurrentProject().setProjectSourceImage(path)
            self.dispatch("msg_sourceimage_selected", {"source": self.getCurrentProject().getProjectSource().getSource()})

    def getCurrentProject(self):
        return self.__currentProject__

    

