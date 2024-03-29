import wx
import wx.lib.newevent as NE
from PIL import Image

import lib.wxdyn.log as  log
from core.model import Project 
import lib.wxdyn as wxd

ImageUpdatedEvent, EVT_IMAGE_UPDATED = NE.NewEvent()
ZoomAreaEvent, EVT_ZOOM_AREA = NE.NewEvent()
DiveDownEvent, EVT_DIVEDOWN = NE.NewEvent()

ZOOM_FACTOR_VALUES = [0.05, 0.1, 0.2, 0.25, 0.5, 0.8]

MODE_ZOOM = 0
MODE_FINISH = 1
VALID_MODES = [MODE_ZOOM, MODE_FINISH]

class ZoomPanel(wxd.DynamicCtrl, wx.Panel):
    def __init__(self, parent, modelObject, attributeName, **kw):
        wxd.DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.Panel.__init__(self, parent, **kw)
        self.__mode__ = MODE_ZOOM
        self.__areaRect__ = self.modelObject.getArea().getRect()
        self.__scaleFactor__ = 2
        self.__scaleToFit__ = False
        self.__zoomRect__ = None
        self.__imgFitSize__ = None
        self.__mouseOver__ = False
        self.__genSetUnderMouseCursor__ = None
        self.__SourceImageStamp__ = None
        self.setImage(modelObject.getAttribute(self.attributeName))
        self.Bind(wx.EVT_PAINT,self.onPaint)
        self.Bind(wx.EVT_SIZE, self.onResize)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        self.Bind(wx.EVT_MOTION,  self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.SetAutoLayout(True)

 # ------- METHODS FOR GETTING AND SETTING VALUES -------

    def setImage(self, pilImg):
        if pilImg!=None:
            self.__pilImage__ = pilImg
        elif isinstance(self.modelObject, Project):
            self.__pilImage__ = Image.new("RGB", self.modelObject.getSize())  
        else:
            self.__pilImage__ = Image.new("RGB", self.GetSize())
        try:
            self.SetSize(self.__pilImage__.size)
            self.Refresh()
            wx.PostEvent(self, ImageUpdatedEvent())
        except:
            pass

    def getImage(self):
        return self.__pilImage__

    def getScaleToFit(self):
        return self.__scaleToFit__

    def setScaleToFit(self, v):
        self.__scaleToFit__ = v
        self.Refresh()

    def getImageFitSize(self):
        return self.__pilImage__.size if not self.__scaleToFit__ else self.__imgFitSize__

    def getImageFitPos(self):
        return (0,0)
        
    def getImageFitRect(self):
        ix,iy = self.getImageFitPos()
        iw,ih = self.getImageFitSize()
        return (ix,iy,iw,ih)

    def getArea(self):
        assert isinstance(self.modelObject, Project)
        return self.modelObject.getArea()
        
    def setAreaRect(self, rect):
        self.getArea().setRect(self.calcSelectedAreaRect())
        
    def getZoomScale(self):
        return ZOOM_FACTOR_VALUES[self.__scaleFactor__]

    def getZoomRect(self, imsize):
        mx,my = self.ScreenToClient(wx.GetMousePosition())
        iw,ih = imsize
        rw,rh = (iw*self.getZoomScale(), ih*self.getZoomScale())
        rx = mx-(rw/2) if mx>(rw/2) else 0
        ry = my-(rh/2) if my>(rh/2) else 0
        rx = rx if rx+rw<iw else iw-rw
        ry = ry if ry+rh<ih else ih-rh
        return (rx,ry,rw,rh)

    def getGenerationSetUnderMouse(self):
        mx,my = self.ScreenToClient(wx.GetMousePosition())
        sets = self.modelObject.getCurrentSet().getGeneratedSets()
        for s in sets:
            areaRect = s.getArea().getRect()
            if areaRect!=None:
                rx,ry,rw,rh = self.areaRectToClientRect(s.getArea().getRect())  
                if mx>rx and my>ry and mx<rx+rw-1 and my<ry+rh-1:
                    return s      
        return None

    def setMode(self, m=MODE_ZOOM):
        if m in VALID_MODES:
            self.__mode__ = m

    def spinZoomScale(self, rotation=0):
        log.debug(function=self.spinZoomScale, args=rotation)
        max = len(ZOOM_FACTOR_VALUES)
        cur = self.__scaleFactor__
        r=1
        if rotation<0:
            self.__scaleFactor__ = 0 if cur-r<0 else cur-r
        else:
            self.__scaleFactor__ = max-r if cur+r>=max else cur+r
        self.Refresh(eraseBackground=False)

# ------- METHODS FOR HANDLING EVENTS -------

    def onModelObjectChange(self, payload):
        #if "modified" in payload: return
        obj = payload["object"]
        assert isinstance(obj, wxd.ModelObject)
        log.debug(function=self.onModelObjectChange, args=obj.getFullId())
        if "modified" in payload:
            mods = obj.getModificationsFromPayload(payload)
            log.debug(var=("modifications in payload", mods), function=self.onModelObjectChange)
        pilImg = obj.getAttribute(self.attributeName)
        if pilImg != self.getImage():
            self.setImage(pilImg)
            self.__areaRect__ = self.modelObject.getArea().getRect()
            self.__zoomRect__ = None
            self.__imgFitSize__ = None
        
    def onResize(self, e):
        e.Skip()
        pw, ph = self.GetParent().GetSize()
        self.SetSize(pw-2, ph-2)
        self.Refresh(rect=(0,0,pw,ph))

    def onMouseEnter(self, event):
        self.__mouseOver__ = True
        self.Refresh(eraseBackground=False)
        event.Skip()

    def onMouseLeave(self, event):
        self.__mouseOver__ = False
        self.Refresh(eraseBackground=False)
        event.Skip()

    def OnMouseMove(self, event):
        self.__genSetUnderMouseCursor__ = self.getGenerationSetUnderMouse()
        self.Refresh(eraseBackground=False)
        event.Skip()

    def OnMouseLeftDown(self, e):
        if self.__mode__ == MODE_ZOOM:
            if self.__genSetUnderMouseCursor__!=None:
                wx.PostEvent(self, DiveDownEvent(set=self.__genSetUnderMouseCursor__))
        elif self.__mode__ == MODE_FINISH:
            x,y,w,h = self.__zoomRect__
            fw,fh = self.calcImageFitSize(self.modelObject.getProjectSource().getSourceImage(), (w, h))
            self.__SourceImageStamp__ = x,y,fw,fh
            self.Refresh(eraseBackground=False)
            pass
        e.Skip()

    def OnMouseRightDown(self, e):
        if self.__mode__ == MODE_ZOOM:
            wx.PostEvent(self, ZoomAreaEvent(area=self.calcSelectedAreaRect()))
        elif self.__mode__ == MODE_FINISH:
            self.__SourceImageStamp__ = None
            self.Refresh(eraseBackground=False)
            pass
        e.Skip()

    def OnMouseWheel(self, e):
        self.spinZoomScale(e.GetWheelRotation())
        e.Skip()

 # ------- CALCULATION METHODS -------

    # calculates the fractal area that corresponds with the selected rectangle
    def calcSelectedAreaRect(self):
        return self.clientRectToAreaRect(self.__zoomRect__)

    def clientRectToAreaRect(self, clientRect):
        ax,ay,aw,ah = self.__areaRect__
        zrx,zry,zrw,zrh = clientRect
        iw,ih = self.getImageFitSize()
        sx = zrx/iw
        sy = zry/ih
        sw = aw*self.getZoomScale()
        sh = ah*self.getZoomScale()
        nx = ax+sx*aw
        ny = ay+sy*ah
        return (nx, ny, sw, sh)

    def areaRectToClientRect(self, areaRect):
        if areaRect == None: return None
        ax1,ay1,aw1,ah1 = self.__areaRect__ # current area rect
        ax2,ay2,aw2,ah2 = areaRect
        scale = ah2/ah1
        iw,ih = self.getImageFitSize()
        rw=iw*scale
        rh=ih*scale
        rx=iw*(ax2-ax1)/aw1
        ry=ih*(ay2-ay1)/ah1
        return (rx, ry, rw, rh)

    # calculates largest fit while maintaining aspect ratio of the image
    def calcImageFitSize(self, pilImg, targetSize):
        tw,th = targetSize
        sw,sh = pilImg.size
        tr = tw/th
        sr = sw/sh
        return (int(tw), int(tw/sr)) if sr>tr else (int(th*sr), int(th))

# ------- METHODS FOR DRAWING THE CONTENTS -------

    def onPaint(self, event):
        event.Skip()
        im = self.getImage()
        self.__imgFitSize__ = self.calcImageFitSize(im, self.GetSize())
        dc = wx.PaintDC(self)
        self.paintStyler.select("ZoomPanel:normal", dc)
        imr = im.resize(self.__imgFitSize__) if self.__scaleToFit__ else im.copy()
        ix,iy = self.getImageFitPos()
        dc.DrawBitmap(self.pilImageToBitmap(imr), ix, iy)
        self.drawImageSizeTxt(dc)
        self.drawGenerationSetAreas(dc)
        self.drawSourceImageStamp(dc)
        if self.__mouseOver__:
            self.__zoomRect__ = self.getZoomRect(imr.size)
            if self.__mode__ == MODE_ZOOM:
                self.drawZoomRect(dc)
                self.drawZoomRectTxt(dc)
            elif self.__mode__ == MODE_FINISH:
                self.drawSourceImage(dc)

    def drawImageSizeTxt(self, dc):
        self.paintStyler.select("ZoomPanel:normal", dc)
        ix,iy,iw,ih = self.getImageFitRect()
        txt = str(self.getImageFitSize())
        tw,th = dc.GetTextExtent(txt)
        dc.DrawText(txt, ix+iw-tw, iy+ih-th)

    def drawZoomRectTxt(self, dc):
        self.paintStyler.select("ZoomPanel:normal", dc)
        ix,iy,iw,ih = self.getImageFitRect()
        rx,ry,rw,rh = self.__zoomRect__
        txt = str((int(rx),int(ry),int(rx+rw),int(ry+rh)))
        tw,th = dc.GetTextExtent(txt)
        dc.DrawText(txt, ix, iy+ih-th)

    def drawZoomRect(self, dc):
        self.paintStyler.select("ZoomPanel:normal", dc)
        dc.SetBrush(wx.Brush("#000000", style=wx.BRUSHSTYLE_TRANSPARENT))
        rx,ry,rw,rh = self.__zoomRect__
        dc.DrawRectangle(rx, ry, rw, rh)
        txt = str(1/self.getZoomScale())
        tw,th = dc.GetTextExtent(txt)
        dc.DrawText(txt, rx+rw-tw-2, ry+rh-th-2)

    def drawGenerationSetAreas(self, dc):
        self.paintStyler.select("ZoomPanel:normal", dc)
        dc.SetBrush(wx.Brush("#000000", style=wx.BRUSHSTYLE_TRANSPARENT))
        sets = self.modelObject.getCurrentSet().getGeneratedSets()
        for s in sets:
            if s==self.__genSetUnderMouseCursor__:
                dc.SetPen(wx.Pen("#00ffff", width=3, style=wx.PENSTYLE_SOLID))
            else:
                dc.SetPen(wx.Pen("#00ffff", style=wx.PENSTYLE_DOT))
            areaRect = self.areaRectToClientRect(s.getArea().getRect())
            if areaRect!=None: dc.DrawRectangle(*areaRect)
            txt = str(s.getDepth())
            tw,th = dc.GetTextExtent(txt)
            rx,ry,rw,rh = areaRect
            dc.DrawText(txt, rx+rw-tw-2, ry+rh-th-2)

    def drawSourceImage(self, dc):
        self.paintStyler.select("ZoomPanel:normal", dc)
        dc.SetBrush(wx.Brush("#000000", style=wx.BRUSHSTYLE_TRANSPARENT))
        rx,ry,rw,rh = self.__zoomRect__
        im = self.modelObject.getProjectSource().getSourceImage()
        if im!=None:
            imr = im.resize(self.calcImageFitSize(im, (rw,rh)))
            dc.DrawBitmap(self.pilImageToBitmap(imr), rx, ry)
            dc.DrawRectangle(rx, ry, *imr.size)

    def drawSourceImageStamp(self, dc):
        if self.__SourceImageStamp__!=None:
            x,y,w,h = self.__SourceImageStamp__
            im = self.modelObject.getProjectSource().getSourceImage()
            if im!=None:
                imr = im.resize(self.calcImageFitSize(im, (w,h)))
                dc.DrawBitmap(self.pilImageToBitmap(imr), x, y)

# ------- METHODS FOR CONVERTING IMAGES -------

    def pilImageToWxImage(self, pilImg):
        if pilImg==None: return None
        wxImage = wx.Image(pilImg.size)
        wxImage.SetData(pilImg.convert('RGB').tobytes())
        wxImage.SetAlpha(pilImg.convert("RGBA").tobytes()[3::4])
        return wxImage

    def pilImageToBitmap(self, pilImg):
        return self.pilImageToWxImage(pilImg).ConvertToBitmap()

    def saveImage(self, path):
        im = self.__pilImage__
        if self.__SourceImageStamp__!=None:
            x,y,w,h = self.__SourceImageStamp__
            srcIm = self.modelObject.getProjectSource().getSourceImage()
            if srcIm!=None:
                srcIm = srcIm.resize(self.calcImageFitSize(srcIm, (w,h)))
                im = self.__pilImage__.copy()
                im.paste(srcIm, (int(x),int(y)))
                im.save(path)
        else:
            self.__pilImage__.save(path)
