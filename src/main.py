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

apppath = str(Path(__file__).parent / "ui" / "main.ui")
csspath = str(Path(__file__).parent / "ui" / "styles.css")  

class NyarchWallpapersApplication(Adw.Application):
    
    gtype_name__ = 'NyarchWallpapersWindow'

    def __init__(self):
        super().__init__(application_id='wawa.femboydownloader',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_action('quit', self.quit, ['<primary>q'])
        
    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        # Create a Builder
        builder = Gtk.Builder()
        builder.add_from_file(apppath)

        # Obtain and show the main window
        self.win = builder.get_object("main")
        self.win.set_application(self)  # Application will close once it no longer has active windows attached to it
        self.win.set_title("Nyarch Wallpapers")

        # Load the CSS from the styles.css file
        self.load_css()

        # Connect the widgets from the UI
        self.nyarch_wallpapers_box = builder.get_object("nyarch-wallpapers")
        self.release_wallpapers_box = builder.get_object("release-wallpapers")
        self.gnome_wallpapers_box = builder.get_object("gnome-wallpapers")

        # Optionally, we can set some widgets to display content in these boxes, e.g., for example, adding labels or images.
        # Here we can also create placeholders to demonstrate functionality.

        self.nyarch_wallpapers_box.append(Gtk.Label(label="This is the nyarch wallpapers tab"))
        self.release_wallpapers_box.append(Gtk.Label(label="This is the releases wallpapers tab"))
        self.gnome_wallpapers_box.append(Gtk.Label(label="This is the gnome wallpapers tab"))

        self.win.show()
    
    def load_css(self):
        """Load and apply the CSS stylesheet."""
        # Create a CSS provider and load the CSS file
        css_provider = Gtk.CssProvider()
        try:
            # Load the CSS file
            css_provider.load_from_path(csspath)
            # Apply the CSS to the default display (for GTK 4)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"Failed to load CSS file: {e}")
        
    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

def main():
    """The application's entry point."""
    app = NyarchWallpapersApplication()
    app.run(sys.argv)


main()
