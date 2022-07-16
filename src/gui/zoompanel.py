import wx
import base.model
from PIL import Image, ImageDraw
from lib import log
import gui.dynctrl as dynctrl

ZoomAreaEvent, EVT_ZOOM_AREA = wx.lib.newevent.NewEvent()

ZOOM_SCALE_VALUES = [0.05, 0.1, 0.2, 0.25, 0.5, 0.8]

MODE_ZOOM = 0
MODE_FINISH = 1
VALID_MODES = [MODE_ZOOM, MODE_FINISH]

class ZoomPanel(dynctrl.DynamicCtrl, wx.Panel):
    def __init__(self, parent, modelObject, attributeName, styles, **kw):
        dynctrl.DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.Panel.__init__(self, parent, **kw)
        self.mode = MODE_ZOOM
        self.areaRect = self.modelObject.getArea().getRect()
        self.zoomRectScale = 2
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
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.SetAutoLayout(True)

    def pilImageToWxImage(self, pilImg):
        if pilImg==None: return None
        wxImage = wx.Image(pilImg.size)
        wxImage.SetData(pilImg.convert('RGB').tobytes())
        wxImage.SetAlpha(pilImg.convert("RGBA").tobytes()[3::4])
        return wxImage

    def pilImageToBitmap(self, pilImg):
        return self.pilImageToWxImage(pilImg).ConvertToBitmap()

    def setMode(self, m=MODE_ZOOM):
        if m in VALID_MODES:
            self.mode = m

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

    def getZoomScale(self):
        return ZOOM_SCALE_VALUES[self.zoomRectScale]

    def spinZoomScale(self, rotation=0):
        log.debug(function=self.spinZoomScale, args=rotation)
        max = len(ZOOM_SCALE_VALUES)
        cur = self.zoomRectScale
        r=1
        if rotation<0:
            self.zoomRectScale = 0 if cur-r<0 else cur-r
        else:
            self.zoomRectScale = max-r if cur+r>=max else cur+r
        self.Refresh(eraseBackground=False)
        
    def getZoomRect(self, imsize):
        mx,my = self.ScreenToClient(wx.GetMousePosition())
        iw,ih = imsize
        rw,rh = (iw*self.getZoomScale(), ih*self.getZoomScale())
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
            self.zoomRect = self.getZoomRect(imr.size)
            if self.mode == MODE_ZOOM:
                self.drawZoomRect(dc)
            elif self.mode == MODE_FINISH:
                self.drawSourceImage(dc)

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

        txt1 = str(1/self.getZoomScale())
        tw,th = dc.GetTextExtent(txt1)
        dc.DrawText(txt1, rx+rw-tw-2, ry+rh-th-2)

        txt2 = str((int(rx),int(ry),int(rx+rw),int(ry+rh)))
        tw,th = dc.GetTextExtent(txt2)
        w,h = self.GetSize()
        dc.DrawText(txt2, 0, h-th)

    def drawSourceImage(self, dc):
        rx,ry,rw,rh = self.zoomRect
        dc.DrawRectangle(rx, ry, rw, rh)
        im = self.modelObject.getProjectSource().getSourceImage()
        imr = im.resize(self.calcImageFitSize(im, (rw,rh)))
        dc.DrawBitmap(self.pilImageToBitmap(imr), rx, ry)

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
        sw = aw*self.getZoomScale()
        sh = ah*self.getZoomScale()
        log.debug("selected rect (relative to image dimensions): ", (sx,sy,sw,sh))

        nx = ax+sx*aw
        ny = ay+sy*ah

        newArea = (nx, ny, sw, sh)
        log.debug("new fractal area (as rect): ", newArea)
        return newArea

    def getMouseMovement(self):
        x0, y0 = self.mousePos
        x, y = self.ScreenToClient(wx.GetMousePosition())
        return (x, y, x-x0, y-y0)

    def onMouseEnter(self, event):
        self.__mouseOver__ = True
        self.mousePos = self.ScreenToClient(wx.GetMousePosition())
        self.Refresh(eraseBackground=False)
        event.Skip()

    def onMouseLeave(self, event):
        self.__mouseOver__ = False
        self.Refresh(eraseBackground=False)
        event.Skip()

    def OnMouseMove(self, event):
        x,y,dx,dy=self.getMouseMovement()
        self.mousePos = (x,y)
        self.Refresh(eraseBackground=False)
        event.Skip()

    def OnMouseLeftDown(self, e):
        if self.mode == MODE_ZOOM:
            self.modelObject.getArea().setRect(self.calcSelectedAreaRect())
            self.selectedRect = self.getZoomRect(self.pilImage.size)
        elif self.mode == MODE_FINISH:
            pass
        e.Skip()

    def OnMouseRightDown(self, e):
        if self.mode == MODE_ZOOM:
            self.modelObject.getArea().setRect(self.calcSelectedAreaRect())
            self.selectedRect = self.getZoomRect(self.pilImage.size)
            wx.PostEvent(self, ZoomAreaEvent(obj=self))
        e.Skip()

    def OnMouseWheel(self, e):
        self.spinZoomScale(e.GetWheelRotation())
        e.Skip()
