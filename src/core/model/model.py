#foreign
import json

#local
import lib.wxdyn.log as  log
import lib.wxdyn as wxd
from .complex import ComplexProject, JuliaProject, MandelbrotProject

class Application(wxd.ModelObject):
    def __init__(self):
        super().__init__()
        self.__name__ = "FriMage Studio"
        self.__version__ = "0.3"
        self.__storageDir__ = "storage"

    def getName(self):
        return self.__name__

    def getVersion(self):
        return self.__version__

    def getStorageDir(self):
        return self.__storageDir__

class Model(wxd.Publisher):
    PROJECT_TYPE_JULIA = 1
    PROJECT_TYPE_MANDELBROT = 2
    VALID_PROJECT_TYPES = [PROJECT_TYPE_JULIA, PROJECT_TYPE_MANDELBROT]
    EVENTS = [
        "msg_new_project", 
        "msg_generate_complete", 
        "msg_open_project", 
        "msg_project_saved", 
        "msg_sourceimage_selected",
    ]
    def __init__(self):
        self.__application__ = Application()
        self.__currentProject__ = None
        wxd.Publisher.__init__(self, Model.EVENTS)

    def getApplication(self):
        return self.__application__

    def getApplicationTitle(self):
        title = "{} {}"
        return title.format(self.__application__.getName(), self.__application__.getVersion())

    def getCurrentProject(self):
        return self.__currentProject__

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
            self.getCurrentProject().setName(name)
        self.getCurrentProject().setVersion(self.getApplication().getVersion())
        self.getCurrentProject().clearModified(True)
        self.dispatch("msg_new_project", {"project": self.getCurrentProject()})
        return self.__currentProject__

    def saveProperties(self, io):
        data = json.dumps(self.__currentProject__.serialize(), indent=4)
        io.write(data)
        self.getCurrentProject().setTouched(False)
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
        self.getCurrentProject().setPath(storage.getPath())

    def save(self, storage):
        self.getCurrentProject().setVersion(self.getApplication().getVersion())
        self.getCurrentProject().saveThumbnail(storage)
        self.getCurrentProject().savePlots(storage)
        storage.write("properties.json", self.saveProperties)

    def setAttribute(self, attrName, attrValue):
        self.getCurrentProject().setAttribute(attrName, attrValue)

    def animationSetup(self, gensets):
        if len(gensets)==2:
            prj = self.getCurrentProject()
            if isinstance(prj, ComplexProject):
                prj.animationSetup(gensets[1].getArea(), gensets[0].getArea())

    async def animate(self, progressHandler=None):
        prj = self.getCurrentProject()
        if isinstance(prj, ComplexProject):
            await prj.generate(progressHandler, animationsteps=prj.animationsteps)
            self.dispatch("msg_generate_complete", {"project": self.__currentProject__})

    async def preview(self, **kw):
        await self.getCurrentProject().preview(**kw)

    async def generate(self, progressHandler=None, **kw):
        await self.getCurrentProject().generate(progressHandler, **kw)
        self.dispatch("msg_generate_complete", {"project": self.__currentProject__})

    def getGeneratedImage(self):
        return self.getCurrentProject().getGeneratedImage()

    def getProjectSourceImage(self):
        return self.getCurrentProject().getProjectSourceImage()

    def selectProjectSourceImage(self, path):
        if self.getCurrentProject():
            self.getCurrentProject().setProjectSourceImage(path)
            self.dispatch("msg_sourceimage_selected", {"source": self.getCurrentProject().getProjectSource().getSource()})

    def clearProjectTouch(self):
        self.getCurrentProject().setTouched(False)

    def clearProjectModifications(self):
        self.getCurrentProject().clearModified(True)

    def home(self):
        self.getCurrentProject().home()

    def up(self):
        self.getCurrentProject().up()

    def down(self, genSet):
        self.getCurrentProject().down(genSet)

    def remove(self):
        self.getCurrentProject().remove()

    def makeRoot(self):
        self.getCurrentProject().makeRoot()
    

