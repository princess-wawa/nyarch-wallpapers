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
        self.nyarch_box = builder.get_object("nyarch-wallpapers")
        self.release_box = builder.get_object("release-wallpapers")
        self.gnome_box = builder.get_object("gnome-wallpapers")

        self.add_all_wallpapers(self.release_box, "updates")

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

    def add_wallpaper(self, page, version, name, dark, light):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        # Version and Name Labels
        version_label = Gtk.Label(label=version)
        version_label.get_style_context().add_class("wallpaper_version")
        vbox.append(version_label)

        if name != None:
            name_label = Gtk.Label(label=name)
            name_label.get_style_context().add_class("wallpaper_title")
            vbox.append(name_label)

        # Images Box (Horizontal Layout)
        hbox_images = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_images.set_hexpand(True)

        # Function to create image section
        def create_image_section(image_path):
            # Main container
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            box.set_hexpand(True)
            
            # Image container with aspect ratio enforcement
            image_container = Gtk.AspectFrame(
                ratio=16/9,  # 16:9 aspect ratio
                obey_child=False
            )
            image_container.set_hexpand(True)
            
            # The actual image
            picture = Gtk.Picture.new_for_filename(image_path)
            picture.set_content_fit(Gtk.ContentFit.COVER)
            picture.set_size_request(-1, 250)  # Minimum height
            
            image_container.set_child(picture)
            box.append(image_container)
            
            # Buttons
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            btn_box.set_halign(Gtk.Align.END)
            btn_info = Gtk.Button(icon_name="dialog-information")
            btn_set = Gtk.Button(icon_name="preferences-desktop-wallpaper")
            btn_box.append(btn_info)
            btn_box.append(btn_set)
            box.append(btn_box)
            
            return box

        # Add both image sections
        hbox_images.append(create_image_section(light))
        hbox_images.append(create_image_section(dark))

        # Assemble the layout
        vbox.append(version_label)
        vbox.append(hbox_images)
        page.append(vbox)

    def add_all_wallpapers(self, page, page_name):
        path = Path(__file__).parent.parent / "wallpapers" / page_name 
        json_path = f"{path}/list.json"
        with open(json_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                for e in data:
                    dark_path = jpg_or_png(f"{path}/{e["files"]}_dark")
                    light_path = jpg_or_png(f"{path}/{e["files"]}_light")
                    self.add_wallpaper(page,e["version"],e["title"],dark_path,light_path)

            except json.JSONDecodeError:
                print(f"Error decoding JSON in file: {json_path}")
    
def jpg_or_png(path):    
    if os.path.exists(f"{path}.jpg"):
        return f"{path}.jpg"
    return f"{path}.png"


def main():
    """The application's entry point."""
    app = NyarchWallpapersApplication()
    app.run(sys.argv)


main()
