import wx
from lib.modelobject import ModelObject
import base.model
from PIL import Image, ImageDraw
from lib import log

class DynamicCtrl:
    def __init__(self, modelObject, attributeName):
        assert modelObject!=None
        assert isinstance(modelObject, ModelObject)
        assert attributeName!=None
        assert modelObject.hasAttribute(attributeName)
        self.modelObject = modelObject
        self.attributeName = attributeName
        self.modelObject.subscribe(self, "msg_object_modified", self.onModelObjectChange)

    def onUserValueChange(self, e):
        ctrl = e.GetEventObject()
        val = ctrl.GetValue()
        self.modelObject.setAttribute(self.attributeName, val)
        e.Skip()

    def onModelObjectChange(self, payload):
        pass

class DynamicTextCtrl(DynamicCtrl, wx.TextCtrl):
    def __init__(self, parent, modelObject, attributeName, styles, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.TextCtrl.__init__(self, parent, **kw)
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])
        self.SetValue(str(modelObject.getAttribute(self.attributeName)))
        self.Bind(wx.EVT_TEXT, self.onUserValueChange) 

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.ChangeValue(str(obj.getAttribute(self.attributeName)))

class DynamicSpinCtrl(DynamicCtrl, wx.SpinCtrl):
    def __init__(self, parent, modelObject, attributeName, styles, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.SpinCtrl.__init__(self, parent, **kw)
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])
        self.SetValue(str(modelObject.getAttribute(self.attributeName)))
        self.Bind(wx.EVT_SPINCTRL, self.onUserValueChange) 

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.SetValue(str(obj.getAttribute(self.attributeName)))

class DynamicCheckBox(DynamicCtrl, wx.CheckBox):
    def __init__(self, parent, modelObject, attributeName, styles, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.CheckBox.__init__(self, parent, **kw)
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])
        self.SetValue(modelObject.getAttribute(self.attributeName))
        self.Bind(wx.EVT_CHECKBOX, self.onUserValueChange) 

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.SetValue(obj.getAttribute(self.attributeName))

class DynamicBitmap(DynamicCtrl, wx.StaticBitmap):
    def __init__(self, parent, modelObject, attributeName, styles, autoSize=True, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.StaticBitmap.__init__(self, parent, **kw)
        self.autoSize = autoSize
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])
        self.setBitmap(modelObject.getAttribute(self.attributeName), self.GetSize())

    def pilImageToWxImage(self, pilImg):
        wxImage = wx.Image(pilImg.size)
        wxImage.SetData(pilImg.convert('RGB').tobytes())
        wxImage.SetAlpha(pilImg.convert("RGBA").tobytes()[3::4])
        return wxImage

    def createEmptyWxImage(self):
        return wx.Image(self.GetSize())

    def setBitmap(self, pilImg, size=None):
        log.debug(function=self.setBitmap, args=(pilImg, size))
        if pilImg!=None:
            if size!=None and self.autoSize: 
                im = pilImg.resize(size, Image.BOX)
            else:
                im = pilImg
            wxImg = self.pilImageToWxImage(im)
        else:
            wxImg = self.createEmptyWxImage()
        self.SetBitmap(wxImg.ConvertToBitmap())
        self.Refresh()

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.setBitmap(obj.getAttribute(self.attributeName), self.GetSize())


class DynamicProgressIndicator(DynamicCtrl, wx.Panel):
    def __init__(self, parent, modelObject, attributeName, styles, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.Panel.__init__(self, parent, **kw)
        self.progress=0
        self.Bind(wx.EVT_PAINT,self.onPaint)

    def setProgress(self, p):
        log.debug(function=self.setProgress, args=p)
        self.progress=p
        w,h=self.GetSize()
        self.Refresh(rect=(0,0,w,h))

    def onModelObjectChange(self, payload):
        log.debug(function=self.onModelObjectChange, args=payload)
        if "modified" in payload: return
        obj = payload["object"]
        progress = obj.getAttribute(self.attributeName)
        self.setProgress(progress)

    def onPaint(self, event):
        event.Skip()
        self.paint()

    def paint(self):
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen("#00ff00"))
        dc.SetBrush(wx.Brush("#00ff00", style=wx.BRUSHSTYLE_SOLID))
        w,h = self.GetSize()
        p = self.progress
        dc.DrawRectangle(0, 0, w*(p/100), h)
        txt = str(p)+"%"
        tw,th = dc.GetTextExtent(txt)
        tx,ty = (0.5*(w-tw), 0.5*(h-th))
        dc.DrawText(txt, tx, ty)

ZoomAreaEvent, EVT_ZOOM_AREA = wx.lib.newevent.NewEvent()

class ImageZoomPanel(DynamicCtrl, wx.Panel):
    def __init__(self, parent, modelObject, attributeName, styles, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.Panel.__init__(self, parent, **kw)
        self.areaRect = self.modelObject.getArea().getRect()
        self.zoomRectScale = 0.2
        self.zoomRect = None
        self.selectedRect = None
        self.imageFitSize = None
        self.__mouseOver__ = False
        self.mouseMoves = 0
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])
        self.setImage(modelObject.getAttribute(self.attributeName))
        self.Bind(wx.EVT_PAINT,self.onPaint)
        self.Bind(wx.EVT_SIZE, self.onResize)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        self.Bind(wx.EVT_MOTION,  self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        self.SetAutoLayout(True)

    def pilImageToWxImage(self, pilImg):
        if pilImg==None: return None
        wxImage = wx.Image(pilImg.size)
        wxImage.SetData(pilImg.convert('RGB').tobytes())
        wxImage.SetAlpha(pilImg.convert("RGBA").tobytes()[3::4])
        return wxImage

    def pilImageToBitmap(self, pilImg):
        return self.pilImageToWxImage(pilImg).ConvertToBitmap()

    def setImage(self, pilImg):
        if pilImg!=None:
            self.pilImage = pilImg
        elif isinstance(self.modelObject, base.model.Project):
            self.pilImage = Image.new("RGB", self.modelObject.getSize())  
        else:
            self.pilImage = Image.new("RGB", self.GetSize())
        self.Refresh()

    def _setImage(self, wxImg):
        self.image = wxImg
        if wxImg!=None:
            self.image = wxImg
        else:
            self.image = wx.Image(self.GetSize())
        self.Refresh()

    def onModelObjectChange(self, payload):
        if "modified" in payload: return
        obj = payload["object"]
        pilImg = obj.getAttribute(self.attributeName)
        self.setImage(pilImg)
        self.areaRect = self.modelObject.getArea().getRect()
        self.selectedRect = None
        self.zoomRect = None
        self.imageFitSize = None
        
    def onResize(self, e):
        e.Skip()
        pw, ph = self.GetParent().GetSize()
        self.SetSize(pw-2, ph-2)
        self.Refresh(rect=(0,0,pw,ph))

    def calcImageFitSize(self, pilImg, targetSize):
        # calculates largest fit while maintaining aspect ratio of the image
        tw,th = targetSize 
        cw,ch = pilImg.size
        l = cw if cw>ch else ch         # longest edge
        f = tw/l if tw<th else th/l     # resize factor
        s = (int(cw*f), int(ch*f))
        #log.debug(function=self.calcImageFitSize, args=(pilImg.size, targetSize), returns=(l,f,s))
        return s

    def getZoomRect(self, im):
        mx,my = self.ScreenToClient(wx.GetMousePosition())
        iw,ih = im.size
        rw,rh = (iw*self.zoomRectScale, ih*self.zoomRectScale)
        rx = mx-(rw/2) if mx>(rw/2) else 0
        ry = my-(rh/2) if my>(rh/2) else 0
        rx = rx if rx+rw<iw else iw-rw
        ry = ry if ry+rh<ih else ih-rh
        return (rx,ry,rw,rh)

    def onPaint(self, event):
        event.Skip()
        #im = self.drawSelectedRectInImage(self.pilImage)
        im = self.pilImage
        self.imageFitSize = self.calcImageFitSize(im, self.GetSize())
        dc = wx.PaintDC(self)
        imr = im.resize(self.imageFitSize)
        dc.DrawBitmap(self.pilImageToBitmap(imr), 0, 0)
        self.drawImageSize(dc)
        if self.__mouseOver__:
            self.zoomRect = self.getZoomRect(imr)
            self.drawZoomRect(dc)

    def drawImageSize(self, dc):
        dc.SetPen(wx.Pen("#ffffff"))
        dc.SetBrush(wx.Brush("#0000FF", style=wx.BRUSHSTYLE_SOLID))
        txt = str(self.imageFitSize)
        tw,th = dc.GetTextExtent(txt)
        w,h = self.GetSize()
        iw,ih = self.imageFitSize
        dc.DrawText(txt, iw-tw, h-th)

    def drawZoomRect(self, dc):
        dc.SetPen(wx.Pen("#ffffff"))
        dc.SetBrush(wx.Brush("#000000", style=wx.BRUSHSTYLE_TRANSPARENT))
        rx,ry,rw,rh = self.zoomRect
        dc.DrawRectangle(rx, ry, rw, rh)
        txt = str((rx,ry,rx+rw,ry+rh))
        tw,th = dc.GetTextExtent(txt)
        w,h = self.GetSize()
        dc.SetBrush(wx.Brush("#0000FF", style=wx.BRUSHSTYLE_SOLID))
        dc.DrawText(txt, 0, h-th)

    def drawSelectedRectInImage(self, pilImg):
        im = pilImg.copy()
        iw,ih = im.size
        nw,nh = self.calcImageFitSize(im, self.GetSize())
        if self.selectedRect!=None:
            draw = ImageDraw.Draw(im)
            x,y,w,h = self.selectedRect
            x1=x*iw/nw
            y1=y*ih/nh
            x2=x1+w
            y2=y1+h
            draw.rectangle([x1,y1,x2,y2], outline=(255,255,0))
        return im
 
    def calcSelectedAreaRect(self):
        ax,ay,aw,ah = self.areaRect
        log.debug("current fractal area (as rect): ", (ax,ay,aw,ah))
        
        zrx,zry,zrw,zrh = self.zoomRect
        log.debug("zoomrect: ", (zrx,zry,zrw,zrh))

        iw,ih = self.imageFitSize
        log.debug("image fit size:", self.imageFitSize) 

        sx = zrx/iw
        sy = zry/ih
        sw = aw*self.zoomRectScale
        sh = ah*self.zoomRectScale
        log.debug("selected rect (relative to image dimensions): ", (sx,sy,sw,sh))

        nx = ax+sx*aw
        ny = ay+sy*ah

        newArea = (nx, ny, sw, sh)
        log.debug("new fractal area (as rect): ", newArea)
        return newArea

    def onMouseEnter(self, event):
        self.__mouseOver__ = True
        self.Refresh()
        event.Skip()

    def onMouseLeave(self, event):
        self.__mouseOver__ = False
        self.Refresh()
        event.Skip()

    def OnMouseMove(self, event):
        self.mouseMoves+=1
        if self.mouseMoves % 5 == 0:
            self.Refresh()
        event.Skip()

    def OnMouseLeftDown(self, e):
        self.modelObject.getArea().setRect(self.calcSelectedAreaRect())
        self.selectedRect = self.getZoomRect(self.pilImage)
        e.Skip()

    def OnMouseRightDown(self, e):
        log.debug(function=self.OnMouseRightDown)
        wx.PostEvent(self, ZoomAreaEvent(obj=self))
