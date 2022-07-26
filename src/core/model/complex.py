#foreign
import numpy as np

#project
from lib import log
from lib.modelobject import ModelObject
import core.fgen
from .project import Project

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

#TODO: implement base class ComplexProject where MandelbrotProject and JuliaProject inherit from

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
        src = self.getProjectSource().getSourceImage()
        cache = self.getRootSet().getCachedImage()
        if cache:
            im = cache.copy()
            im.thumbnail((150,150))
            if src:
                srcThumb = src.copy()
                srcThumb.thumbnail((50,50))
                im.paste(srcThumb, (5, 5))
        elif src:
            im = src.copy()
            im.thumbnail((150,150))
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
        src = self.getProjectSource().getSourceImage()
        cache = self.getRootSet().getCachedImage()
        if cache:
            im = cache.copy()
            im.thumbnail((150,150))
            if src:
                srcThumb = src.copy()
                srcThumb.thumbnail((50,50))
                im.paste(srcThumb, (5, 5))
        elif src:
            im = src.copy()
            im.thumbnail((150,150))
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

