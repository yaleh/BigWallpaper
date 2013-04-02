from download_thread import DownloadThread
from gi.repository import Gio, GObject
from models import *
from storm.expr import And
from datetime import datetime, timedelta

import os
import tempfile

from big_wallpaper.download_thread import DownloadThread

class WallPaperManager:
    """
    Manager of dowloading thread, content and settings.

    Manager must created before Controller
    """

    SCHEMA = 'org.gnome.desktop.background'
    KEY = 'picture-uri'
    IMG_FILE = "big_wallpaper.jpg"
    URL_FILE = "big_wallpaper.url"
    DESKTOP_FILE = "big_wallpaper.desktop"
    AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")

    def __init__(self, config, prefix_dir="share", img_dir='share/pixmaps'):
        """
        Constructor of WallPaperManager.

        prefix_dir: the installation folder of big_wallpaper
        img_dir: path to save downloaded images
        """
        self.config = config
        self.update_lock = None
        self.prefix_dir = prefix_dir
        self.img_dir = img_dir

        self.url_file = "%s/%s" % (self.img_dir, self.URL_FILE)
        self.desktop_source_file = \
            "%s/%s" % (self.prefix_dir, self.DESKTOP_FILE)
        self.autostart_desktop_file = \
            "%s/%s" % (self.AUTOSTART_DIR, self.DESKTOP_FILE)
        self.wp_url = None
        self.saved_url = None
        self.ui_controller = None

    def set_controller(self, ui_controller):
        """
        Set UI controller.

        Controller is created with WallPaperManager. And WallPaperManager needs to know
        controller with this method after the controller was created.
        """
        self.ui_controller = ui_controller

    def get_autostart(self):
        """
        Find out whether auto start is enabled.
        """
        return os.access(self.autostart_desktop_file, os.F_OK)
                       
    def update_autostart(self, autostart):
        """
        Enable/disable auto start.
        """
        try:
            os.unlink(self.autostart_desktop_file)
        except OSError:
            pass

        if autostart:
            f_source = open(self.desktop_source_file, "r")
            f_dest = open(self.autostart_desktop_file, "w")
            try:
                f_dest.write(f_source.read())
            finally:
                f_source.close()
                f_dest.close()

    def delete_expired_images(self):
        """
        Delete all images with state of STATE_EXPIRED.
        """

        for old_image in store().find(Image, Image.state == Image.STATE_EXPIRED):
            if old_image.image_path is not None:
                try:
                    os.unlink(old_image.image_path)
                except (IOError, OSError):
                    pass

            old_image.state = Image.STATE_DELETED
            old_image.active_wallpaper = False

            store().flush()
            store().commit()

    def update_wallpaper_record(self, image):
        """
        Update DB records of the wallpaper image.
        """

        image.active_wallpaper = True
        if image.active_time is not None:
            image.active_time = datetime.now()
        store().flush()
        store().commit()

    def estimate_next_image(self):
        """
        Estimate the time when the next image will downloaded.
        """

        keep_timestamp = datetime.now() - timedelta(seconds=self.config.get_options().keep)
        queued_images = store().find(Image,
                                     And(Image.state == Image.STATE_DOWNLOADED,
                                         Image.download_time >= keep_timestamp,
                                         Image.active_wallpaper == False))
        if queued_images.count() == 0:
            return datetime.now() + timedelta(seconds=self.config.get_options().keep)

        return datetime.now() + timedelta(seconds=self.config.get_options().keep) / queued_images.count()

    def update_wallpaper(self):
        """
        Find out the wallpaper image and set it.
        """

        try:
            image = self.get_wallpaper_image()
            print "New wallpaper image: %s" % image.image_path
            if image is not None:
                self.update_gsettings(image)
        finally:
            store().close()

    def get_wallpaper_image(self):
        """
        Find out the wallpaer image to use based on DB records.
        """

        # if the current_wallpaper is the only image of STATE_DOWNLOADED, then nothing to do
        current_wallpaper = store().find(Image, Image.active_wallpaper == True).any() 

        if store().find(Image,
                        And(Image.state == Image.STATE_DOWNLOADED,
                            Image.active_wallpaper == False)).count() == 0:
            return current_wallpaper

        keep_timestamp = datetime.now() - timedelta(seconds=self.config.get_options().keep)

        # if there's no downloaded image during KEEP duration, then active the latest one
        if store().find(Image,
                        And(Image.state == Image.STATE_DOWNLOADED,
                            Image.download_time >= keep_timestamp)).count() == 0:
            downloaded_images = store.find(Image, Image.state == Image.STATE_DOWNLOADED).order_by(Desc(Image.download_time))
            downloaded_images.set(state = Image.STATE_EXPIRED)

            wallpaper = downloaded_images.last()
            wallpaper.state = Image.STATE_DOWNLOADED

            store().flush()
            store().commit()

            # unlink expired images
            self.delete_expired_images()

            # set the new wallpaper
            # self.active_wallpaper(wallpaper)
            self.update_wallpaper_record(image)

            return wallpaper

        # unlink all images over KEEP duration
        expired_images = store().find(Image,
                                      And(Image.state == Image.STATE_DOWNLOADED,
                                          Image.download_time < keep_timestamp))
        expired_images.set(state = Image.STATE_EXPIRED)
        store().flush()
        store().commit()            
        self.delete_expired_images()

        # Estimate the time of next image will be successfully fetched.
        # Ajust the switching fequency so that all pending images can be displayed
        # before it.

        next_image_estimation = self.estimate_next_image()
        time_to_next_image = next_image_estimation - datetime.now()
        print "Time to next image: %d seconds" % time_to_next_image.total_seconds()
        images_to_show = store().find(Image,
                       And(Image.state == Image.STATE_DOWNLOADED,
                           Image.active_wallpaper == False)).count()
        print "Images to show: %d" % images_to_show
        display_time_per_image = time_to_next_image / images_to_show \
            if images_to_show != 0 \
            else timedelta(seconds=self.config.get_options().keep)
        print "Display time per image: %d" % display_time_per_image.total_seconds()

        # did the current wallpaper expire?
        if current_wallpaper is not None:
            if current_wallpaper.active_time is None:
                current_wallpaper.active_time = datetime.now()
                store().flush()
                store().commit()
                return current_wallpaper

            if current_wallpaper.active_time >= datetime.now() - display_time_per_image:
                # not expired, nothing to do
                return current_wallpaper

            current_wallpaper.state = Image.STATE_EXPIRED
            store().flush()
            store().commit()            
            self.delete_expired_images()

        # active the first downloaded image
        image = store().find(Image, Image.state == Image.STATE_DOWNLOADED).order_by(Image.download_time).first()

        if image is None:
            return None

        if image.active_wallpaper == True:
            return image

        # set a new wallpaper
        self.update_wallpaper_record(image)
        return image

    def update_gsettings(self, image):
        """
        Update wallpaper image with gsettings.
        """

        print "image_file = %s" % (image.image_path)

        if self.get_gsettings_wallpaper() != "file://" + image.image_path:
            gsettings = Gio.Settings.new(self.SCHEMA)
            gsettings.set_string(self.KEY, "file://" + image.image_path)
            GObject.idle_add(lambda: self.ui_controller.notify_wallpaper_update(image))
    
    def get_gsettings_wallpaper(self):
        """
        Get the current wallpaper image URI with gsettings.
        """

        gsettings = Gio.Settings.new(self.SCHEMA)
        return gsettings.get_string(self.KEY)

    def correct_link(self):
        """
        Correct wallpaer on startup.
        """

        try:
            os.mkdir(self.img_dir)
        except OSError:
            pass
        self.update_wallpaper()

    def update(self):
        """
        Try to download new images and update wallpaper.
        """

        print "Updating..."
        download_thread = DownloadThread(self, self.ui_controller, self.config)
        download_thread.start()

    def generate_img_file(self, suffix):
        """
        Generate a new empty image file.
        """

        return tempfile.mkstemp(suffix=suffix, dir=self.img_dir)
