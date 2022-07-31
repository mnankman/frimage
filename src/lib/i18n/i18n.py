import wx
import builtins

# setup i18n localisation for wx
builtins.__dict__['_'] = wx.GetTranslation
