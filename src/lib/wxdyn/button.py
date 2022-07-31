import wx
import wx.svg
import wx.lib.newevent as NE
import lib.wxdyn.log as log
import lib.wxdyn as wxdyn

ButtonPressedEvent, EVT_BUTTON_PRESSED = NE.NewEvent()

class Button(wx.Panel):
    def __init__(self, parent, **kw):
        self.__mouseOver__ = False
        self.__selected__ = False
        self.__svg__ = None
        panelkw = {}
        for k,v in kw.items():
            if k=="label":
                self.__label__ = v
            elif k=="svg":
                self.__svg__ = v
            else:
                panelkw[k] = v
        wx.Panel.__init__(self, parent, **panelkw)
        self.Bind(wx.EVT_PAINT,self.onPaint)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.paintStyler = wxdyn.PaintStyler()

    def setSelected(self, selected=True):
        self.__selected__ = selected       
        self.Refresh(eraseBackground=False)

    def setSVG(self, svg: wx.svg.SVGimage):
        self.__svg__ = svg
        self.Refresh(eraseBackground=False)
        
    def onPaint(self, event):
        event.Skip()
        dc = wx.PaintDC(self)
        self.drawBackground(dc)
        self.drawLabel(dc)
        self.renderSVG(dc)

    def drawLabel(self, dc):
        if self.__label__:
            self.paintStyler.select("Button:normal", dc)
            w,h = self.GetSize()
            tw,th = dc.GetTextExtent(self.__label__)
            x = int((w-tw)/2)
            y = int((h-th)/2)
            dc.DrawText(self.__label__, x, y)

    def renderSVG(self, dc):
        if self.__svg__:
            dcdim = min(self.Size.width, self.Size.height)
            imgdim = min(self.__svg__.width, self.__svg__.height)
            scale = dcdim / imgdim
            dc.SetDeviceOrigin(3, 3)
            gc = wx.GraphicsContext.Create(dc)
            self.__svg__.RenderToGC(gc, 0.8*scale)

    def drawBackground(self, dc):
        w,h = self.GetSize()
        if self.__selected__:
            self.paintStyler.select("Button:selected", dc)
        elif self.__mouseOver__:
            self.paintStyler.select("Button:mouseOver", dc)
        else:
            self.paintStyler.select("Button:normal", dc)
        dc.DrawRectangle((0, 0, w, h))

    def onMouseEnter(self, event):
        self.__mouseOver__ = True
        self.Refresh(eraseBackground=False)
        event.Skip()

    def onMouseLeave(self, event):
        self.__mouseOver__ = False
        self.Refresh(eraseBackground=False)
        event.Skip()

    def OnMouseLeftDown(self, event):
        wx.PostEvent(self, ButtonPressedEvent())
