import sys
import gi
import threading
import json
from pathlib import Path
import time
import os

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw, GdkPixbuf, GLib, Gdk

apppath = str(Path(__file__).parent.parent / "ui" / "main.ui") 

class NyarchWallpapersApplication(Adw.Application):
    pass

def main():
    """The application's entry point."""
    app = NyarchWallpapersApplication()
    app.run(sys.argv)
    
main()
