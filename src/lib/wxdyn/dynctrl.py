import wx
from .modelobject import ModelObject
from PIL import Image
import lib.wxdyn.log as  log
import lib.wxdyn as wxdyn

class DynamicCtrl:
    def __init__(self, modelObject, attributeName):
        assert modelObject!=None
        assert isinstance(modelObject, ModelObject)
        assert attributeName!=None
        assert modelObject.hasAttribute(attributeName)
        self.paintStyler = wxdyn.PaintStyler()
        self.modelObject = modelObject
        self.attributeName = attributeName
        self.modelObject.subscribe(self, "msg_object_modified", self.onModelObjectChange)

    def __del__(self):
        try:
            self.modelObject.unsubscribe(self.onModelObjectChange, "msg_object_modified")
        except AttributeError as e:
            log.warning(e, function=self.__del__)

    def onUserValueChange(self, e):
        ctrl = e.GetEventObject()
        val = ctrl.GetValue()
        self.modelObject.setAttribute(self.attributeName, val)
        e.Skip()

    def onModelObjectChange(self, payload):
        pass

class DynamicLabel(DynamicCtrl, wx.StaticText):
    def __init__(self, parent, modelObject, attributeName, **kw):
        self.valueMap = {}
        kw2={}
        for k,v in kw.items():
            if k=="valuemapping":
                assert isinstance(v, dict)
                self.valueMap = v
            else:
                kw2[k]=v
        DynamicCtrl.__init__(self, modelObject, attributeName)
        super(wx.StaticText, self).__init__(parent, **kw2)
        attrVal = modelObject.getAttribute(self.attributeName)
        if attrVal in self.valueMap:
            self.SetLabel(str(self.valueMap[attrVal]))
        else:
            self.SetLabel(str(attrVal))

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        attrVal = obj.getAttribute(self.attributeName)
        if attrVal in self.valueMap:
            self.SetLabel(str(self.valueMap[attrVal]))
        else:
            self.SetLabel(str(attrVal))

class DynamicTextCtrl(DynamicCtrl, wx.TextCtrl):
    def __init__(self, parent, modelObject, attributeName, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        super(wx.TextCtrl, self).__init__(parent, **kw)
        self.SetValue(str(modelObject.getAttribute(self.attributeName)))
        self.Bind(wx.EVT_TEXT, self.onUserValueChange) 

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.ChangeValue(str(obj.getAttribute(self.attributeName)))

class DynamicSpinCtrl(DynamicCtrl, wx.SpinCtrl):
    def __init__(self, parent, modelObject, attributeName, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        super(wx.SpinCtrl, self).__init__(parent, **kw)
        self.SetValue(str(modelObject.getAttribute(self.attributeName)))
        self.Bind(wx.EVT_TEXT, self.onUserValueChange) 
        self.Bind(wx.EVT_SPINCTRL, self.onUserValueChange) 

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.SetValue(int(obj.getAttribute(self.attributeName)))

class DynamicCheckBox(DynamicCtrl, wx.CheckBox):
    def __init__(self, parent, modelObject, attributeName, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        super(wx.CheckBox, self).__init__(parent, **kw)
        self.SetValue(modelObject.getAttribute(self.attributeName))
        self.Bind(wx.EVT_CHECKBOX, self.onUserValueChange) 

    def onModelObjectChange(self, payload):
        obj = payload["object"]
        self.SetValue(obj.getAttribute(self.attributeName))

class DynamicBitmap(DynamicCtrl, wx.StaticBitmap):
    def __init__(self, parent, modelObject, attributeName, autoSize=True, **kw):
        DynamicCtrl.__init__(self, modelObject, attributeName)
        super(wx.StaticBitmap, self).__init__(parent, **kw)
        self.autoSize = autoSize
        self.setBitmap(modelObject.getAttribute(self.attributeName), self.GetSize())

    def pilImageToWxImage(self, pilImg):
        wxImage = wx.Image(pilImg.size)
        wxImage.SetData(pilImg.convert('RGB').tobytes())
        wxImage.SetAlpha(pilImg.convert("RGBA").tobytes()[3::4])
        return wxImage

    def createEmptyWxImage(self):
        return wx.Image(self.GetSize())

    def setBitmap(self, pilImg, size=None):
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

