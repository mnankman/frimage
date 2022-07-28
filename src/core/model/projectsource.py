#foreign
from PIL import Image

#project
from lib import log
import lib.wxdyn as wxd
import core.fgen

class ProjectSource(wxd.ModelObject):
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
        self.setSource(core.fgen.Source(None, self.getHeatmapBaseImageSize()))

    def getPath(self):
        return self.__path
    
    def setPath(self, path):
        self.__path = path
        im = Image.open(self.__path)
        self.setSource(core.fgen.Source(im.convert('RGB'), self.getHeatmapBaseImageSize()))

    def setSource(self, source):
        self.__source = source
        self.setSourceImage(source.getSourceImage())
        self.setHeatmapBaseImage(source.getHeatmapBaseImage())
        self.setGradientImage(source.getGradientImage())

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
