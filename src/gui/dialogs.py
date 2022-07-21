import imp
import wx
from lib import log
from gui import i18n

DEFAULT_DIR = "."

FILESPEC_IMAGES = {
    "jpg": _("JPEG Images"),
    "png": _("PNG Images"),
}

FILESPEC_PNG = {
    "png": _("PNG Images")
}

FILESPEC_PROJECT = {
    "igp": _("Image Generation Project files")
}

def toWildCardString(filespec=None):
    wildCardStr = ""
    for e, d in filespec.items():
        str = "{desc} (*.{ext})|*.{ext}"
        if len(wildCardStr)==0:
            wildCardStr = str.format(desc=d, ext=e)
        else:
            wildCardStr += "|" + str.format(desc=d, ext=e)
    return wildCardStr

def fileDialog(parentFrame, **kw):
    dlg = wx.FileDialog(parentFrame, **kw)
    if dlg.ShowModal() == wx.ID_CANCEL:
        return
    path = dlg.GetPath()
    dlg.Destroy()
    return path

def openFileDialog(parentFrame, **kw):
    return fileDialog(parentFrame, style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST, **kw)

def saveFileDialog(parentFrame, **kw):
    return fileDialog(parentFrame, style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, **kw)

def openProjectDialog(parentFrame):
    return openFileDialog(parentFrame, 
        message = _("Open Project"), 
        wildcard = toWildCardString(FILESPEC_PROJECT))

def saveProjectDialog(parentFrame):
    return saveFileDialog(parentFrame, 
        message = _("Open Project"), 
        wildcard = toWildCardString(FILESPEC_PROJECT))

def openImageDialog(parentFrame):
    return openFileDialog(parentFrame, 
        message = _("Open Image"), 
        wildcard = toWildCardString(FILESPEC_IMAGES))

def saveImageDialog(parentFrame):
    return saveFileDialog(parentFrame, 
        message = _("Open Image"), 
        wildcard = toWildCardString(FILESPEC_PNG))

def message(message, style=wx.OK):
    return Messages.getInstance().message(message, style)

class Messages:
    __instance__ = None
    def getInstance():
        if Messages.__instance__ == None:
            Messages.__instance__ = Messages.__Messages__()
        return Messages.__instance__

    def setWindow(window):
        Messages.getInstance().setWindow(window)

    class __Messages__:
        def __init__(self):
            self.__window__ = None

        def getWindow(self):
            return self.__window__

        def setWindow(self, window):
            assert isinstance(window, wx.Window)
            self.__window__ = window

        def message(self, message, style):
            if self.__window__ != None:
                dlg = wx.MessageDialog(self.__window__, message, style=style)
                return dlg.ShowModal()
            else:
                log.error("window == None", function=self.message)
                return None

