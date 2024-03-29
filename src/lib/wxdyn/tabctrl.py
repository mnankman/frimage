import wx
import wx.svg
import wx.lib.newevent as NE
import lib.wxdyn.log as log
import lib.wxdyn as wxdyn

TabSelectedEvent, EVT_TAB_SELECTED = NE.NewEvent()

class TabButton(wx.Panel):
    def __init__(self, parent, name, **kw):
        wx.Panel.__init__(self, parent, **kw)
        self.__mouseOver__ = False
        self.__selected__ = False
        self.__name__ = name
        self.__svg__ = None
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
        self.drawHighlight(dc)
        self.renderSVG(dc)

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

    def drawHighlight(self, dc):
        if self.__selected__:
            self.paintStyler.select("TabButton:highlight", dc)
            dc.DrawRectangle(0,0,2,self.Size.height)
        
    def onMouseEnter(self, event):
        self.__mouseOver__ = True
        self.Refresh(eraseBackground=False)
        event.Skip()

    def onMouseLeave(self, event):
        self.__mouseOver__ = False
        self.Refresh(eraseBackground=False)
        event.Skip()

    def OnMouseLeftDown(self, event):
        wx.PostEvent(self, TabSelectedEvent(nm=self.__name__))

class TabCtrl(wx.Panel):
    def __init__(self, parent, **kw):
        super(TabCtrl, self).__init__(parent, **kw)    
        self.tabs = {}
        self.styler = wxdyn.WindowStyler()
        self.styler.select("TabCtrl:normal", self)
        
        self.SetSize(self.GetParent().GetSize())
        self.sizer = wx.FlexGridSizer(1,2,0,0)
        self.SetSizer(self.sizer)
        self.tabsizer = wx.FlexGridSizer(20,1,5,0)
        self.pagepanel = wx.Panel(self)
        self.pagesizer = wx.BoxSizer(wx.VERTICAL)
        self.pagepanel.SetSizer(self.pagesizer)
        self.sizer.Add(self.tabsizer, 1)
        self.sizer.Add(self.pagepanel, 1)
        self.sizer.Layout()
        self.SetAutoLayout(True)
        self.Bind(wx.EVT_SIZE, self.onResize)

    def addTab(self, panel, label="", **kw):
        assert isinstance(panel, wx.Panel)
        panel.Reparent(self.pagepanel)
        nm = panel.GetName()
        if nm and len(nm)>0 and not nm in self.tabs:
            btn = TabButton(self, name=nm, size=(36, 36), style=wx.BORDER_NONE)
            btn.Bind(EVT_TAB_SELECTED, self.onTabSelect)
            self.tabsizer.Add(btn, 1)
            self.pagesizer.Add(panel)
            self.tabs[nm] = (panel, btn)
            self.setTabBitmaps(nm, **kw)
            panel.Hide()
        self.tabsizer.Layout()
        self.sizer.Layout()

    def setTabBitmaps(self, nm, **kw):
        log.debug(function=self.setTabBitmaps, args=(nm, kw))
        if nm in self.tabs:
            panel, btn = self.tabs[nm]
            for state, resource in kw.items():
                bmp=None
                if isinstance(resource, wx.Bitmap): bmp = resource
                if isinstance(resource, (wx.Image)): bmp = resource.ConvertToBitmap()
                if isinstance(resource, (wx.svg.SVGimage)): btn.setSVG(resource)
                if bmp:
                    if state=="normal": btn.SetBitmap(bmp)
                    elif state=="disabled": btn.SetBitmapDisabled(bmp)
                    elif state=="focus": btn.SetBitmapFocus(bmp)
                    elif state=="current": btn.SetBitmapCurrent(bmp)
                    elif state=="pressed": btn.SetBitmapPressed(bmp)

    def selectTab(self, name):
        for nm, tab in self.tabs.items():
            panel, btn = tab
            panel.Hide()
            btn.setSelected(False)
        self.tabs[name][0].Show()
        self.tabs[name][1].setSelected()
        self.Layout()

    def onTabSelect(self, e):
        nm = e.nm
        self.selectTab(nm)

    def onResize(self, e):
        e.Skip()
        pw, ph = self.GetParent().GetSize()
        self.pagepanel.SetSize(pw-2, ph-2)
        self.sizer.Layout()
