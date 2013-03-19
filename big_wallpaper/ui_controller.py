from gi.repository import Gio, Gtk, GObject, AppIndicator3, Notify

class AnimationTimer:
    def __init__(self, ui_controller, interval, icons):
        self.interval = interval
        self.icons = icons
        self.current_icon_index = 0
        self.ui_controller = ui_controller
        
        self.ui_controller.update_appindicator( \
            self.icons[self.current_icon_index])

        self.timer_id = GObject.timeout_add(self.interval, self.on_timer)

    def cancel(self):
        GObject.source_remove(self.timer_id)
        self.timer_id = None

    def on_timer(self):
        try:
            self.current_icon_index += 1
            self.current_icon_index %= len(self.icons)

            self.ui_controller.update_appindicator( \
                self.icons[self.current_icon_index])
        finally:
            return True # continue

class UIController:
    ICON_FILE = 'big_wallpaper_small.png'
    UPDATING_ICON_FILES = ['big_wallpaper_updating_1.png',
                           'big_wallpaper_updating_2.png',
                           'big_wallpaper_updating_3.png',
                           'big_wallpaper_updating_4.png',
                           'big_wallpaper_updating_5.png']
    
    def __init__(self, manager, config, icon_dir=None):
        # global manager, config

        self.manager = manager
        self.config = config

        self.manager.set_controller(self)
        self.animation_timer = None

        self.icon_dir = icon_dir

        self.ind = AppIndicator3.Indicator.new ( \
            "BigWallpaper",
            "%s/%s" % (self.icon_dir, self.ICON_FILE),
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status (AppIndicator3.IndicatorStatus.ACTIVE)

        # create a menu
        self.menu = Gtk.Menu()

        self.update_item = Gtk.MenuItem('Update Now')
        self.update_item.connect("activate",
                                 lambda obj: self.manager.update())

        self.auto_start_item = Gtk.CheckMenuItem('Start with System')
        self.auto_start_item.set_active(self.manager.get_autostart())
        self.auto_start_item.connect( \
            "toggled",
            lambda obj: \
                self.manager.update_autostart(self.auto_start_item.get_active()))

        self.save_item = Gtk.MenuItem("Save Preference")
        self.save_item.connect("activate",
                               lambda obj: self.config.save())

        self.sep_item = Gtk.SeparatorMenuItem()

        self.quit_item = Gtk.MenuItem('Quit')
        self.quit_item.connect("activate", Gtk.main_quit)

        self.menu.append(self.update_item)
        self.menu.append(self.auto_start_item)
        self.menu.append(self.save_item)
        self.menu.append(self.sep_item)
        self.menu.append(self.quit_item)
        self.menu.show_all()

        self.ind.set_menu(self.menu)

    def start_updating(self):
        self.update_item.set_sensitive(False)
        self.update_item.set_label("Updating...")

        self.animation_timer = AnimationTimer( \
            self, 500,
            map(lambda s: "%s/%s" % (self.icon_dir, s),
                self.UPDATING_ICON_FILES) )

    def finish_updating(self):
        self.update_item.set_sensitive(True)
        self.update_item.set_label("Update Now")

        if self.animation_timer is not None:
            self.animation_timer.cancel()
            self.animation_timer = None

        self.ind.set_icon("%s/%s" % (self.icon_dir, self.ICON_FILE))

    def update_appindicator(self, icon):
        self.ind.set_icon(icon)

    def show_message_dialog(self, title, message):
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def notify_wallpaper_update( \
        self, title="New Wallpaper",
        body="A new wallpaper was updated by BigWallpaper."):
        if not Notify.init ("BigWallpaper"):
            return
        n = Notify.Notification.new(title, body,
                                    "dialog-information")
        n.show ()
