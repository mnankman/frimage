import asyncio
from platform import platform
import wx
from wxasync import WxAsyncApp
from wx.lib.inspection import InspectionTool

from lib import log

from core.model.model import Model
from core.controller import Controller
import gui.zoompanel as zoompanel
import gui.dialogs as dlg
import gui.projectgallery as pgallery
from gui.projectpanels import ProjectPropertiesPanel, ResultPanel
import gui.i18n
        
RESOURCES="resource"

ID_FILE_NEW_PROJECT=101
ID_FILE_NEW_PROJECT_JULIAPROJECT=121
ID_FILE_NEW_PROJECT_MANDELBROTPROJECT=122
ID_FILE_OPEN_PROJECT=102
ID_FILE_SAVE_PROJECT=103
ID_FILE_SAVE_PROJECT_AS=104
ID_FILE_SAVE_GENERATED_IMAGE=105

ID_FILE_EXIT=199

ID_PROJECT_SELECT_SOURCEIMAGE=301
ID_PROJECT_GENERATE=302
ID_PROJECT_RESET=303
ID_PROJECT_SELECT_ZOOM_MODE=304
ID_PROJECT_SELECT_FINISH_MODE=305
ID_PROJECT_HISTORY_UP=306
ID_PROJECT_FIT_IMAGE=307

ID_DEBUG_SHOWINSPECTIONTOOL=601

ID_GROUP_PROJECTLOADED = []
for i in range(ID_FILE_SAVE_PROJECT,ID_FILE_SAVE_GENERATED_IMAGE+1): ID_GROUP_PROJECTLOADED.append(i)
for i in range(ID_PROJECT_SELECT_SOURCEIMAGE, ID_PROJECT_FIT_IMAGE+1): ID_GROUP_PROJECTLOADED.append(i)

ICONS = {
    ID_FILE_OPEN_PROJECT: RESOURCES+"/open.png",
    ID_FILE_SAVE_PROJECT: RESOURCES+"/save.png",
    ID_PROJECT_SELECT_SOURCEIMAGE: RESOURCES+"/add_photo.png",
    ID_PROJECT_GENERATE: RESOURCES+"/play.png",
    ID_PROJECT_RESET: RESOURCES+"/refresh.png",
    ID_PROJECT_FIT_IMAGE: RESOURCES+"/aspect_ratio.png",
    ID_PROJECT_SELECT_ZOOM_MODE: RESOURCES+"/picture_in_picture.png",
    ID_PROJECT_SELECT_FINISH_MODE: RESOURCES+"/image.png",
    ID_PROJECT_HISTORY_UP: RESOURCES+"/north_west.png",
}

WINDOW_STYLES = {
    "BackgroundColour": "#333333",
    "ForegroundColour": "#FFFFFF"
}

class MainWindow(wx.Frame):
    def __init__(self, styles, controller):
        super().__init__(parent=None, title='Frimage Studio', size=(1200,800))
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])

        iconFile = RESOURCES+"/icon.png"
        icon = wx.Icon(iconFile)
        self.SetIcon(icon)

        self.controller = controller
        self.model = self.controller.getModel()
        self.SetTitle(self.model.getApplicationTitle())
        self.model = self.controller.getModel()
        self.model.subscribe(self, "msg_new_project", self.onMsgNewProject)
        self.model.subscribe(self, "msg_open_project", self.onMsgOpenProject)
        self.model.subscribe(self, "msg_project_saved", self.onMsgProjectSaved)
        self.model.subscribe(self, "msg_generate_complete", self.onMsgGenerateComplete)

        self.prjGallery = pgallery.ProjectGalleryFrame(WINDOW_STYLES, self.controller)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
 
        self.configPnl = ProjectPropertiesPanel(self, styles, self.controller, size=(310,800))
        self.ResultPnl = ResultPanel(self, styles, self.controller, style=wx.SUNKEN_BORDER, size=(1600,1600))
        self.ResultPnl.Bind(zoompanel.EVT_ZOOM_AREA, self.configPnl.onGenerate)
        self.ResultPnl.Bind(zoompanel.EVT_DIVEDOWN, self.onUserProjectHistoryDown)

        self.sizer.Add(self.configPnl, 1)
        self.sizer.Add(self.ResultPnl, 5)
        self.SetAutoLayout(True)

        self.constructToolbar()
        self.constructMenu()
        self.SetSizer(self.sizer)
        self.SetMinSize((600,600))
 
        self.Show()

        self.Bind(event=wx.EVT_CLOSE, handler=self.onUserCloseMainWindow)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserNewMandelbrotProject, id=ID_FILE_NEW_PROJECT_MANDELBROTPROJECT)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserNewJuliaProject, id=ID_FILE_NEW_PROJECT_JULIAPROJECT)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserSaveProject, id=ID_FILE_SAVE_PROJECT)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserOpenProject, id=ID_FILE_OPEN_PROJECT)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserExit, id=ID_FILE_EXIT)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserShowInspectionTool, id=ID_DEBUG_SHOWINSPECTIONTOOL)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserGenerate, id=ID_PROJECT_GENERATE)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserReset, id=ID_PROJECT_RESET)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserSelectSourceImage, id=ID_PROJECT_SELECT_SOURCEIMAGE)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserSaveGeneratedImage, id=ID_FILE_SAVE_GENERATED_IMAGE)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserSelectZoomMode, id=ID_PROJECT_SELECT_ZOOM_MODE)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserSelectFinishMode, id=ID_PROJECT_SELECT_FINISH_MODE)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserProjectHistoryUp, id=ID_PROJECT_HISTORY_UP)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserProjectFitImage, id=ID_PROJECT_FIT_IMAGE)

        for id in ID_GROUP_PROJECTLOADED:
            self.enable(id, False)

        #wx.PostEvent(self, wx.MenuEvent(wx.wxEVT_MENU, ID_FILE_NEW_PROJECT_MANDELBROTPROJECT))

    def enable(self, id, enabled):
        try:
            self.toolBar.EnableTool(id, enabled)
            self.menuBar.Enable(id, enabled)
        except AssertionError as e:
            log.warning(e, function=self.enable, args=(id, enabled))
            pass
    
    def getToolBitmap(self, id, enabled=True):
        if id in ICONS.keys():
            im = wx.Image(ICONS[id])
            if enabled: 
                return im.ConvertToBitmap()
            else:
                return im.ConvertToDisabled().ConvertToBitmap()

    def addTool(self, toolbar, id, label, shortHelp=None, longHelp=""):
        toolbar.AddTool(id, label, self.getToolBitmap(id), self.getToolBitmap(id, False), 
            wx.ITEM_NORMAL, shortHelp if shortHelp else label, longHelp, None)

    def constructToolbar(self):
        self.toolBar = self.CreateToolBar()

        self.addTool(self.toolBar, ID_FILE_OPEN_PROJECT, "Open project")

        self.addTool(self.toolBar, ID_FILE_SAVE_PROJECT, "Save project")
        self.toolBar.AddSeparator()
        self.addTool(self.toolBar, ID_PROJECT_SELECT_SOURCEIMAGE, "Select image...")
        self.addTool(self.toolBar, ID_PROJECT_GENERATE, "Generate")
        self.addTool(self.toolBar, ID_PROJECT_RESET, "Reset")
        self.addTool(self.toolBar, ID_PROJECT_FIT_IMAGE, "Fit image to frame size")
        self.toolBar.AddSeparator()
        self.addTool(self.toolBar, ID_PROJECT_SELECT_ZOOM_MODE, "Zoom mode")
        self.addTool(self.toolBar, ID_PROJECT_SELECT_FINISH_MODE, "Zoom mode")
        self.addTool(self.toolBar, ID_PROJECT_HISTORY_UP, "Zoom mode")
        
        self.toolBar.Realize()

        self.SetToolBar(self.toolBar)

    def constructMenu(self):
        self.menuBar = wx.MenuBar()
        debugMenu = wx.Menu()
        debugMenu.Append(ID_DEBUG_SHOWINSPECTIONTOOL, "&Inspection tool", "Show the WX Inspection Tool")
        fileMenu = wx.Menu()
        
        newProjectMenu = wx.Menu()
        newProjectMenu.Append(ID_FILE_NEW_PROJECT_MANDELBROTPROJECT, "new &Mandelbrot Project", "Create new Mandelbrot Project")
        newProjectMenu.Append(ID_FILE_NEW_PROJECT_JULIAPROJECT, "new &Julia Project", "Create new Julia Project")
        fileMenu.AppendSubMenu(newProjectMenu, "&New")
        fileMenu.Append(ID_FILE_SAVE_PROJECT, "&Save project", "Save current project")
        fileMenu.Append(ID_FILE_SAVE_PROJECT_AS, "&Save project as...", "Save current project under a new name")
        fileMenu.Append(ID_FILE_OPEN_PROJECT, "&Open project", "Open project")
        fileMenu.Append(ID_FILE_SAVE_GENERATED_IMAGE, "Save &generated image", "Save generated image")
        fileMenu.Append(ID_FILE_EXIT, "E&xit", "Exit")

        projectMenu = wx.Menu()
        projectMenu.Append(ID_PROJECT_SELECT_SOURCEIMAGE, "Se&lect source image", "Select the source image for this project")
        projectMenu.Append(ID_PROJECT_RESET, "&Reset", "Reset to default values")
        projectMenu.Append(ID_PROJECT_GENERATE, "&Generate", "Generate")
        projectMenu.Append(ID_PROJECT_FIT_IMAGE, "Scale image to f&it", "Scale image to fit")
        projectMenu.Append(ID_PROJECT_SELECT_ZOOM_MODE, "Select &Zoom Mode", "Select Zoom Mode")
        projectMenu.Append(ID_PROJECT_SELECT_FINISH_MODE, "Select &Finish Mode", "Select Finish Mode")
        projectMenu.Append(ID_PROJECT_HISTORY_UP, "Go &up (to parent view)", "Go to parent view")
        self.menuBar.Append(fileMenu, "&File")
        self.menuBar.Append(projectMenu, "&Project")
        self.menuBar.Append(debugMenu, "&Debug")
        self.SetMenuBar(self.menuBar)

    def activateTools(self, group):
        for id in group:
            self.enable(id, True)

    def onMsgNewProject(self, payload):
        self.activateTools(ID_GROUP_PROJECTLOADED)
        self.controller.clearProjectModifications()

    def onMsgOpenProject(self, payload):
        self.activateTools(ID_GROUP_PROJECTLOADED)
        self.controller.clearProjectModifications()

    def onMsgProjectSaved(self, payload):
        self.controller.clearProjectModifications()

    def onMsgGenerateComplete(self, payload):
        self.controller.clearProjectModifications()

    def onUserCloseMainWindow(self, e):
        exit()

    def onUserExit(self, e):
        self.askSaveProject()
        self.Close(True) 
        e.Skip()

    def onUserNewMandelbrotProject(self, e):
        self.askSaveProject()
        self.controller.newMandelbrotProject("mandelbrot")
        e.Skip()

    def onUserNewJuliaProject(self, e):
        self.askSaveProject()
        self.controller.newJuliaProject("julia")
        e.Skip()

    def onUserSaveProject(self, e):
        self.controller.saveProject()
        e.Skip()

    def onUserSaveProjectAs(self, e):
        pass

    def onUserSaveGeneratedImage(self, e):
        path = dlg.saveImageDialog(self)
        self.ResultPnl.saveCurrentImage(path)
        #self.controller.saveGeneratedImage(path)
        e.Skip()

    def onUserGenerate(self, e):
        self.configPnl.onGenerate(e)
        e.Skip()

    def onUserReset(self, e):
        self.controller.resetProject()
        e.Skip()

    def selectProjectSourceImage(self, path):
        self.controller.selectProjectSourceImage(path)
    
    def onUserSelectSourceImage(self, e):
        path = dlg.openImageDialog(self)
        self.selectProjectSourceImage(path)
        e.Skip()

    def askSaveProject(self):
        if self.controller.getCurrentProject()==None: return
        if self.controller.getCurrentProject().isModified():
            if dlg.message(_("Do you want to save current project?"), wx.YES_NO) == wx.ID_YES:
                self.controller.saveProject()

    def onUserOpenProject(self, e):
        self.askSaveProject()
        self.prjGallery.loadGallery()
        self.prjGallery.Show()
        e.Skip()

    def onUserSelectZoomMode(self, e):
        self.ResultPnl.setZoomMode()
        e.Skip()

    def onUserSelectFinishMode(self, e):
        self.ResultPnl.setFinishMode()
        e.Skip()
    
    def onUserProjectHistoryUp(self, e):
        log.debug(function=self.onUserProjectHistoryUp)
        self.controller.clearProjectModifications()
        self.controller.up()
        e.Skip()

    def onUserProjectHistoryDown(self, e):
        log.debug(function=self.onUserProjectHistoryDown)
        self.controller.clearProjectModifications()
        self.controller.down(e.set)
        e.Skip()

    def onUserProjectFitImage(self, e):
        self.ResultPnl.toggleFitImage()
        e.Skip()

    def onUserShowInspectionTool(self, e):
        InspectionTool().Show()
        e.Skip()

import logging

import PIL._version as pilversion
import numpy as np
import platform
def versions():
    print("Platform and lbirary versions:")
    print("Python version", platform.python_version())
    print("wx version", wx.version())
    print("PIL version", pilversion.__version__)
    print("Numpy version", np.__version__)


def start():
    # configure logging
    logging.basicConfig(format='[%(name)s] %(levelname)s:%(message)s', level=logging.DEBUG)
    log.setLoggerLevel("lib.persistentobject", logging.ERROR)
    log.setLoggerLevel("lib.modelobject", logging.DEBUG)
    log.setLoggerLevel("gui.projectgallery", logging.ERROR)
    log.setLoggerLevel("core.filemgmt", logging.ERROR)
    log.setLoggerLevel("lib.pubsub", logging.ERROR)

    versions()
       
    # construct the asynchronous app and run it in the main async event loop
    app = WxAsyncApp()
    loop = asyncio.get_event_loop()
    controller = Controller(Model())
    w = MainWindow(WINDOW_STYLES, controller)
    dlg.Messages.setWindow(w)
    try:
        loop.run_until_complete(app.MainLoop())
    finally:
        loop.stop()
        loop.close()

if __name__ == '__main__':
    start()

