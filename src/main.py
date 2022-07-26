import asyncio
import wx
from wxasync import WxAsyncApp
import logging

from lib import log
from core.model.model import Model
from core.controller import Controller
import gui.dialogs as dlg
import gui.i18n
from mainwindow import MainWindow
        

WINDOW_STYLES = {
    "BackgroundColour": "#333333",
    "ForegroundColour": "#FFFFFF"
}

def start():
    # configure logging
    logging.basicConfig(format='[%(name)s] %(levelname)s:%(message)s', level=logging.ERROR)
       
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
