import wx
from wxasync import StartCoroutine
import wx.lib.progressindicator as progress

from lib import log

from core.model.complex import JuliaProject, GeneratedSet
import lib.wxdyn.dynctrl as dynctrl 
import gui.zoompanel as zoompanel
import random
        
RESOURCES="resource"

class ProjectPanel(wx.Panel):
    def __init__(self, parent, styles, controller, **kw):
        super(ProjectPanel, self).__init__(parent, **kw)    
        self.styles = styles
        self.SetBackgroundColour(self.styles["BackgroundColour"])
        self.SetForegroundColour(self.styles["ForegroundColour"])

        self.controller = controller
        self.model = self.controller.getModel()
        self.model.subscribe(self, "msg_new_project", self.onUpdate)
        self.model.subscribe(self, "msg_open_project", self.onUpdate)

    def cleanUp(self):
        children = self.GetChildren()
        for c in children:
            self.RemoveChild(c)

    def construct(self, project):
        pass

    def onUpdate(self, payload):
        #self.cleanUp()
        if "project" in payload.keys():            
            prj = payload["project"]
        elif "object" in payload.keys():
            prj = payload["object"]
        else:
            return
        self.construct(prj)
        if prj != self.controller.getCurrentProject():
            prj.subscribe(self, "msg_object_modified", self.onUpdate)
        self.Refresh()

class StatusBar(ProjectPanel):
    def __init__(self, parent, styles, controller, **kw):
        super(StatusBar, self).__init__(parent, styles, controller, **kw)    
        self.SetBackgroundColour("#444444")
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.SetAutoLayout(True)
        
    def construct(self, project):
        log.debug(function=self.construct, args=project.getFullId())
        self.project = project
        self.sizer.Clear(True)
        gridsizer = wx.FlexGridSizer(1,3,5,0)
        self.progressBar = progress.ProgressIndicator(self)
        gridsizer.AddMany([
            (dynctrl.DynamicLabel(self, self.project, "path", self.styles), 1, wx.ALIGN_BOTTOM),
            (dynctrl.DynamicLabel(self, self.project, "saved", self.styles, valuemapping={False: "*", True: ""}), 1, wx.ALIGN_BOTTOM),
        ])
        self.sizer.Add(gridsizer, 10)
        self.sizer.Add(self.progressBar, 0, wx.EXPAND | wx.ALL, 0)
        
        self.sizer.Layout()

    def onProgress(self, generator, p):
        self.progressBar.SetValue(p)

    def onGenerate(self, e):
        if isinstance(e, zoompanel.ZoomAreaEvent):
            self.selectedArea = e.area
        else:
            self.selectedArea = None
        self.progressBar.Start()
        StartCoroutine(self.generate, self)
        e.Skip()

    async def generate(self):
        await self.controller.generate(self.onProgress, area=self.selectedArea)


class ProjectExplorerPanel(ProjectPanel):
    def __init__(self, parent, styles, controller, **kw):
        super(ProjectExplorerPanel, self).__init__(parent, styles, controller, **kw)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.SetAutoLayout(True)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetSize(self.GetParent().GetSize())
        self.sizer.Layout()

    def construct(self, project):
        log.debug(function=self.construct, args=project.getFullId())
        self.project = project
        self.sizer.Clear(True)
        self.projectTree = wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, self.GetSize(), wx.TR_HAS_BUTTONS)
        self.projectTree.SetBackgroundColour(self.styles["BackgroundColour"])
        self.projectTree.SetForegroundColour(self.styles["ForegroundColour"])
        rootset = self.project.getRootSet()
        root = self.projectTree.AddRoot(rootset.getName())
        self.constructTree(root, rootset)
        self.projectTree.ExpandAll()
        self.sizer.Add(self.projectTree, 100)
        self.sizer.Layout()

    def constructTree(self, parentItem, genset):
        log.debug(function=self.constructTree, args=(parentItem, genset.getFullId()))
        for gs in genset.getGeneratedSets():
            item = self.projectTree.AppendItem(parentItem, gs.getName())
            self.constructTree(item, gs)
    
 
class ProjectPropertiesPanel(ProjectPanel):
    def __init__(self, parent, styles, controller, **kw):
        super(ProjectPropertiesPanel, self).__init__(parent, styles, controller, **kw)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        w,h=self.GetSize()
        gridsizer = wx.FlexGridSizer(1, gap=(5, 5))
        btnNewMandelbrot = wx.Button(self, label=_("New Mandelbrot project"), size=(w*0.8, 30), style=wx.CENTER)
        btnNewJulia = wx.Button(self, label=_("New Julia project"), size=(w*0.8, 30), style=wx.CENTER)
        gridsizer.Add(btnNewMandelbrot, 1)
        gridsizer.Add(btnNewJulia, 1)
        btnNewMandelbrot.Bind(wx.EVT_BUTTON, self.onNewMandelbrotProject)
        btnNewJulia.Bind(wx.EVT_BUTTON, self.onNewJuliaProject)
        self.sizer.AddSpacer(40)
        self.sizer.Add(gridsizer, 1, flag=wx.ALIGN_CENTER_HORIZONTAL)
        self.SetAutoLayout(True)
        self.Bind(wx.EVT_SIZE, self.onResize)
        self.sizer.Layout()

    def construct(self, project):
        self.project = project
        self.area = self.project.getArea()
        self.projectSource = self.project.getProjectSource()

        self.sizer.Clear(True)
        gridsizer1 = wx.FlexGridSizer(2, gap=(5, 5))
        
        lbl4_1 = wx.StaticText(self, label="project name:", size=(120, 20))
        lbl4_2 = wx.StaticText(self, label="project artist:", size=(120, 20))
        textCtrl4_1 = dynctrl.DynamicTextCtrl(self, self.project, "name", self.styles, size=(150, 24))
        textCtrl4_2 = dynctrl.DynamicTextCtrl(self, self.project, "artist", self.styles, size=(150, 24))
        im1 = dynctrl.DynamicBitmap(self, self.projectSource, "sourceImage", self.styles, size=(150,150))
        im1.SetScaleMode(wx.StaticBitmap.Scale_AspectFit)
        im2 = dynctrl.DynamicBitmap(self, self.projectSource, "heatmapBaseImage", self.styles, size=(150,150))
        im2.SetScaleMode(wx.StaticBitmap.Scale_AspectFit)
        im3 = dynctrl.DynamicBitmap(self, self.projectSource, "gradientImage", self.styles, size=(150,20))
        im3.SetScaleMode(wx.StaticBitmap.Scale_Fill)
        chkBox1 = dynctrl.DynamicCheckBox(self, self.projectSource, "flipGradient", self.styles, label="flip gradient:")
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
        gridsizer1.AddMany([
            (lbl4_1, 1), (textCtrl4_1, 1), 
            (lbl4_2, 1), (textCtrl4_2, 1),
            (im1, 1), (im2, 1), 
            (im3, 1), (chkBox1, 1),
            (lbl1_1, 1), (textCtrl1_1, 1), 
            (lbl1_2, 1), (textCtrl1_2, 1), 
            (lbl2_1, 1), (textCtrl2_1, 1), 
            (lbl2_2, 1), (textCtrl2_2, 1), 
            (lbl3_1, 1), (textCtrl3_1, 1), 
            (lbl3_2, 1), (textCtrl3_2, 1)
        ])
        self.sizer.Add(gridsizer1, 1)
        self.sizer.AddSpacer(10)

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
            self.sizer.AddSpacer(10)

        gridsizer4 = wx.FlexGridSizer(1, gap=(5, 5))

        pw,ph = self.GetSize()
        chkPreview = dynctrl.DynamicCheckBox(self, self.project, "preview", self.styles, label="preview:")
        chkPreview.Bind(wx.EVT_CHECKBOX, self.onPreviewCheckboxChanged)
        imgPreview = dynctrl.DynamicBitmap(self, self.project, "previewImage", self.styles, False, size=(150,150))
        imgPreview.SetScaleMode(wx.StaticBitmap.Scale_Fill)
        if isinstance(project, JuliaProject):
            btnRandomCxy = wx.Button(self, label=_("Random Cx & Cy"), size=(pw, 18))
            btnRandomCxy.Bind(wx.EVT_BUTTON, self.onRandomCxy)
            gridsizer4.Add(btnRandomCxy, 1)
        gridsizer4.Add(chkPreview, 1)
        gridsizer4.Add(imgPreview, 1)
        
        self.sizer.Add(gridsizer4, 1)
        self.sizer.Layout()

    def onResize(self, e):
        e.Skip()
        w,h = self.GetSize()
        self.Refresh(rect=(0,0,w,h))

    def onPreviewCheckboxChanged(self, e):
        obj = e.GetEventObject()
        if obj.IsChecked():
            StartCoroutine(self.controller.startPreview, self)
        e.Skip()

    def onReset(self, e):
        self.project.reset()
        e.Skip()

    def onNewMandelbrotProject(self, e):
        self.controller.newMandelbrotProject("mandelbrot")
        e.Skip()

    def onNewJuliaProject(self, e):
        self.controller.newJuliaProject("julia")
        e.Skip()

    def onRandomCxy(self, e):
        self.project.setCxy((random.random() * 2.0 - 1.0, random.random() - 0.5))


class ResultPanel(ProjectPanel):
    def __init__(self, parent, styles, controller, **kw):
        super(ResultPanel, self).__init__(parent, styles, controller, **kw)
        self.model.subscribe(self, "msg_generate_complete", self.onMsgGenerateComplete)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Bind(wx.EVT_SIZE, self.onResize)

    def construct(self, project):
        self.project = project
        self.sizer.Clear(True)
        self.imZmPnl = zoompanel.ZoomPanel(self, self.project, "generatedImage", self.styles)
        self.imZmPnl.Bind(zoompanel.EVT_IMAGE_UPDATED, self.onImageUpdated)
        self.imZmPnl.Bind(zoompanel.EVT_ZOOM_AREA, self.onAreaZoom)
        self.imZmPnl.Bind(zoompanel.EVT_DIVEDOWN, self.onDiveDown)
        self.sizer.Add(self.imZmPnl, 1)
        self.sizer.Layout()

    def onResize(self, e):
        e.Skip()
        w,h = self.GetSize()

        self.Refresh(rect=(0,0,w,h))

    def onImageUpdated(self, e):
        log.debug(function=self.onImageUpdated)
        e.Skip()
        wx.PostEvent(self, e)

    def onAreaZoom(self, e):
        log.debug(function=self.onAreaZoom)
        e.Skip()
        wx.PostEvent(self, e)

    def onDiveDown(self, e):
        log.debug(function=self.onDiveDown)
        e.Skip()
        wx.PostEvent(self, e)

    def onMsgGenerateComplete(self, payload):
        pass

    def setZoomMode(self):
        self.imZmPnl.setMode(zoompanel.MODE_ZOOM)

    def setFinishMode(self):
        self.imZmPnl.setMode(zoompanel.MODE_FINISH)

    def toggleFitImage(self):
        self.imZmPnl.setScaleToFit(not self.imZmPnl.getScaleToFit())

    def showNextStep(self):
        self.imZmPnl.showNextStep()

    def showPreviousStep(self):
        self.imZmPnl.showPreviousStep()

    def saveCurrentImage(self, path):
        self.imZmPnl.saveImage(path)
