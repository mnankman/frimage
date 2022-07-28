import lib.wxdyn.log as  log
import lib.wxdyn as wxd
from lib.imgbox import ImageBox
import core.fgen
from .projectsource import ProjectSource

class Project(wxd.ModelObject):
    def __init__(self):
        super().__init__()
        self.__name = None
        self.__artist = None
        self.__version = None
        self.__width = None
        self.__height = None
        self.__borderSize = 0
        self.__borderColourPick = 255
        self.projectSource = ProjectSource(self)
        self.__generatedPlot__ = None
        self.__maxPlotValue__ = None
        self.__generatedImage__ = None
        self.path = None
        self.progress = 0
        self.__preview__ = False
        self.previewImage = None
        self.saved = False
        self.persist("name")
        self.persist("artist")
        self.persist("version")
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

    def setVersion(self, version):
        self.__version = version
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

    def getVersion(self):
        return self.__version

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

    def getPreview(self):
        return self.__preview__

    def setPreview(self, v):
        if v!=self.__preview__:
            self.__preview__ = v
            self.setModified()

    def getPreviewImage(self):
        return self.previewImage

    def setPreviewImage(self, im):
        self.previewImage = im
        self.setModified()

    def getProgress(self):
        return self.progress

    def setProgress(self, p):
        self.progress = p
        self.setModified()

    def getSaved(self):
        return self.saved

    def setSaved(self, saved):
        if saved!=self.saved:
            self.saved = saved
            self.setModified()

    def getGeneratedPlot(self):
        return self.__generatedPlot__

    def setGeneratedPlot(self, plot):
        self.__generatedPlot__ = plot
        self.setModified()

    def getMaxPlotValue(self):
        return self.__maxPlotValue__

    def setMaxPlotValue(self, v):
        self.__maxPlotValue__ = v
        self.setModified()

    def getGradientPixels(self):
        if self.getMaxPlotValue()!=None:
            return self.getProjectSource().getGradientPixels(self.getMaxPlotValue()+1)
        return None

    def onProgress(self, generator, p):
        log.debug(function=self.onProgress, args=p)
        self.setProgress(p)

    def up(self):
        pass

    def generate(self):
        pass

    def getPreviewSize(self):
        w,h = self.getSize()
        l = w if w>h else h
        d=0.25
        while l*d>1000: d=d*0.1
        return (int(w*d), int(h*d))

    def prePreview(self, generator, **setup):
        generator.setup(**setup)

    async def preview(self, **setup):
        log.debug(function=self.preview, args=(setup))
        generator = self.getGenerator()
        if generator:
            self.prePreview(generator, **setup)
            generator.setup(size=self.getPreviewSize())
            await generator.generate()
            gradient = self.getProjectSource().getGradientPixels(generator.maxValue+1)
            self.setPreviewImage(core.fgen.getImage(self.getPreviewSize(), generator.plotValues, gradient))

    def getGenerator(self):
        return None

    def preGenerate(self, generator, **setup):
        generator.setup(**setup)

    def getFormattedImage(self):
        log.debug(function=self.getFormattedImage)
        borderSize = self.getBorderSize()
        p = self.getBorderColourPick()        
        pixels = self.getGradientPixels()
        try:
            plot = self.getGeneratedPlot()
        except:
            return None
        if pixels!=None and borderSize!=None and p!=None:
            borderColour = pixels[p] if p < len(pixels) else (0,0,0)
            fractalBox = ImageBox(ImageBox.ORIENTATION_HORIZONTAL, borderSize, borderSize, borderColour)
            fractalBox.addImage(core.fgen.getImage(self.getSize(), plot, pixels))
            return fractalBox.getImage()
        return None

    async def generate(self, progressHandler=None, **setup):
        log.debug(function=self.generate, args=(setup))
        generator = self.getGenerator()
        if generator:
            self.preGenerate(generator, **setup)
            self.setProgress(0)
            await generator.generate(progressHandler=self.onProgress if progressHandler==None else progressHandler)
            self.setMaxPlotValue(generator.maxValue)
            self.setGeneratedPlot(generator.plotValues)
            log.trace("generation complete")

    def getGeneratedImage(self):
        return self.getFormattedImage()

    def savePlots(self, storage):
        pass

    def loadPlots(self, storage):
        pass

    def toString(self):
        s =  self.getId() + ": " + self.__name
        return s

    def print(self):
        log.trace(self.toString())
