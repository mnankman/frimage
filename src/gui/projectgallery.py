from PIL import Image
import wx

import lib.wxdyn.log as  log
import lib.wxdyn as wxd
import core.filemgmt as filemgmt

RESOURCES="resource"

ID_OPEN = 500

class ProjectGalleryFrame(wx.Frame):
    def __init__(self, styles, controller):
        super().__init__(parent=None, title='Project Gallery', style=wx.CAPTION | wx.CLOSE_BOX )

        iconFile = RESOURCES+"/icon.png"
        icon = wx.Icon(iconFile)
        self.SetIcon(icon)

        self.controller = controller
        self.model = self.controller.getModel()

        self.styles = styles
        self.applyStyles(self)
        self.storage = filemgmt.ProjectStorage(self.model.getApplication().getStorageDir())

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        self.scroller = wx.ScrolledWindow(self, name="scroller")
        self.scroller.SetInitialSize((800,600))
        self.applyStyles(self.scroller)
        self.sizer.Add(self.scroller, proportion=8, flag=wx.EXPAND|wx.ALL)

        self.selPrjPnl = self.constructSelectedProjectPanel()
        self.sizer.Add(self.selPrjPnl, 3)

        self.sizer.Layout()

        self.Fit()
        self.SetAutoLayout(True)
        self.Bind(event=wx.EVT_CLOSE, handler=self.onUserCloseWindow)

    def applyStyles(self, obj):
        obj.SetBackgroundColour(self.styles["BackgroundColour"])
        obj.SetForegroundColour(self.styles["ForegroundColour"])

    def cleanUp(self):
        children = self.GetChildren()
        for c in children:
            c.Destroy()

    def constructProjectTile(self, name, path):
        log.debug(function=self.constructProjectTile, args=(name, path))
        list = ["thumbnail.png", "source.png"]
        p = None
        for fName in list:
            p = filemgmt.toPath(path, fName)
            if p: return self.constructTile(name, p)

    def loadImage(self, path):
        # use PIL to load the image in stead of wx.Image to prevent 
        # the warning message: "iCCP: known incorrect sRGB profile"
        im = Image.open(path)
        wxImage = wx.Image(im.size)
        wxImage.SetData(im.convert('RGB').tobytes())
        wxImage.SetAlpha(im.convert("RGBA").tobytes()[3::4])
        return wxImage

    def constructTile(self, name, bmpPath):
        tilePnl = wx.Panel(self.scroller, size=(150,170))
        self.applyStyles(tilePnl)
        bmpBtn = wx.BitmapButton(tilePnl, id=ID_OPEN, 
            bitmap=self.loadImage(bmpPath).Rescale(140,140).ConvertToBitmap(), 
            name=name, size=(150, 150), style=wx.BORDER_NONE)
        bmpBtn.Bind(wx.EVT_BUTTON, self.onRead)
        bmpBtn.Bind(wx.EVT_LEFT_DCLICK, self.onOpen)
        lbl = wx.StaticText(tilePnl, label=name)
        self.applyStyles(lbl)
        self.applyStyles(bmpBtn)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(bmpBtn, 1)
        vbox.Add(lbl, 1)
        vbox.Layout()
        tilePnl.SetSizer(vbox)
        return tilePnl

    def constructSelectedProjectPanel(self):
        selPrjPnl = wx.Panel(self, size=(80, 600), style=wx.BORDER_SIMPLE)
        self.applyStyles(selPrjPnl)
        self.btnOpen = wx.Button(selPrjPnl, id=ID_OPEN, label=_("Open"), name="open", size=(80, 20))
        self.btnOpen.Bind(wx.EVT_BUTTON, self.onOpen)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.infoGrid = self.constructProjectInfoGrid(selPrjPnl)
        vbox.Add(self.infoGrid, 10)
        vbox.Add(self.btnOpen, proportion=1, flag=wx.EXPAND|wx.ALL)
        vbox.Layout()
        selPrjPnl.SetSizer(vbox)
        return selPrjPnl

    def constructProjectInfoGrid(self, container):
        infoGrid = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        txt = wx.StaticText(container, label="")
        infoGrid.Add(txt, 1)
        return infoGrid

    def loadGallery(self):
        self.scrollsizer = wx.FlexGridSizer(cols=5, hgap=5, vgap=5)
        self.scroller.SetSizer(self.scrollsizer)
        projects = self.storage.getProjects()
        for name, prjStorageData in projects.items():
            tile = self.constructProjectTile(name, prjStorageData)
            self.scrollsizer.Add(tile, 1)
        self.scrollsizer.Layout()
        self.scroller.SetScrollRate(5,5)

    def constructProperties(self, prjProps):  
        if prjProps:
            for c in self.selPrjPnl.GetChildren(): 
                if c!=self.btnOpen: c.Destroy()
            self.infoGrid.Clear()
            for item, val in prjProps.items():
                if not item in ["elements"]:
                    attrTxt = wx.StaticText(self.selPrjPnl, label=item, style=wx.EXPAND)
                    valueTxt = wx.StaticText(self.selPrjPnl, label=str(val), style=wx.EXPAND)
                    self.infoGrid.Add(attrTxt, 1)
                    self.infoGrid.Add(valueTxt, 1)
            txt = wx.StaticText(self.selPrjPnl, label="source", style=wx.EXPAND)
            src = wx.BitmapButton(self.selPrjPnl, 
                bitmap=self.loadImage(self.storage.toPath("source.png")).Rescale(140,140).ConvertToBitmap(), 
                size=(150, 150), style=wx.BORDER_NONE)
            self.infoGrid.Add(txt, 1)
            self.infoGrid.Add(src, 1)
            self.infoGrid.Layout()

    def onRead(self, e):
        btn = e.GetEventObject()
        nm = btn.GetName()
        self.storage.setName(nm)
        prjProps = self.storage.loadProperties()
        self.constructProperties(prjProps)

    def onOpen(self, e):
        log.debug(function=self.onOpen, args=e.GetEventObject().GetName())
        self.Hide()
        self.controller.openProject(self.storage.name)

    def onUserCloseWindow(self, e):
        self.Hide()

    def constructDummyTile(self, i):
        return self.constructTile("dummy"+str(i), RESOURCES+"/icon.png")

    def loadDummyGallery(self):
        self.scrollsizer = wx.FlexGridSizer(cols=5, hgap=5, vgap=5)
        self.scrollsizer.Clear()
        for i in range(60):
            self.scrollsizer.Add(self.constructDummyTile(i), 1)
        self.scrollsizer.Layout()
        self.scroller.SetSizer(self.scrollsizer)
        self.scroller.SetScrollRate(5,5)

    