import asyncio
from wx import *
from wxasync import WxAsyncApp

from core.model.model import Model
from core.controller import Controller
import gui.dialogs as dlg
from mainwindow import MainWindow
        

WINDOW_STYLES = {
    "BackgroundColour": "#333333",
    "ForegroundColour": "#FFFFFF"
}
import logsetup
def start():
    logsetup.setup(logsetup.SETUP_PRODUCTION)       

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
