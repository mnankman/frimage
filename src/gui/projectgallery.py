import wx
from wx.lib.scrolledpanel import ScrolledPanel
import gui.dynctrl as dynctrl 
import base.filemgmt as filemgmt
from lib import log

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
        self.storage = filemgmt.ProjectStorage()

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

    def applyStyles(self, obj):
        obj.SetBackgroundColour(self.styles["BackgroundColour"])
        obj.SetForegroundColour(self.styles["ForegroundColour"])

    def cleanUp(self):
        children = self.GetChildren()
        for c in children:
            c.Destroy()

    def constructProjectTile(self, name, path):
        return self.constructTile(name, path+"/root.png")

    def constructTile(self, name, bmpPath):
        tilePnl = wx.Panel(self.scroller, size=(150,170))
        self.applyStyles(tilePnl)
        bmpBtn = wx.BitmapButton(tilePnl, id=ID_OPEN, 
            bitmap=wx.Image(bmpPath).Rescale(140,140).ConvertToBitmap(), 
            name=name, size=(150, 150), style=wx.BORDER_NONE)
        bmpBtn.Bind(wx.EVT_BUTTON, self.onOpen)
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
        btnOpen = wx.Button(selPrjPnl, id=ID_OPEN, label=_("Open"), name="Open Project", size=(80, 20))
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.constructProjectInfoGrid(selPrjPnl), 10)
        vbox.Add(btnOpen, proportion=1, flag=wx.EXPAND|wx.ALL)
        vbox.Layout()
        selPrjPnl.SetSizer(vbox)
        return selPrjPnl

    def constructProjectInfoGrid(self, container):
        infoGrid = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
        txt = wx.StaticText(container, label="project info")
        infoGrid.Add(txt, 1)
        return infoGrid

    def loadGallery(self):
        self.scrollsizer = wx.FlexGridSizer(cols=5, hgap=5, vgap=5)
        self.scroller.SetSizer(self.scrollsizer)
        self.scrollsizer.Clear()
        projects = self.storage.getProjects()
        for name, path in projects.items():
            tile = self.constructProjectTile(name, path)
            self.scrollsizer.Add(tile, 1)
        self.scrollsizer.Layout()

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

    def onOpen(self, e):
        log.debug(function=self.onOpen, args=e.GetEventObject().GetName())
        btn = e.GetEventObject()
        nm = btn.GetName()
        self.controller.openProject(nm)
        self.Hide()
