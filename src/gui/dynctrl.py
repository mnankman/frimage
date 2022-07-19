import wx
from lib.modelobject import ModelObject
from PIL import Image
from lib import log

class DynamicCtrl:
    def __init__(self, modelObject, attributeName):
        assert modelObject!=None
        assert isinstance(modelObject, ModelObject)
        assert attributeName!=None
        assert modelObject.hasAttribute(attributeName)
        self.modelObject = modelObject
        self.attributeName = attributeName
        self.modelObject.subscribe(self, "msg_object_modified", self.onModelObjectChange)

    def __del__(self):
        try:
            self.modelObject.unsubscribe(self, self.onModelObjectChange)
        except AttributeError as e:
            log.warning(e, function=self.__del__)

    def onUserValueChange(self, e):
        ctrl = e.GetEventObject()
        val = ctrl.GetValue()
        self.modelObject.setAttribute(self.attributeName, val)
        e.Skip()

    def onModelObjectChange(self, payload):
        pass

class DynamicTextCtrl(DynamicCtrl, wx.TextCtrl):
    def __init__(self, parent, modelObject, attributeName, styles, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.TextCtrl.__init__(self, parent, **kw)
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])
        self.SetValue(str(modelObject.getAttribute(self.attributeName)))
        self.Bind(wx.EVT_TEXT, self.onUserValueChange) 

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.ChangeValue(str(obj.getAttribute(self.attributeName)))

class DynamicSpinCtrl(DynamicCtrl, wx.SpinCtrl):
    def __init__(self, parent, modelObject, attributeName, styles, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.SpinCtrl.__init__(self, parent, **kw)
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])
        self.SetValue(str(modelObject.getAttribute(self.attributeName)))
        self.Bind(wx.EVT_SPINCTRL, self.onUserValueChange) 

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.SetValue(str(obj.getAttribute(self.attributeName)))

class DynamicCheckBox(DynamicCtrl, wx.CheckBox):
    def __init__(self, parent, modelObject, attributeName, styles, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.CheckBox.__init__(self, parent, **kw)
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])
        self.SetValue(modelObject.getAttribute(self.attributeName))
        self.Bind(wx.EVT_CHECKBOX, self.onUserValueChange) 

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.SetValue(obj.getAttribute(self.attributeName))

class DynamicBitmap(DynamicCtrl, wx.StaticBitmap):
    def __init__(self, parent, modelObject, attributeName, styles, autoSize=True, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        wx.StaticBitmap.__init__(self, parent, **kw)
        self.autoSize = autoSize
        self.SetBackgroundColour(styles["BackgroundColour"])
        self.SetForegroundColour(styles["ForegroundColour"])
        self.setBitmap(modelObject.getAttribute(self.attributeName), self.GetSize())

    def pilImageToWxImage(self, pilImg):
        wxImage = wx.Image(pilImg.size)
        wxImage.SetData(pilImg.convert('RGB').tobytes())
        wxImage.SetAlpha(pilImg.convert("RGBA").tobytes()[3::4])
        return wxImage

    def createEmptyWxImage(self):
        return wx.Image(self.GetSize())

    def setBitmap(self, pilImg, size=None):
        log.debug(function=self.setBitmap, args=(pilImg, size))
        if pilImg!=None:
            if size!=None and self.autoSize: 
                im = pilImg.resize(size, Image.BOX)
            else:
                im = pilImg
            wxImg = self.pilImageToWxImage(im)
        else:
            wxImg = self.createEmptyWxImage()
        self.SetBitmap(wxImg.ConvertToBitmap())
        self.Refresh()

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.setBitmap(obj.getAttribute(self.attributeName), self.GetSize())

