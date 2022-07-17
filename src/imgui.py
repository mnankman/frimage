import asyncio
import wx
from wxasync import WxAsyncApp, StartCoroutine
from wx.lib.inspection import InspectionTool
import wx.lib.progressindicator as progress

from lib import log

from base.model import JuliaProject, Model
from base.controller import Controller
import gui.dynctrl as dynctrl 
import gui.zoompanel as zoompanel
import gui.dialogs as dlg
import gui.i18n
        
RESOURCES="resource"

ID_FILE_NEW_PROJECT=101
ID_FILE_SAVE_PROJECT=102
ID_FILE_SAVE_PROJECT_AS=103
ID_FILE_OPEN_PROJECT=104
ID_FILE_SAVE_GENERATED_IMAGE=105
ID_FILE_EXIT=199

ID_FILE_NEW_PROJECT_JULIAPROJECT=121
ID_FILE_NEW_PROJECT_MANDELBROTPROJECT=122

ID_PROJECT_SELECT_SOURCEIMAGE=301
ID_PROJECT_GENERATE=302
ID_PROJECT_RESET=303
ID_PROJECT_SELECT_ZOOM_MODE=304
ID_PROJECT_SELECT_FINISH_MODE=305
ID_PROJECT_HISTORY_NEXT=306
ID_PROJECT_HISTORY_PREVIOUS=307
ID_PROJECT_HISTORY_UP=308

ID_DEBUG_SHOWINSPECTIONTOOL=601

WINDOW_STYLES = {
    "BackgroundColour": "#333333",
    "ForegroundColour": "#FFFFFF"
}


class ProjectPropertiesPanel(wx.Panel):
    def __init__(self, parent, styles, controller, **kw):
        super(ProjectPropertiesPanel, self).__init__(parent, **kw)    
        self.styles = styles
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])
        self.controller = controller
        self.model = self.controller.getModel()
        self.model.subscribe(self, "msg_new_project", self.onMsgNewProject)
        self.model.subscribe(self, "msg_open_project", self.onMsgOpenProject)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def cleanUp(self):
        children = self.GetChildren()
        for c in children:
            c.Destroy()

    def construct(self, project):
        self.project = project
        self.area = self.project.getArea()
        self.projectSource = self.project.getProjectSource()

        self.sizer.Clear()
        gridsizer1 = wx.FlexGridSizer(4,0,5,5)
        
        im1 = dynctrl.DynamicBitmap(self, self.projectSource, "sourceImage", self.styles, size=(160,160))
        im1.SetScaleMode(wx.StaticBitmap.Scale_AspectFit)
        im2 = dynctrl.DynamicBitmap(self, self.projectSource, "heatmapBaseImage", self.styles, size=(160,160))
        im2.SetScaleMode(wx.StaticBitmap.Scale_AspectFit)
        im3 = dynctrl.DynamicBitmap(self, self.projectSource, "gradientImage", self.styles, size=(160,20))
        im3.SetScaleMode(wx.StaticBitmap.Scale_Fill)
        chkBox1 = dynctrl.DynamicCheckBox(self, self.projectSource, "flipGradient", self.styles, label="flip gradient:")
        gridsizer1.AddMany([(im1, 1), (im2, 1), (im3, 1), (chkBox1, 1)])
        self.sizer.Add(gridsizer1, 1)
        self.sizer.AddSpacer(5)

        lbl1_1 = wx.StaticText(self, label="heatmap width:", size=(120, 20))
        lbl1_2 = wx.StaticText(self, label="heatmap height:", size=(120, 20))
        textCtrl1_1 = dynctrl.DynamicSpinCtrl(self, self.projectSource, "heatmapBaseImageWidth", self.styles, size=(60, 18), min=4, max=50, style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        textCtrl1_2 = dynctrl.DynamicSpinCtrl(self, self.projectSource, "heatmapBaseImageHeight", self.styles, size=(60, 18), min=4, max=50, style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        lbl2_1 = wx.StaticText(self, label="generated width:", size=(120, 20))
        lbl2_2 = wx.StaticText(self, label="generated height:", size=(120, 20))
        textCtrl2_1 = dynctrl.DynamicSpinCtrl(self, self.project, "width", self.styles, size=(60, 18), min=200, max=2500, style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        textCtrl2_2 = dynctrl.DynamicSpinCtrl(self, self.project, "height", self.styles, size=(60, 18), min=200, max=2500, style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        lbl3_1 = wx.StaticText(self, label="border size:", size=(120, 20))
        lbl3_2 = wx.StaticText(self, label="border colour:", size=(120, 20))
        textCtrl3_1 = dynctrl.DynamicSpinCtrl(self, self.project, "borderSize", self.styles, size=(60, 18), min=0, max=50, style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        textCtrl3_2 = dynctrl.DynamicSpinCtrl(self, self.project, "borderColourPick", self.styles, size=(60, 18), min=1, max=255, style=wx.SP_WRAP|wx.SP_ARROW_KEYS)
        gridsizer2 = wx.FlexGridSizer(2, gap=(5, 5))
        gridsizer2.AddMany([
            (lbl1_1, 1), (textCtrl1_1, 1), 
            (lbl1_2, 1), (textCtrl1_2, 1), 
            (lbl2_1, 1), (textCtrl2_1, 1), 
            (lbl2_2, 1), (textCtrl2_2, 1), 
            (lbl3_1, 1), (textCtrl3_1, 1), 
            (lbl3_2, 1), (textCtrl3_2, 1)
        ])
 
        '''
        lbl4_1 = wx.StaticText(self, label="Ax:", size=(120, 20))
        lbl4_2 = wx.StaticText(self, label="Ay:", size=(120, 20))
        lbl4_3 = wx.StaticText(self, label="Bx:", size=(120, 20))
        lbl4_4 = wx.StaticText(self, label="By:", size=(120, 20))
        textCtrl4_1 = dynctrl.DynamicTextCtrl(self, self.area, "xa", self.styles, size=(120, 18))
        textCtrl4_1.Disable()
        textCtrl4_2 = dynctrl.DynamicTextCtrl(self, self.area, "ya", self.styles, size=(120, 18))
        textCtrl4_2.Disable()
        textCtrl4_3 = dynctrl.DynamicTextCtrl(self, self.area, "xb", self.styles, size=(120, 18))
        textCtrl4_3.Disable()
        textCtrl4_4 = dynctrl.DynamicTextCtrl(self, self.area, "yb", self.styles, size=(120, 18))
        textCtrl4_4.Disable()
        
        gridsizer2.AddMany([
            (lbl4_1, 1), (textCtrl4_1, 1), 
            (lbl4_2, 1), (textCtrl4_2, 1),
            (lbl4_3, 1), (textCtrl4_3, 1), 
            (lbl4_4, 1), (textCtrl4_4, 1)
        ])
        '''
        self.sizer.Add(gridsizer2, 1)

        if isinstance(project, JuliaProject):
            self.cxy = project.getCxy()
            lbl5_1 = wx.StaticText(self, label="cx:", size=(120, 20))
            lbl5_2 = wx.StaticText(self, label="cy:", size=(120, 20))
            textCtrl5_1 = dynctrl.DynamicTextCtrl(self, self.cxy, "cx", self.styles, size=(150, 18))
            textCtrl5_2 = dynctrl.DynamicTextCtrl(self, self.cxy, "cy", self.styles, size=(150, 18))

            gridsizer3 = wx.FlexGridSizer(2, gap=(5, 5))
            gridsizer3.AddMany([
                (lbl5_1, 1), (textCtrl5_1, 1), 
                (lbl5_2, 1), (textCtrl5_2, 1) 
            ])
            self.sizer.Add(gridsizer3, 1)

        gridsizer4 = wx.FlexGridSizer(1, gap=(5, 5))

        pw,ph = self.GetSize()
        self.btnGenerate = wx.Button(self, label=_("Generate"), size=(pw, 18))
        btnReset = wx.Button(self, label=_("Reset"), size=(pw, 18))
        self.progressBar = progress.ProgressIndicator(self, size=(pw,5))
        gridsizer4.Add(btnReset, 1)
        gridsizer4.Add(self.btnGenerate, 1)
        gridsizer4.Add(self.progressBar, 1)
        self.btnGenerate.Bind(wx.EVT_BUTTON, self.onGenerate)
        btnReset.Bind(wx.EVT_BUTTON, self.onReset)

        self.sizer.Add(gridsizer4, 1)
        self.sizer.Layout()

    def onMsgNewProject(self, payload):
        prj = payload["project"]
        self.cleanUp()
        self.construct(prj)
        self.Refresh()

    def onMsgOpenProject(self, payload):
        prj = payload["project"]
        self.cleanUp()
        self.construct(prj)
        self.Refresh()

    def onProgress(self, generator, p):
        self.progressBar.SetValue(p)
        if p>=100: 
            self.btnGenerate.Enable()
            self.btnGenerate.SetLabel(_("Generate"))

    def onGenerate(self, e):
        if isinstance(e, zoompanel.ZoomAreaEvent):
            self.selectedArea = e.area
        else:
            self.selectedArea = None
        self.progressBar.Start()
        self.btnGenerate.SetLabel(_("working") + "...")
        self.btnGenerate.Disable()
        StartCoroutine(self.generate, self)
        e.Skip()

    def onReset(self, e):
        self.project.reset()
        e.Skip()

    async def generate(self):
        await self.controller.generate(self.onProgress, area=self.selectedArea)


class ResultPanel(wx.Panel):
    def __init__(self, parent, styles, controller, **kw):
        wx.Panel.__init__(self, parent, **kw)
        self.styles = styles
        self.SetBackgroundColour(self.styles["BackgroundColour"])
        self.SetForegroundColour(self.styles["ForegroundColour"])
        self.controller = controller
        self.model = self.controller.getModel()
        self.model.subscribe(self, "msg_new_project", self.onMsgNewProject)
        self.model.subscribe(self, "msg_open_project", self.onMsgOpenProject)
        self.model.subscribe(self, "msg_generate_complete", self.onMsgGenerateComplete)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Bind(wx.EVT_SIZE, self.onResize)

    def cleanUp(self):
        children = self.GetChildren()
        for c in children:
            c.Destroy()

    def construct(self, sizer, project):
        self.project = project

        sizer.Clear()
        self.imZmPnl = zoompanel.ZoomPanel(self, self.project, "generatedImage", self.styles, size=self.GetSize())
        self.imZmPnl.Bind(zoompanel.EVT_ZOOM_AREA, self.onAreaZoom)
        sizer.Add(self.imZmPnl, 1)
        sizer.Layout()

    def onResize(self, e):
        e.Skip()
        w,h = self.GetSize()
        self.Refresh(rect=(0,0,w,h))

    def onAreaZoom(self, e):
        log.debug(function=self.onAreaZoom)
        e.Skip()
        wx.PostEvent(self, e)

    def onMsgNewProject(self, payload):
        prj = payload["project"]
        self.cleanUp()
        self.construct(self.sizer, prj)
        self.Refresh()

    def onMsgOpenProject(self, payload):
        prj = payload["project"]
        self.cleanUp()
        self.construct(self.sizer, prj)
        self.Refresh()

    def onMsgGenerateComplete(self, payload):
        pass

    def setZoomMode(self):
        self.imZmPnl.setMode(zoompanel.MODE_ZOOM)

    def setFinishMode(self):
        self.imZmPnl.setMode(zoompanel.MODE_FINISH)

    def showNextStep(self):
        self.imZmPnl.showNextStep()

    def showPreviousStep(self):
        self.imZmPnl.showPreviousStep()

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

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
 
        self.configPnl = ProjectPropertiesPanel(self, styles, self.controller, size=(300,800))
        self.ResultPnl = ResultPanel(self, styles, self.controller, style=wx.SUNKEN_BORDER, size=(1600,1600))
        self.ResultPnl.Bind(zoompanel.EVT_ZOOM_AREA, self.configPnl.onGenerate)

        self.sizer.Add(self.configPnl, 1)
        self.sizer.Add(self.ResultPnl, 5)
        self.SetAutoLayout(True)

        self.createToolbar()
        self.createMenu()
        self.SetSizer(self.sizer)
        self.SetMinSize((800,400))
 
        self.Show()

        self.Bind(event=wx.EVT_CLOSE, handler=self.onUserCloseMainWindow)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserNewMandelbrotProject, id=ID_FILE_NEW_PROJECT_MANDELBROTPROJECT)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserNewJuliaProject, id=ID_FILE_NEW_PROJECT_JULIAPROJECT)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserSaveProject, id=ID_FILE_SAVE_PROJECT)
        self.Bind(event=wx.EVT_MENU, handler=self.onUserSaveProjectAs, id=ID_FILE_SAVE_PROJECT_AS)
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

        wx.PostEvent(self, wx.MenuEvent(wx.wxEVT_MENU, ID_FILE_NEW_PROJECT_MANDELBROTPROJECT))

    def createToolbar(self):
        toolbar = self.CreateToolBar()

        bmpOpen = wx.Image(RESOURCES+"/open.png").ConvertToBitmap()
        bmpSave = wx.Image(RESOURCES+"/save.png").ConvertToBitmap()
        bmpSaveAs = wx.Image(RESOURCES+"/save_as.png").ConvertToBitmap()
        bmpSelectImage = wx.Image(RESOURCES+"/add_photo.png").ConvertToBitmap()
        bmpGenerate = wx.Image(RESOURCES+"/play.png").ConvertToBitmap()
        bmpReset = wx.Image(RESOURCES+"/refresh.png").ConvertToBitmap()
        bmpSelectZoomMode = wx.Image(RESOURCES+"/picture_in_picture.png").ConvertToBitmap()
        bmpSelectFinishMode = wx.Image(RESOURCES+"/image.png").ConvertToBitmap()
        bmpUp = wx.Image(RESOURCES+"/north_west.png").ConvertToBitmap()

        toolbar.AddTool(ID_FILE_OPEN_PROJECT, "Open project", bmpOpen, wx.NullBitmap, wx.ITEM_NORMAL, "Open project", "Open project", None)
        toolbar.AddTool(ID_FILE_SAVE_PROJECT, "Save project", bmpSave, wx.NullBitmap, wx.ITEM_NORMAL, "Save project", "Save project", None)
        toolbar.AddTool(ID_FILE_SAVE_PROJECT_AS, "Save project as...", bmpSaveAs, wx.NullBitmap, wx.ITEM_NORMAL, "Save project as...", "Save project project under a new name", None)
        toolbar.AddSeparator()
        toolbar.AddTool(ID_PROJECT_SELECT_SOURCEIMAGE, "Select image...", bmpSelectImage, wx.NullBitmap, wx.ITEM_NORMAL, "Select image", "Select image", None)
        toolbar.AddTool(ID_PROJECT_GENERATE, "Generate", bmpGenerate, wx.NullBitmap, wx.ITEM_NORMAL, "Generate", "Generate", None)
        toolbar.AddTool(ID_PROJECT_RESET, "Reset", bmpReset, wx.NullBitmap, wx.ITEM_NORMAL, "Reset", "Reset", None)
        toolbar.AddSeparator()
        toolbar.AddTool(ID_PROJECT_SELECT_ZOOM_MODE, "Zoom mode", bmpSelectZoomMode, wx.NullBitmap, wx.ITEM_NORMAL, "Switch to zoom mode", "Switch to zoom mode", None)
        toolbar.AddTool(ID_PROJECT_SELECT_FINISH_MODE, "Zoom mode", bmpSelectFinishMode, wx.NullBitmap, wx.ITEM_NORMAL, "Switch to finish mode", "Switch to finish mode", None)
        toolbar.AddTool(ID_PROJECT_HISTORY_UP, "Zoom mode", bmpUp, wx.NullBitmap, wx.ITEM_NORMAL, "Show parent step", "Show parent step", None)

        toolbar.Realize()

        self.SetToolBar(toolbar)

    def createMenu(self):
        menuBar = wx.MenuBar()
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
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(projectMenu, "&Project")
        menuBar.Append(debugMenu, "&Debug")
        self.SetMenuBar(menuBar)

    def onUserCloseMainWindow(self, e):
        exit()

    def onUserExit(self, e):
        self.Close(True) 
        e.Skip()

    def onUserNewMandelbrotProject(self, e):
        self.controller.newMandelbrotProject("mandelbrot")
        e.Skip()

    def onUserNewJuliaProject(self, e):
        self.controller.newJuliaProject("julia")
        e.Skip()

    def onUserSaveProject(self, e):
        if self.model.getCurrentProject().getPath()!=None:
            self.controller.saveProject()
        else: 
            self.onUserSaveProjectAs(e)
        e.Skip()

    def onUserSaveProjectAs(self, e):
        path = dlg.saveProjectDialog(self)
        self.controller.saveProjectAs(path)
        e.Skip()

    def onUserSaveGeneratedImage(self, e):
        path = dlg.saveImageDialog(self)
        self.controller.saveGeneratedImage(path)
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

    def onUserOpenProject(self, e):
        path = dlg.openProjectDialog(self)
        self.controller.openProject(path)
        e.Skip()

    def onUserSelectZoomMode(self, e):
        self.ResultPnl.setZoomMode()
        e.Skip()

    def onUserSelectFinishMode(self, e):
        self.ResultPnl.setFinishMode()
        e.Skip()
    
    def onUserProjectHistoryUp(self, e):
        log.debug(function=self.onUserProjectHistoryUp)
        self.controller.getCurrentProject().up()
        e.Skip()

    def onUserShowInspectionTool(self, e):
        InspectionTool().Show()
        e.Skip()

import logging

def start():
    # configure logging
    logging.basicConfig(format='[%(name)s] %(levelname)s:%(message)s', level=logging.DEBUG)
       
    # construct the asynchronous app and run it in the main async event loop
    app = WxAsyncApp()
    loop = asyncio.get_event_loop()
    controller = Controller(Model())
    w = MainWindow(WINDOW_STYLES, controller)
    try:
        loop.run_until_complete(app.MainLoop())
    finally:
        loop.stop()
        loop.close()

if __name__ == '__main__':
    start()

