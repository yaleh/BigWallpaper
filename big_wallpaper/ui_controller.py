from gi.repository import Gio, Gtk, GObject, AppIndicator3, Notify
from models import *


class AnimationTimer:

    """
    Timer of icon animation.
    """

    def __init__(self, ui_controller, interval, icons):
        """
        Constructor of AnimationTimer.
        """

        self.interval = interval
        self.icons = icons
        self.current_icon_index = 0
        self.ui_controller = ui_controller

        self.ui_controller.update_appindicator(
            self.icons[self.current_icon_index])

        self.timer_id = GObject.timeout_add(self.interval, self.on_timer)

    def cancel(self):
        """
        Cancel animation.
        """

        GObject.source_remove(self.timer_id)
        self.timer_id = None

    def on_timer(self):
        """
        Callback of timer.

        Show the next icon.
        """

        try:
            self.current_icon_index += 1
            self.current_icon_index %= len(self.icons)

            self.ui_controller.update_appindicator(
                self.icons[self.current_icon_index])
        finally:
            return True  # continue


class UIController:

    """
    UI controller for GTK.
    """

    ICON_FILE = 'big_wallpaper_small.png'
    UPDATING_ICON_FILES = ['big_wallpaper_updating_1.png',
                           'big_wallpaper_updating_2.png',
                           'big_wallpaper_updating_3.png',
                           'big_wallpaper_updating_4.png',
                           'big_wallpaper_updating_5.png']

    def __init__(self, manager, config, icon_dir=None):
        """
        Constructor of UIController.
        """

        # global manager, config

        self.manager = manager
        self.config = config

        self.manager.set_controller(self)
        self.animation_timer = None

        self.icon_dir = icon_dir

        self.ind = AppIndicator3.Indicator.new(
            "BigWallpaper",
            "%s/%s" % (self.icon_dir, self.ICON_FILE),
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.update_menu()

    def update_menu(self):
        """
        Update the menu.

        Update menu with following status:
        * Current wallpaper
        * Downloading status
        * Auto-start setting
        """

        # create a menu
        self.menu = Gtk.Menu()

        image = None
        image_title = 'No Image'

        try:
            image = Image.get(Image.active_wallpaper == True)
        except Image.DoesNotExist:
            pass
        else:
            image_title = "%s (%s)" % (
                image.source_title, image.source_site.name)

        image_item = Gtk.MenuItem(image_title)
        if image is not None and image.source_link is not None:
            image_item.connect("activate",
                               lambda obj: Gtk.show_uri(
                                   None, image.source_link,
                               Gtk.get_current_event_time()))
        else:
            image_item.set_sensitive(False)

        self.update_item = Gtk.MenuItem('Update Now')
        self.update_item.connect("activate",
                                 lambda obj: self.manager.update())

        auto_start_item = Gtk.CheckMenuItem('Start with System')
        auto_start_item.set_active(self.manager.get_autostart())
        auto_start_item.connect(
            "toggled",
            lambda obj:
            self.manager.update_autostart(auto_start_item.get_active()))

        save_item = Gtk.MenuItem("Save Preference")
        save_item.connect("activate",
                          lambda obj: self.config.save())

        self.sep_item = Gtk.SeparatorMenuItem()

        quit_item = Gtk.MenuItem('Quit')
        quit_item.connect("activate", Gtk.main_quit)

        self.menu.append(image_item)
        self.menu.append(Gtk.SeparatorMenuItem())
        self.menu.append(self.update_item)
        self.menu.append(self.auto_start_item)
        self.menu.append(save_item)
        self.menu.append(Gtk.SeparatorMenuItem())
        self.menu.append(quit_item)
        self.menu.show_all()

        self.ind.set_menu(self.menu)

    def start_updating(self):
        """
        Start updating.

        Update menu item. Start animation.
        """

        self.update_item.set_sensitive(False)
        self.update_item.set_label("Updating...")

        self.animation_timer = AnimationTimer(
            self, 500,
            map(lambda s: "%s/%s" % (self.icon_dir, s),
                self.UPDATING_ICON_FILES))

    def finish_updating(self):
        """
        Finish updating.

        Update menu itme. Stop animation.
        """

        self.update_item.set_sensitive(True)
        self.update_item.set_label("Update Now")

        if self.animation_timer is not None:
            self.animation_timer.cancel()
            self.animation_timer = None

        self.ind.set_icon("%s/%s" % (self.icon_dir, self.ICON_FILE))

    def update_appindicator(self, icon):
        """
        Update appindicator for icon animation.
        """

        self.ind.set_icon(icon)

    def show_message_dialog(self, title, message):
        """
        DEFUNCT. Message dialog on setting a new wallpaer.
        """

        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def notify_wallpaper_update(self, image):
        """
        Notification popup on setting a new wallpaper.
        """

        if not Notify.init("BigWallpaper"):
            return
        n = Notify.Notification.new("A new wallpaper by BigWallpaper",
                                    image.source_title,
                                    image.image_path)
        n.show()
        self.update_menu()
