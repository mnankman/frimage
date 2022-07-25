#foreign
from PIL import Image
import numpy as np
import json

#local
from lib import log
from lib.modelobject import ModelObject
from lib.imgbox import ImageBox
import core.fgen

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


class GeneratedSet(ModelObject):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.area = Area(self)
        self.__name = name
        self.__generatedPlot__ = None
        self.__maxPlotValue = None
        self.__cachedImage__ = None
        self.__generatedSets__ = []
        self.persist("name")
        self.persist("maxPlotValue")

    def setName(self, name):
        self.__name = name
        self.setModified()

    def getName(self):
        return self.__name

    def getArea(self):
        return self.area

    def setArea(self, area):
        self.area.setAll(area)

    def getCachedImage(self):
        return self.__cachedImage__

    def setCachedImage(self, im):
        log.debug(function=self.setCachedImage, args=im)
        self.__cachedImage__ = im

    def getGeneratedPlot(self):
        try:
            if self.__generatedPlot__.any() == None: return None
        except AttributeError as ae:
            log.error(ae, function=self.getGeneratedPlot)
            return None
        except ValueError:
            return None
        return self.__generatedPlot__

    def setGeneratedPlot(self, plot):
        self.__generatedPlot__ = plot
        self.setModified()

    def getMaxPlotValue(self):
        return self.__maxPlotValue

    def setMaxPlotValue(self, v):
        self.__maxPlotValue = v
        self.setModified()

    def hasGeneratedPlot(self):
        return self.__maxPlotValue!=None

    def addGeneratedSet(self):
        newSet = self.newGeneratedSet()
        self.__generatedSets__.append(newSet)
        return newSet

    def newGeneratedSet(self):
        if isinstance(self.getParent(), GeneratedSet):
            nm = self.getName()
        else:
            nm = "step"
        newSet = self.__construct__(nm  + "_" + str(len(self.__generatedSets__)+1))
        return newSet

    def __construct__(self, nm):
        return GeneratedSet(self, nm)

    def getGeneratedSets(self):
        return self.__generatedSets__

    def getDepth(self, d=1):
        depth = d
        for s in self.__generatedSets__:
            sd = s.getDepth(d+1)
            depth = sd if sd>depth else depth
        return depth

    def getPlots(self):
        plots = {self.getName():self.getGeneratedPlot()}
        for gs in self.getGeneratedSets():
            plots.update(gs.getPlots())
        return plots

    def setPlots(self, plots):
        if self.getName() in plots.keys():
            self.setGeneratedPlot(plots[self.getName()])
        for gs in self.getGeneratedSets():
            gs.setPlots(plots)

    def savePlots(self, storage):
        path = storage.toPath("plots.npz", False)
        plots = self.getPlots()
        try:
            np.savez_compressed(path, **plots)
        except OSError as oe:
            log.error(oe, function=self.savePlots)
        except AttributeError as ae:
            log.error(ae, function=self.savePlots)
        finally:
            pass

    def loadPlots(self, storage):
        path = storage.toPath("plots.npz", False)
        try:
            plots = np.load(path)
            self.setPlots(plots)
        except OSError as oe:
            log.error(oe, function=self.loadPlots)
        except AttributeError as ae:
            log.error(ae, function=self.loadPlots)

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

    def getGeneratedImage(self):
        log.debug(function=self.getGeneratedImage)
        if self.currentSet == None: return None
        im = self.currentSet.getCachedImage()
        if im==None or self.getModified():
            im = self.getFormattedImage()
            self.currentSet.setCachedImage(im)
        return im

    def getGeneratedPlot(self):
        if self.currentSet == None: return None
        return self.currentSet.getGeneratedPlot()

    def setGeneratedPlot(self, plot):
        log.debug(function=self.setGeneratedPlot)
        assert self.currentSet != None
        self.currentSet.setGeneratedPlot(plot)
        self.currentSet.setCachedImage(self.getFormattedImage())
        self.setModified()

    def getMaxPlotValue(self):
        if self.currentSet == None: return None
        return self.currentSet.getMaxPlotValue()
        
    def setMaxPlotValue(self, v):
        assert self.currentSet != None
        self.currentSet.setMaxPlotValue(v)
        self.setModified()

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

    def getGenerator(self):
        return core.fgen.MandelbrotGenerator(self.getProjectSource().getSource())

    def preGenerate(self, generator, **setup):
        log.debug(function=self.preGenerate, args=setup)
        if setup!=None and "area" in setup.keys():
            areaRect = setup["area"]
        else:
            areaRect = self.currentSet.getArea().getRect()
        if areaRect!=None and self.currentSet.hasGeneratedPlot():
            genSet = self.currentSet.addGeneratedSet()
            genSet.getArea().setRect(areaRect)
            self.currentSet = genSet
        generator.setup(
            size=self.getSize(), 
            reverseColors=self.getProjectSource().getFlipGradient(), 
            area=self.currentSet.getArea().getAll()
        )

    def prePreview(self, generator, **setup):
        log.debug(function=self.prePreview, args=generator)
        generator.setup(
            reverseColors=self.getProjectSource().getFlipGradient(), 
            area=self.currentSet.getArea().getAll()
        )
    
    def saveThumbnail(self, storage):
        im = self.getRootSet().getCachedImage().copy()
        im.thumbnail((150,150))
        src = self.getProjectSource().getSourceImage()
        if src!=None:
            srcThumb = src.copy()
            srcThumb.thumbnail((50,50))
            im.paste(srcThumb, (5, 5))
        if im!=None:
            path = storage.toPath("thumbnail.png", False)
            try:
                im.save(path)
            except OSError as oe:
                log.error(oe, function=self.savePlots)
            except AttributeError as ae:
                log.error(ae, function=self.savePlots)
            finally:
                pass    

    def savePlots(self, storage):
        self.getProjectSource().saveSourceImage(storage)
        self.getRootSet().savePlots(storage)

    def loadPlots(self, storage):
        self.getRootSet().loadPlots(storage)

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

    def getGeneratedImage(self):
        log.debug(function=self.getGeneratedImage)
        if self.currentSet == None: return None
        im = self.currentSet.getCachedImage()
        if im==None:
            im = self.getFormattedImage()
            self.currentSet.setCachedImage(im)
        return im

    def getGeneratedPlot(self):
        if self.currentSet == None: return None
        return self.currentSet.getGeneratedPlot()

    def setGeneratedPlot(self, plot):
        log.debug(function=self.setGeneratedPlot)
        assert self.currentSet != None
        self.currentSet.setGeneratedPlot(plot)
        self.currentSet.setCachedImage(self.getFormattedImage())
        self.setModified()

    def getMaxPlotValue(self):
        if self.currentSet == None: return None
        return self.currentSet.getMaxPlotValue()
        
    def setMaxPlotValue(self, v):
        assert self.currentSet != None
        self.currentSet.setMaxPlotValue(v)
        self.setModified()

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

    def getGenerator(self):
        return core.fgen.JuliaGenerator(self.getProjectSource().getSource())

    def preGenerate(self, generator, **setup):
        log.debug(function=self.preGenerate, args=setup)
        if setup!=None and "area" in setup.keys():
            areaRect = setup["area"]
        else:
            areaRect = self.currentSet.getArea().getRect()
        cxy = self.currentSet.getCxy().getCxy()
        if areaRect!=None and self.currentSet.hasGeneratedPlot():
            genSet = self.currentSet.addGeneratedJuliaSet()
            genSet.getArea().setRect(areaRect)
            genSet.getCxy().setCxy(cxy)
            self.currentSet = genSet
        generator.setup(
            size=self.getSize(), 
            reverseColors=self.getProjectSource().getFlipGradient(), 
            area=self.currentSet.getArea().getAll(),
            cxy=self.currentSet.getCxy().getCxy()
        )
    
    def prePreview(self, generator, **setup):
        log.debug(function=self.prePreview, args=generator)
        generator.setup(
            reverseColors=self.getProjectSource().getFlipGradient(), 
            area=self.currentSet.getArea().getAll(),
            cxy=self.currentSet.getCxy().getCxy()
        )
    
    def saveThumbnail(self, storage):
        im = self.getRootSet().getCachedImage().copy()
        im.thumbnail((150,150))
        src = self.getProjectSource().getSourceImage()
        if src!=None:
            srcThumb = src.copy()
            srcThumb.thumbnail((50,50))
            im.paste(srcThumb, (5, 5))
        if im!=None:
            path = storage.toPath("thumbnail.png", False)
            try:
                im.save(path)
            except OSError as oe:
                log.error(oe, function=self.savePlots)
            except AttributeError as ae:
                log.error(ae, function=self.savePlots)
            finally:
                pass    

    def savePlots(self, storage):
        self.getProjectSource().saveSourceImage(storage)
        self.getRootSet().savePlots(storage)

    def loadPlots(self, storage):
        self.getRootSet().loadPlots(storage)
