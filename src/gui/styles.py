import wx
from lib.wxdyn import styler

def init():
    styleCat = styler.StyleCatalog.getInstance()
    
   
    """
    Style definitions for Anything
    """
    
    styleCat.addStyle(
        styleName = "Anything:normal",
        elements=[
            styler.Colors(foreground="#ffffff", background="#333333")
        ],
    )

    """
    Style definitions for TabCtrl
    """
    
    styleCat.addStyle(
        styleName = "TabCtrl:normal",
        basedOn = "Anything:normal",
        elements=[
            styler.Colors(background="#444444")
        ],
    )

    """
    Style definitions for StatusBar
    """
    
    styleCat.addStyle(
        styleName = "StatusBar:normal",
        basedOn = "Anything:normal",
        elements=[
            styler.Colors(background="#444444")
        ],
    )

    """
    Style definitions for Button
    """
    
    styleCat.addStyle(
        styleName = "Button:normal", 
        basedOn = "Button:normal",
        elements = [
            wx.Brush("#444444", style=wx.BRUSHSTYLE_SOLID),
            wx.Pen("#444444", style=wx.PENSTYLE_SOLID),
        ],
    )

    styleCat.addStyle(
        styleName = "Button:mouseOver", 
        basedOn = "Button:normal",
        elements = [
            wx.Brush("#555555", style=wx.BRUSHSTYLE_SOLID),
            wx.Pen("#555555", style=wx.PENSTYLE_SOLID),
        ],
    )

    styleCat.addStyle(
        styleName = "Button:selected", 
        basedOn = "Button:normal",
        elements = [
            wx.Brush("#333333", style=wx.BRUSHSTYLE_SOLID),
            wx.Pen("#333333", style=wx.PENSTYLE_SOLID),
        ],
    )

    styleCat.addStyle(
        styleName = "TabButton:highlight", 
        basedOn = "Button:normal",
        elements = [
            wx.Brush("#FFFFFF", style=wx.BRUSHSTYLE_SOLID),
            wx.Pen("#FFFFFF", style=wx.PENSTYLE_SOLID),
        ],
    )
    
    
    """
    Style definitions for ZoomPanel
    """
    
    styleCat.addStyle(
        styleName = "ZoomPanel:normal", 
        basedOn = "Anything:normal",
        elements = [
            wx.Pen("#ffffff", style=wx.PENSTYLE_SOLID),
            wx.Brush("#ffffff", style=wx.BRUSHSTYLE_SOLID),
            styler.Colors(textForeground="White")
        ],
    )

