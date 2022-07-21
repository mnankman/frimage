from operator import ge
from tempfile import NamedTemporaryFile

from numpy import deprecate_with_doc
from lib import log, util
from lib.pubsub import Publisher
from lib.modelobject import ModelObject
import img.imgengine
from img.imgbox import ImageBox
from PIL import Image
import json

class ProjectSource(ModelObject):
    def __init__(self, project, path=None):
        super().__init__(project)
        self.__path = path
        self.__source = None
        self.__sourceImage = None
        self.__heatmapBaseImage = None
        self.__gradientImage = None
        self.__heatmapBaseImageWidth = 10
        self.__heatmapBaseImageHeight = 10
        self.__flipGradient = False
        self.persist("path", None)
        self.persist("heatmapBaseImageWidth", 10)
        self.persist("heatmapBaseImageHeight", 10)
        self.persist("flipGradient", False)

    def getPath(self):
        return self.__path
    
    def setPath(self, path):
        self.__path = path
        self.setSource(img.imgengine.Source(path, self.getHeatmapBaseImageSize()))
        self.setModified()

    def setSource(self, source):
        self.__source = source
        self.setSourceImage(source.getSourceImage())
        self.setHeatmapBaseImage(source.getHeatmapBaseImage())
        self.setGradientImage(source.getGradientImage())
        self.setModified()

    def setSourceImage(self, im):
        self.__sourceImage = im
        self.setModified()

    def setHeatmapBaseImage(self, im):
        self.__heatmapBaseImage = im
        self.setModified()

    def setFlipGradient(self, v):
        self.__flipGradient = v
        self.setModified()

    def setGradientImage(self, im):
        self.__gradientImage = im
        self.setModified()

    def getHeatmapBaseImageWidth(self):
        return self.__heatmapBaseImageWidth

    def __initSource__(self):
        if self.__source: self.__source.init(self.getHeatmapBaseImageSize())
        self.setSourceImage(self.__source.getSourceImage())
        self.setHeatmapBaseImage(self.__source.getHeatmapBaseImage())
        self.setGradientImage(self.__source.getGradientImage())
    
    def setHeatmapBaseImageWidth(self, w):
        log.debug(function=self.setHeatmapBaseImageWidth, args=w)
        self.__heatmapBaseImageWidth = int(w)
        self.__initSource__()
        self.setModified()

    def getHeatmapBaseImageHeight(self):
        return self.__heatmapBaseImageHeight

    def setHeatmapBaseImageHeight(self, h):
        log.debug(function=self.setHeatmapBaseImageHeight, args=h)
        self.__heatmapBaseImageHeight = int(h)
        self.__initSource__()
        self.setModified()

    def getHeatmapBaseImageSize(self):
        return (self.__heatmapBaseImageWidth, self.__heatmapBaseImageHeight)
    
    def setHeatmapBaseImageSize(self, size):
        self.__heatmapBaseImageWidth, self.__heatmapBaseImageHeight = size
        self.setModified()

    def getSource(self):
        return self.__source

    def getSourceImage(self):
        return self.__sourceImage

    def getHeatmapBaseImage(self):
        return self.__heatmapBaseImage

    def getFlipGradient(self):
        return self.__flipGradient

    def getGradientImage(self):
        im = self.__gradientImage
        if im!=None:
            if self.__flipGradient:
                return im.transpose(method=Image.FLIP_LEFT_RIGHT)
        return im

    def getGradientPixels(self, w):
        return self.__source.getGradientPixels(w, self.__flipGradient)

    def saveSourceImage(self, storage):
        im = self.getSourceImage()
        if im != None:
            imgPath = storage.toPath("source.png", False)
            im.save(imgPath)
            self.__path = imgPath
    
    def toString(self):
        s =  self.getId() + ": " + self.__path
        return s

    def print(self):
        log.trace(self.toString())

class Area(ModelObject):
    def __init__(self, project):
        super().__init__(project)
        self.__xa = None
        self.__xb = None
        self.__ya = None
        self.__yb = None
        self.persist("xa", None)
        self.persist("xb", None)
        self.persist("ya", None)
        self.persist("yb", None)

    def getXa(self): return self.__xa
    def getXb(self): return self.__xb
    def getYa(self): return self.__ya
    def getYb(self): return self.__yb

    def getAll(self): return (self.__xa, self.__xb, self.__ya, self.__yb)

    def getRect(self): 
        try:
            rect = (self.__xa, self.__ya, self.__xb - self.__xa, self.__yb - self.__ya)
        except TypeError as e:
            rect = None
        return rect

    def setXa(self, v): 
        fv = float(v) if v!=None else None
        log.debug(function=self.setXa, args=fv)
        self.__xa = fv
        self.setModified()
        log.debug("area:", self.toString())

    def setXb(self, v): 
        fv = float(v) if v!=None else None
        log.debug(function=self.setXb, args=fv)
        self.__xb = fv
        self.setModified()
        log.debug("area:", self.toString())

    def setYa(self, v): 
        fv = float(v) if v!=None else None
        log.debug(function=self.setYa, args=fv)
        self.__ya = fv
        self.setModified()
        log.debug("area:", self.toString())

    def setYb(self, v): 
        fv = float(v) if v!=None else None
        log.debug(function=self.setYb, args=fv)
        self.__yb = fv
        self.setModified()
        log.debug("area:", self.toString())

    def setAll(self, area):
        self.__xa, self.__xb, self.__ya, self.__yb = area
        self.setModified()

    def setRect(self, rect):
        x,y,w,h = rect
        self.__xa = x
        self.__xb = x+w
        self.__ya = y
        self.__yb = y+h
        self.setModified()

    def toString(self):
        s =  self.getId() + ": " + str((self.__xa, self.__xb, self.__ya, self.__yb))
        return s

class Cxy(ModelObject):
    def __init__(self, project):
        super().__init__(project)
        self.__cx = None
        self.__cy = None
        self.persist("cx", None)
        self.persist("cy", None)

    def getCx(self): return self.__cx
    def getCy(self): return self.__cy
    def getCxy(self): return (self.__cx, self.__cy)

    def setCx(self, v): 
        fv = float(v) if v!=None else None
        self.__cx = fv
        self.setModified()

    def setCy(self, v): 
        fv = float(v) if v!=None else None
        self.__cy = fv
        self.setModified()

    def setCxy(self, cxy):
        self.__cx, self.__cy = cxy
        self.setModified()

    def toString(self):
        s =  self.getId() + ": " + str((self.__cx, self.__cy))
        return s

class Project(ModelObject):
    def __init__(self):
        super().__init__()
        self.__name = None
        self.__artist = None
        self.__width = None
        self.__height = None
        self.__borderSize = 0
        self.__borderColourPick = 255
        self.projectSource = ProjectSource(self)
        self.generatedImage = None
        self.path = None
        self.progress = 0
        self.persist("name")
        self.persist("artist")
        self.persist("width")
        self.persist("height")
        self.persist("borderSize", 2)
        self.persist("borderColourPick", 255)
        
    def reset(self):
        pass
        
    def setName(self, name):
        self.__name = name
        self.setModified()
        
    def setArtist(self, artist):
        self.__artist = artist
        self.setModified()
        
    def setWidth(self, w):
        self.__width = w

    def setHeight(self, h):
        self.__height = h

    def setSize(self, size):
        self.__width, self.__height = size
        self.setModified()

    def setBorderSize(self, b):
        self.__borderSize = b
        self.setModified()

    def setBorderColourPick(self, p):
        self.__borderColourPick = p
        self.setModified()

    def setPath(self, path):
        self.path = path
        self.setModified()
        
    def getProjectSourceImage(self):
        return self.projectSource.getSource().getSourceImage()

    def setProjectSourceImage(self, path):
        self.projectSource.setPath(path)

    def getProjectSource(self):
        return self.projectSource

    def getName(self):
        return self.__name

    def getArtist(self):
        return self.__artist

    def getSize(self):
        return (self.__width, self.__height)

    def getWidth(self):
        return self.__width

    def getHeight(self):
        return self.__height
        
    def getBorderSize(self):
        return self.__borderSize

    def getBorderColourPick(self):
        return self.__borderColourPick

    def getPath(self):
        return self.path

    def generate(self):
        pass

    def getProgress(self):
        return self.progress

    def setProgress(self, p):
        self.progress = p
        self.setModified()

    def onProgress(self, generator, p):
        log.debug(function=self.onProgress, args=p)
        self.setProgress(p)

    async def generate(self, generator, progressHandler=None, preview=False, **setup):
        log.debug(function=self.generate, args=(generator, preview, setup))
        if preview:
            w,h = setup["size"]
            setup["size"] = (int(w/10), int(h/10))
        generator.setup(**setup)
        h = self.onProgress if progressHandler==None else progressHandler
        self.setProgress(0)
        await generator.generate(progressHandler=h)
        b = self.getBorderSize()
        p = self.getBorderColourPick()        
        pixels = self.getProjectSource().getGradientPixels(generator.maxIt)
        fractalBox = ImageBox(ImageBox.ORIENTATION_HORIZONTAL, b, b, pixels[p])
        fractalBox.addImage(generator.getImage())
        self.setGeneratedImage(fractalBox.getImage())
        log.trace("generation complete")

    def up(self):
        pass

    def setGeneratedImage(self, im):
        self.generatedImage = im
        self.setModified()

    def getGeneratedImage(self):
        return self.generatedImage

    def saveImages(self, storage):
        pass

    def loadImages(self, storage):
        pass

    def toString(self):
        s =  self.getId() + ": " + self.__name
        return s

    def print(self):
        log.trace(self.toString())


class GeneratedSet(ModelObject):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.area = Area(self)
        self.__name = name
        self.__generatedImage = None
        self.__generatedSets = []
        self.persist("name")

    def setName(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def getArea(self):
        return self.area

    def setArea(self, area):
        self.area.setAll(area)

    def getGeneratedImage(self):
        return self.__generatedImage

    def setGeneratedImage(self, im):
        self.__generatedImage = im
        self.setModified()

    def addGeneratedSet(self):
        newSet = self.newGeneratedSet()
        self.__generatedSets.append(newSet)
        return newSet

    def newGeneratedSet(self):
        if isinstance(self.getParent(), GeneratedSet):
            nm = self.getName()
        else:
            nm = "step"
        newSet = self.__construct__(nm  + "_" + str(len(self.__generatedSets)+1))
        return newSet

    def __construct__(self, nm):
        return GeneratedSet(self, nm)

    def getGeneratedSets(self):
        return self.__generatedSets

    def getDepth(self, d=1):
        depth = d
        for s in self.__generatedSets:
            sd = s.getDepth(d+1)
            depth = sd if sd>depth else depth
        return depth

    def saveImages(self, storage):
        im = self.getGeneratedImage()
        if im != None:
            imgPath = storage.toPath(self.getName()+".png", False)
            im.save(imgPath)
            log.debug("saved image to ", imgPath, function=self.saveImages)
        for gs in self.getGeneratedSets():
            gs.saveImages(storage)

    def loadImages(self, storage):
        imgPath = storage.toPath(self.getName()+".png")
        if imgPath!=None: self.setGeneratedImage(Image.open(imgPath))
        for gs in self.getGeneratedSets():
            gs.loadImages(storage)

class MandelbrotProject(Project):
    def __init__(self):
        super().__init__()
        self.rootSet = GeneratedSet(self, "root")
        self.currentSet = self.rootSet
        self.generator = None
        self.__maxIt = None
        self.persist("maxIt")
        self.init()

    def init(self):
        self.setSize((400,400))
        self.setArea((-2.0,1.0,-1.5,1.5))
        self.setMaxIt(256)

    def setMaxIt(self, maxIt):
        self.__maxIt = maxIt
        self.setModified()

    def getMaxIt(self):
        return self.__maxIt

    def getArea(self):
        return self.currentSet.getArea()

    def setArea(self, area):
        self.currentSet.setArea(area)
        self.setModified()

    # this one is needed so PersistentObject can restore it from a serialized stream
    def getGeneratedSet(self):
        return self.rootSet

    def getRootSet(self):
        return self.rootSet

    def getCurrentSet(self):
        return self.currentSet

    def reset(self):
        self.setSize((400,400))

    def setGeneratedImage(self, im):
        assert self.currentSet != None
        self.currentSet.setGeneratedImage(im)
        self.setModified()

    def getGeneratedImage(self):
        if self.currentSet == None: return None
        return self.currentSet.getGeneratedImage()

    def down(self, genSet):
        parent = genSet.getParent()
        if parent != None and isinstance(genSet, GeneratedSet) and parent==self.currentSet:
            log.debug(function=self.down, args=genSet)
            self.currentSet = genSet
            self.setModified()

    def up(self):
        parent = self.currentSet.getParent()
        if parent != None and isinstance(parent, GeneratedSet):
            log.debug(function=self.up)
            self.currentSet = parent
            self.setModified()

    def setProjectSourceImage(self, path):
        super().setProjectSourceImage(path)
        if self.generator:
            self.generator.source = self.getProjectSource().getSource()
            self.setGeneratedImage(self.generator.getImage())

    async def generate(self, progressHandler=None, preview=False, **kw):
        log.debug(function=self.generate, args=kw)
        self.generator = img.imgengine.MandelbrotGenerator(self.getProjectSource().getSource())
        if kw!=None and "area" in kw.keys():
            areaRect = kw["area"]
        else:
            areaRect = self.currentSet.getArea().getRect()
        if areaRect!=None and self.currentSet.getGeneratedImage()!=None:
            genSet = self.currentSet.addGeneratedSet()
            genSet.getArea().setRect(areaRect)
            self.currentSet = genSet
        await super().generate(
            self.generator, 
            progressHandler,
            preview,
            size=self.getSize(), 
            reverseColors=self.getProjectSource().getFlipGradient(), 
            area=self.currentSet.getArea().getAll()
        )

    def saveImages(self, storage):
        self.getProjectSource().saveSourceImage(storage)
        self.getRootSet().saveImages(storage)

    def loadImages(self, storage):
        self.getRootSet().loadImages(storage)

class GeneratedJuliaSet(GeneratedSet):
    def __init__(self, parent, name):
        super().__init__(parent, name)
        self.cxy = Cxy(self)

    def getCxy(self):
        return self.cxy

    def setCxy(self, cxy):
        self.cxy.setCxy(cxy)

    def __construct__(self, nm):
        return GeneratedJuliaSet(self, nm)

    def addGeneratedJuliaSet(self):
        return GeneratedSet.addGeneratedSet(self)


class JuliaProject(Project):
    def __init__(self):
        super().__init__()
        self.rootSet = GeneratedJuliaSet(self, "root")
        self.currentSet = self.rootSet
        self.generator = None
        self.__maxIt = None
        self.persist("maxIt")
        self.init()

    def init(self):
        self.setSize((600,450))
        self.setArea((-0.0008,0.0008,-0.0008,0.0008))
        self.setCxy((-0.6523253489293293, -0.44925312958958075))
        self.setMaxIt(256)

    def setMaxIt(self, maxIt):
        self.__maxIt = maxIt
        self.setModified()

    def getMaxIt(self):
        return self.__maxIt

    def getArea(self):
        return self.currentSet.getArea()

    def setArea(self, area):
        self.currentSet.setArea(area)
        self.setModified()

    def getCxy(self):
        return self.currentSet.getCxy()

    def setCxy(self, cxy):
        self.currentSet.setCxy(cxy)

    # this one is needed so PersistentObject can restore it from a serialized stream
    def getGeneratedJuliaSet(self):
        return self.rootSet

    def getRootSet(self):
        return self.rootSet

    def getCurrentSet(self):
        return self.currentSet

    def reset(self):
        self.setSize((600,450))
        self.setCxy((-0.6523253489293293, -0.44925312958958075))

    def setGeneratedImage(self, im):
        assert self.currentSet != None
        self.currentSet.setGeneratedImage(im)
        self.setModified()

    def getGeneratedImage(self):
        if self.currentSet == None: return None
        return self.currentSet.getGeneratedImage()

    def down(self, genSet):
        parent = genSet.getParent()
        if parent != None and isinstance(genSet, GeneratedSet) and parent==self.currentSet:
            log.debug(function=self.down, args=genSet)
            self.currentSet = genSet
            self.setModified()

    def up(self):
        parent = self.currentSet.getParent()
        if parent != None and isinstance(parent, GeneratedSet):
            log.debug(function=self.up)
            self.currentSet = parent
            self.setModified()
 
    def setProjectSourceImage(self, path):
        super().setProjectSourceImage(path)
        if self.generator:
            self.generator.source = self.getProjectSource().getSource()
            self.setGeneratedImage(self.generator.getImage())

    async def generate(self, progressHandler=None, preview=False, **kw):
        log.debug(function=self.generate, args=kw)
        self.generator = img.imgengine.JuliaGenerator(self.getProjectSource().getSource())
        if kw!=None and "area" in kw.keys():
            areaRect = kw["area"]
        else:
            areaRect = self.currentSet.getArea().getRect()
        cxy = self.currentSet.getCxy().getCxy()
        if areaRect!=None and self.currentSet.getGeneratedImage()!=None:
            genSet = self.currentSet.addGeneratedJuliaSet()
            genSet.getArea().setRect(areaRect)
            genSet.getCxy().setCxy(cxy)
            self.currentSet = genSet
        await super().generate(
            self.generator, 
            progressHandler,
            preview,
            size=self.getSize(), 
            reverseColors=self.getProjectSource().getFlipGradient(), 
            area=self.currentSet.getArea().getAll(),
            cxy=self.currentSet.getCxy().getCxy()
        )

    def saveImages(self, storage):
        self.getProjectSource().saveSourceImage(storage)
        self.getRootSet().saveImages(storage)

    def loadImages(self, storage):
        self.getRootSet().loadImages(storage)


class AbstractModel():
    def __init__(self):
        pass
    
    def newProject(self, projectType, name=None):
        pass

    async def generate(self, progressHandler=None, **kw):
        pass

    def selectProjectSourceImage(self, path):
        pass

    def getGeneratedImage(self):
        pass

    def getProjectSourceImage(self):
        pass

    def getCurrentProject(self):
        pass

    def openProject(self, data):
        pass

    def setAttribute(self, attrName, attrValue):
        pass

    def load(self, storage):
        pass

    def save(self, storage):
        pass
 

class Model(AbstractModel, Publisher):
    PROJECT_TYPE_JULIA = 1
    PROJECT_TYPE_MANDELBROT = 2
    VALID_PROJECT_TYPES = [PROJECT_TYPE_JULIA, PROJECT_TYPE_MANDELBROT]
    EVENTS = ["msg_new_project", "msg_generate_complete", "msg_open_project", "msg_sourceimage_selected"]
    def __init__(self):
        self.currentProject = None
        Publisher.__init__(self, Model.EVENTS)

    def newProject(self, projectType, name=None):
        log.trace(function=self.newProject, args=(name, projectType))
        assert projectType in Model.VALID_PROJECT_TYPES
        if self.currentProject:
            del self.currentProject
        if projectType==Model.PROJECT_TYPE_JULIA: 
            self.currentProject = JuliaProject()
        elif projectType==Model.PROJECT_TYPE_MANDELBROT: 
            self.currentProject = MandelbrotProject()
        if name!=None: 
            self.currentProject.setName(name)
        self.dispatch("msg_new_project", {"project": self.currentProject})
        return self.currentProject

    def saveProperties(self, io):
        data = json.dumps(self.currentProject.serialize(), indent=4)
        io.write(data)

    def loadProperties(self, io):
        data = json.load(io)
        if self.currentProject:
            del self.currentProject
        if data["type"] == "MandelbrotProject": 
            self.currentProject = MandelbrotProject()
        elif data["type"] == "JuliaProject": 
            self.currentProject = JuliaProject()
        else:
            return
        self.currentProject.deserialize(data)
        self.dispatch("msg_open_project", {"project": self.currentProject})

    def load(self, storage):
        storage.read("properties.json", self.loadProperties)
        self.currentProject.loadImages(storage)
        self.currentProject.clearModified()

    def save(self, storage):
        self.currentProject.saveImages(storage)
        storage.write("properties.json", self.saveProperties)
        self.currentProject.clearModified()

    def setAttribute(self, attrName, attrValue):
        self.currentProject.setAttribute(attrName, attrValue)

    async def generate(self, progressHandler=None, preview=False, **kw):
        await self.getCurrentProject().generate(progressHandler, preview, **kw)
        self.dispatch("msg_generate_complete", {"generated": self.currentProject.getGeneratedImage()})

    def getGeneratedImage(self):
        return self.getCurrentProject().getGeneratedImage()

    def getProjectSourceImage(self):
        return self.getCurrentProject().getProjectSourceImage()

    def selectProjectSourceImage(self, path):
        log.trace(function=self.selectProjectSourceImage, args=path)
        if self.currentProject:
            self.currentProject.setProjectSourceImage(path)
            self.dispatch("msg_sourceimage_selected", {"source": self.currentProject.getProjectSource().getSource()})

    def getCurrentProject(self):
        return self.currentProject

    

