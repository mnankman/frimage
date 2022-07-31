import asyncio
from platform import platform
import wx
import wx.svg
from wxasync import WxAsyncApp
from wx.lib.inspection import InspectionTool

from builtins import _
import lib.wxdyn.log as log
import lib.wxdyn as wxdyn

from core.model import Model
from core.controller import Controller
import gui.dialogs as dlg
import gui.zoompanel as zoom
from gui import ProjectPropertiesPanel, ResultPanel, ProjectExplorerPanel, StatusBar
from gui import ProjectGalleryFrame
from gui import styles


        
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
ID_PROJECT_UP=306
ID_PROJECT_HOME=307
ID_PROJECT_MAKE_ROOT=308
ID_PROJECT_DELETE_BRANCH=309
ID_PROJECT_FIT_IMAGE=310

ID_PROJECT_EXPLORER=311
ID_PROJECT_PROPERTIES=312

ID_DEBUG_SHOWINSPECTIONTOOL=601

ID_GROUP_PROJECTLOADED = []
for i in range(ID_FILE_SAVE_PROJECT,ID_FILE_SAVE_GENERATED_IMAGE+1): ID_GROUP_PROJECTLOADED.append(i)
for i in range(ID_PROJECT_SELECT_SOURCEIMAGE, ID_PROJECT_FIT_IMAGE+1): ID_GROUP_PROJECTLOADED.append(i)

RESOURCE_LIST = {
    ID_FILE_OPEN_PROJECT: RESOURCES+"/open.png",
    ID_FILE_SAVE_PROJECT: RESOURCES+"/save.png",
    ID_PROJECT_SELECT_SOURCEIMAGE: RESOURCES+"/add_photo.png",
    ID_PROJECT_GENERATE: RESOURCES+"/play.png",
    ID_PROJECT_RESET: RESOURCES+"/refresh.png",
    ID_PROJECT_FIT_IMAGE: RESOURCES+"/aspect_ratio.png",
    ID_PROJECT_SELECT_ZOOM_MODE: RESOURCES+"/picture_in_picture.png",
    ID_PROJECT_SELECT_FINISH_MODE: RESOURCES+"/image.png",
    ID_PROJECT_UP: RESOURCES+"/north_west.png",
    ID_PROJECT_HOME: RESOURCES+"/home.png",
    ID_PROJECT_MAKE_ROOT: RESOURCES+"/upload.png",
    ID_PROJECT_DELETE_BRANCH: RESOURCES+"/delete.png",
    ID_FILE_NEW_PROJECT: RESOURCES+"/add.svg",
    ID_PROJECT_EXPLORER: RESOURCES+"/tree.svg",
    ID_PROJECT_PROPERTIES: RESOURCES+"/ballot.svg",
}

WINDOW_STYLES = {
    "BackgroundColour": "#333333",
    "ForegroundColour": "#FFFFFF"
}

class MainWindow(wx.Frame):
    def __init__(self, styles, controller):
        super().__init__(parent=None, title='Frimage Studio', size=(1200,900))
        self.styler = wxdyn.WindowStyler()
        self.styler.select("Anything:normal", self)
        
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

        self.prjGallery = ProjectGalleryFrame(WINDOW_STYLES, self.controller)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.createPnl = self.constructCreatePanel((310,2000))

        self.configPnl = ProjectPropertiesPanel(self, self.controller, size=(310,2000), name="properties")
        self.configPnl.SetMaxSize((310,2000))
        self.explorerPnl = ProjectExplorerPanel(self, self.controller, size=(310,2000), name="explorer")
        self.explorerPnl.SetMaxSize((310,2000))
        self.tabctrl = wxdyn.TabCtrl(self)
        self.tabctrl.SetForegroundColour(styles["ForegroundColour"])
        self.tabctrl.addTab(self.createPnl, "", svg=self.getResource(ID_FILE_NEW_PROJECT))
        self.tabctrl.addTab(self.configPnl, "", svg=self.getResource(ID_PROJECT_PROPERTIES))
        self.tabctrl.addTab(self.explorerPnl, "", svg=self.getResource(ID_PROJECT_EXPLORER))
        self.tabctrl.selectTab("create")

        self.ResultPnl = ResultPanel(self, self.controller, style=wx.SUNKEN_BORDER)
        self.ResultPnl.Bind(zoom.EVT_IMAGE_UPDATED, self.onImageUpdated)
        self.ResultPnl.Bind(zoom.EVT_ZOOM_AREA, self.onUserGenerate)
        self.ResultPnl.Bind(zoom.EVT_DIVEDOWN, self.onDiveDown)

        hbox.Add(self.tabctrl, 1, 0, 0)
        hbox.Add(self.ResultPnl, 10, wx.EXPAND | wx.ALL, 0)
        self.sizer.Add(hbox, 1, flag=wx.EXPAND)
        self.statusBar = StatusBar(self, self.controller, size=(4000,15))
        self.sizer.Add(self.statusBar, 0, wx.EXPAND | wx.ALL, 0)
        self.sizer.Layout()

        self.constructToolbar()
        self.constructMenu()

        self.SetAutoLayout(True)
        self.SetMinSize((800,800))
 
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
        self.Bind(event=wx.EVT_MENU, handler=self.onProjectUp, id=ID_PROJECT_UP)
        self.Bind(event=wx.EVT_MENU, handler=self.onProjectHome, id=ID_PROJECT_HOME)
        self.Bind(event=wx.EVT_MENU, handler=self.onProjectMakeRoot, id=ID_PROJECT_MAKE_ROOT)
        self.Bind(event=wx.EVT_MENU, handler=self.onProjectDeleteBranch, id=ID_PROJECT_DELETE_BRANCH)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserProjectFitImage, id=ID_PROJECT_FIT_IMAGE)

        for id in ID_GROUP_PROJECTLOADED:
            self.enable(id, False)

        #wx.PostEvent(self, wx.MenuEvent(wx.wxEVT_MENU, ID_FILE_NEW_PROJECT_MANDELBROTPROJECT))


        self.Show()


    def enable(self, id, enabled):
        try:
            self.toolBar.EnableTool(id, enabled)
            self.menuBar.Enable(id, enabled)
        except AssertionError as e:
            log.warning(e, function=self.enable, args=(id, enabled))
            pass
    
    def getResource(self, id):
        if id in RESOURCE_LIST.keys():
            res = RESOURCE_LIST[id]
            if res.endswith("png"):
                return wx.Image(res)
            elif res.endswith("svg"):
                return wx.svg.SVGimage.CreateFromFile(res)
            else:
                return None

    def getToolBitmap(self, id, enabled=True):
        im = self.getResource(id)
        if im:
            if enabled: 
                return im.ConvertToBitmap()
            else:
                return im.ConvertToDisabled().ConvertToBitmap()
        else:
            return None

    def addTool(self, toolbar, id, label, shortHelp=None, longHelp=""):
        toolbar.AddTool(id, label, self.getToolBitmap(id), self.getToolBitmap(id, False), 
            wx.ITEM_NORMAL, shortHelp if shortHelp else label, longHelp, None)

    def constructCreatePanel(self, size):
        pnl = wx.Panel(self, size=size, name="create")
        vbox = wx.BoxSizer(wx.VERTICAL)
        pnl.SetSizer(vbox)
        w,h=size
        gridsizer = wx.FlexGridSizer(1, gap=(5, 5))
        btnNewMandelbrot = wxdyn.Button(pnl, label=_("Mandelbrot project"), svg=self.getResource(ID_FILE_NEW_PROJECT), size=(w*0.8, 30), style=wx.CENTER)
        btnNewJulia = wxdyn.Button(pnl, label=_("Julia project"), svg=self.getResource(ID_FILE_NEW_PROJECT), size=(w*0.8, 30), style=wx.CENTER)
        gridsizer.Add(btnNewMandelbrot, 1)
        gridsizer.Add(btnNewJulia, 1)
        btnNewMandelbrot.Bind(wxdyn.EVT_BUTTON_PRESSED, self.onUserNewMandelbrotProject)
        btnNewJulia.Bind(wxdyn.EVT_BUTTON_PRESSED, self.onUserNewJuliaProject)
        vbox.AddSpacer(40)
        vbox.Add(gridsizer, 1, flag=wx.ALIGN_CENTER_HORIZONTAL)
        pnl.SetAutoLayout(True)
        pnl.SetMaxSize((310,2000))
        vbox.Layout()
        self.styler.select("Anything:normal", pnl) 
        for c in pnl.GetChildren():
            self.styler.select("Anything:normal", c) 
        return pnl

    def constructToolbar(self):
        self.toolBar = self.CreateToolBar()

        self.addTool(self.toolBar, ID_FILE_OPEN_PROJECT, _("Open project"))

        self.addTool(self.toolBar, ID_FILE_SAVE_PROJECT, _("Save project"))
        self.toolBar.AddSeparator()
        self.addTool(self.toolBar, ID_PROJECT_SELECT_SOURCEIMAGE, _("Select image..."))
        self.addTool(self.toolBar, ID_PROJECT_GENERATE, _("Generate"))
        self.addTool(self.toolBar, ID_PROJECT_RESET, _("Reset"))
        self.addTool(self.toolBar, ID_PROJECT_FIT_IMAGE, _("Fit image to frame size"))
        self.toolBar.AddSeparator()
        self.addTool(self.toolBar, ID_PROJECT_SELECT_ZOOM_MODE, _("Zoom mode"))
        self.addTool(self.toolBar, ID_PROJECT_SELECT_FINISH_MODE, _("Finish mode"))
        self.addTool(self.toolBar, ID_PROJECT_HOME, _("Go to home area"))
        self.addTool(self.toolBar, ID_PROJECT_UP, _("Go to parent area"))
        self.addTool(self.toolBar, ID_PROJECT_MAKE_ROOT, _("Make current area root"))
        self.addTool(self.toolBar, ID_PROJECT_DELETE_BRANCH, _("Remove the current area and all area's behind it"))
        
        self.toolBar.Realize()

        self.SetToolBar(self.toolBar)

    def constructMenu(self):
        self.menuBar = wx.MenuBar()
        debugMenu = wx.Menu()
        debugMenu.Append(ID_DEBUG_SHOWINSPECTIONTOOL, _("&Inspection tool"), _("Show the WX Inspection Tool"))
        fileMenu = wx.Menu()
        
        newProjectMenu = wx.Menu()
        newProjectMenu.Append(ID_FILE_NEW_PROJECT_MANDELBROTPROJECT, _("new &Mandelbrot Project"), _("Create new Mandelbrot Project"))
        newProjectMenu.Append(ID_FILE_NEW_PROJECT_JULIAPROJECT, _("new &Julia Project"), _("Create new Julia Project"))
        fileMenu.AppendSubMenu(newProjectMenu, _("&New"))
        fileMenu.Append(ID_FILE_SAVE_PROJECT, _("&Save project"), _("Save current project"))
        fileMenu.Append(ID_FILE_SAVE_PROJECT_AS, _("&Save project as..."), _("Save current project under a new name"))
        fileMenu.Append(ID_FILE_OPEN_PROJECT, _("&Open project"), _("Open project"))
        fileMenu.Append(ID_FILE_SAVE_GENERATED_IMAGE, _("Save &generated image"), _("Save generated image"))
        fileMenu.Append(ID_FILE_EXIT, _("E&xit"), _("Exit"))

        projectMenu = wx.Menu()
        projectMenu.Append(ID_PROJECT_SELECT_SOURCEIMAGE, _("Se&lect source image"), _("Select the source image for this project"))
        projectMenu.Append(ID_PROJECT_RESET, _("&Reset"), _("Reset to default values"))
        projectMenu.Append(ID_PROJECT_GENERATE, _("&Generate"), _("Generate"))
        projectMenu.Append(ID_PROJECT_FIT_IMAGE, _("Scale image to f&it"), _("Scale image to fit"))
        projectMenu.Append(ID_PROJECT_SELECT_ZOOM_MODE, _("Select &Zoom Mode"), _("Select Zoom Mode"))
        projectMenu.Append(ID_PROJECT_SELECT_FINISH_MODE, _("Select &Finish Mode"), _("Select Finish Mode"))
        projectMenu.Append(ID_PROJECT_HOME, _("Go &home (to top view)"), _("Go to top view"))
        projectMenu.Append(ID_PROJECT_UP, _("Go &up (to parent view)"), _("Go to parent view"))
        projectMenu.Append(ID_PROJECT_MAKE_ROOT, _("Make r&oot"), _("Make current area the new root"))
        projectMenu.Append(ID_PROJECT_DELETE_BRANCH, _("&Delete this branch"), _("Delete this branch"))
        self.menuBar.Append(fileMenu, _("&File"))
        self.menuBar.Append(projectMenu, _("&Project"))
        self.menuBar.Append(debugMenu, _("&Debug"))
        self.SetMenuBar(self.menuBar)

    def activateTools(self, group):
        for id in group:
            self.enable(id, True)

    def onMsgNewProject(self, payload):
        self.activateTools(ID_GROUP_PROJECTLOADED)
        self.controller.clearProjectModifications()
        self.controller.clearProjectTouch()
        self.tabctrl.selectTab("properties")

    def onMsgOpenProject(self, payload):
        self.activateTools(ID_GROUP_PROJECTLOADED)
        self.controller.clearProjectModifications()
        self.controller.clearProjectTouch()
        self.tabctrl.selectTab("properties")

    def onMsgProjectSaved(self, payload):
        self.controller.clearProjectModifications()

    def onMsgGenerateComplete(self, payload):
        self.controller.clearProjectModifications()
        self.controller.getCurrentProject().setTouched()

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
        self.statusBar.onGenerate(e)
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
        if self.controller.getCurrentProject().getTouched():
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
    
    def onProjectUp(self, e):
        log.debug(function=self.onProjectUp)
        self.controller.clearProjectModifications()
        self.controller.up()
        e.Skip()

    def onProjectHome(self, e):
        log.debug(function=self.onProjectHome)
        self.controller.clearProjectModifications()
        self.controller.home()
        e.Skip()

    def onProjectMakeRoot(self, e):
        log.debug(function=self.onProjectMakeRoot)
        if dlg.message(_("This will make this area the root of the project and remove everything above this point. Are you sure?"), wx.YES_NO) == wx.ID_YES:
            self.controller.makeRoot()
        e.Skip()

    def onProjectDeleteBranch(self, e):
        log.debug(function=self.onProjectDeleteBranch)
        if dlg.message(_("This will remove this area and all area's after it. Are you sure?"), wx.YES_NO) == wx.ID_YES:
            self.controller.remove()
        e.Skip()

    def onDiveDown(self, e):
        log.debug(function=self.onDiveDown)
        self.controller.clearProjectModifications()
        self.controller.down(e.set)
        e.Skip()

    def onImageUpdated(self, e):
        log.debug(function=self.onImageUpdated)
        self.controller.clearProjectModifications()
        e.Skip()

    def onUserProjectFitImage(self, e):
        self.ResultPnl.toggleFitImage()
        e.Skip()

    def onUserShowInspectionTool(self, e):
        InspectionTool().Show()
        e.Skip()

import PIL._version as pilversion
import numpy as np
import platform
def versions():
    print("Platform and lbirary versions:")
    print("Python version", platform.python_version())
    print("wx version", wx.version())
    print("PIL version", pilversion.__version__)
    print("Numpy version", np.__version__)

import logsetup
def start():
    logsetup.setup(logsetup.SETUP_DEBUG)

    versions()
       
    # construct the asynchronous app and run it in the main async event loop
    app = WxAsyncApp()
    styles.init()
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

