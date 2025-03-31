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

        name_label = Gtk.Label(label=name)
        name_label.get_style_context().add_class("wallpaper_title")
        vbox.append(name_label)

        # Images Box (Horizontal Layout)
        hbox_images = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Light Image Section
        light_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        light_box.set_hexpand(True)  # Allow horizontal expansion
        light_box.set_vexpand(True)  # Allow vertical expansion
        light_image = Gtk.Image.new_from_file(light)
        light_image.get_style_context().add_class("wallpaper_image")
        light_image.set_hexpand(True)  # Ensure image expands horizontally
        light_image.set_vexpand(True)  # Ensure image expands vertically
        light_box.append(light_image)

        # Light Buttons (Align to the right)
        btn_box_light = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        btn_box_light.set_halign(Gtk.Align.END)  # Align buttons to the right
        btn_info_light = Gtk.Button()
        btn_info_light.set_icon_name("dialog-information")  # Info icon
        btn_set_light = Gtk.Button()
        btn_set_light.set_icon_name("preferences-desktop-wallpaper")  # Wallpaper icon
        btn_box_light.append(btn_info_light)
        btn_box_light.append(btn_set_light)
        light_box.append(btn_box_light)

        # Dark Image Section
        dark_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        dark_box.set_hexpand(True)  # Allow horizontal expansion
        dark_box.set_vexpand(True)  # Allow vertical expansion
        dark_image = Gtk.Image.new_from_file(dark)
        dark_image.get_style_context().add_class("wallpaper_image")
        dark_image.set_hexpand(True)  # Ensure image expands horizontally
        dark_image.set_vexpand(True)  # Ensure image expands vertically
        dark_box.append(dark_image)

        # Dark Buttons (Align to the right)
        btn_box_dark = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        btn_box_dark.set_halign(Gtk.Align.END)  # Align buttons to the right
        btn_info_dark = Gtk.Button()
        btn_info_dark.set_icon_name("dialog-information")  # Info icon
        btn_set_dark = Gtk.Button()
        btn_set_dark.set_icon_name("preferences-desktop-wallpaper")  # Wallpaper icon
        btn_box_dark.append(btn_info_dark)
        btn_box_dark.append(btn_set_dark)
        dark_box.append(btn_box_dark)

        # Add both images and their buttons to the row
        hbox_images.append(light_box)
        hbox_images.append(dark_box)

        # Add the images section to the main vertical box
        vbox.append(hbox_images)

        # Add the final layout to the page
        page.append(vbox)

    def add_all_wallpapers(self, page, page_name):
        path = Path(__file__).parent.parent / "wallpapers" / page_name 
        json_path = f"{path}/list.json"
        with open(json_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                for e in data:
                    dark_path = f"{path}/{e["files"]}_dark.png"
                    light_path = f"{path}/{e["files"]}_light.png"
                    self.add_wallpaper(page,e["version"],e["title"],dark_path,light_path)

            except json.JSONDecodeError:
                print(f"Error decoding JSON in file: {json_path}")


def main():
    """The application's entry point."""
    app = NyarchWallpapersApplication()
    app.run(sys.argv)


main()
