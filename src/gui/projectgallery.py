import wx
from lib import log

import gui.dynctrl as dynctrl 
import base.filemgmt as filemgmt

RESOURCES="resource"

ID_OPEN = 500

class ProjectGalleryFrame(wx.Frame):
    def __init__(self, styles, controller):
        super().__init__(parent=None, title='Project Gallery', size=(800,600))
        #self.SetBackgroundColour(styles["BackgroundColour"])
        #self.SetForegroundColour(styles["ForegroundColour"])
        self.storage = filemgmt.ProjectStorage()

        iconFile = RESOURCES+"/icon.png"
        icon = wx.Icon(iconFile)
        self.SetIcon(icon)

        self.controller = controller
        self.model = self.controller.getModel()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.Bind(event=wx.EVT_BUTTON, handler=self.onOpen, id=ID_OPEN)

    def cleanUp(self):
        children = self.GetChildren()
        for c in children:
            c.Destroy()

    def constructProjectTile(self, name, path):
        tile = wx.Panel(self, size=(150,170))
        sizer = wx.FlexGridSizer(1, gap=(5, 5))
        tile.SetSizer(sizer)
        bmp = wx.Image(path+"/root.png").ConvertToBitmap()
        bmpBtn = wx.BitmapButton(tile, ID_OPEN, bmp, name=name, size=(150, 150))
        lbl = wx.StaticText(tile, label=name, size=(150, 20), style=wx.TEXT_ALIGNMENT_CENTER)
        sizer.Add(bmpBtn, 1)
        sizer.Add(lbl, 1)
        tile.Center()
        sizer.Layout()
        return tile

    def construct(self):
        self.sizer.Clear()
        gridsizer = wx.FlexGridSizer(1, 0, gap=(5, 5))
        projects = self.storage.getProjects()
        for name, path in projects.items():
            tile = self.constructProjectTile(name, path)
            gridsizer.Add(tile, 1)

        self.sizer.Add(gridsizer, 1)
        self.sizer.Layout()

    def onOpen(self, e):
        log.debug(function=self.onOpen, args=e.GetEventObject().GetName())
        btn = e.GetEventObject()
        nm = btn.GetName()
        self.controller.openProject(nm)
        self.Hide()

