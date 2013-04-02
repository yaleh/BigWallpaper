from gi.repository import GObject
from urllib2 import urlopen, HTTPError, URLError
from httplib import HTTPException
from lxml.html import parse
from models import *
from storm.expr import *
from datetime import datetime

import threading
import os
import socket

class DownloadThread(threading.Thread):
    """
    Thread for fetch homepage and image from Boston Big Picture.
    """

    def __init__(self, manager, ui_controller, config):
        """
        Constructor of DownloadThread.
        """
        super(DownloadThread, self).__init__()
        self.manager = manager
        self.ui_controller = ui_controller
        self.config = config

    def fetch_links(self):
        """
        Fetch links defined in source_site.
        """
        
        new_link = False

        for site in store().find(SourceSite, SourceSite.active == True):
            print "Fetching %s" % site.name

            try:
                page = urlopen(site.url, self.config.get_options().timeout)
            except (HTTPError, URLError):
                print "Failed to fetch %s"
                continue

            try:
                p = parse(page)
                link = p.xpath(site.image_xpath)[0]
            except (HTTPException, IndexError, socket.error):
                print "Failed to parse image path."
                continue

            site.last_update = datetime.now()

            store().flush()
            store().commit()

            print "Got a new image link: %s" % link           

            if store().find(Image, Image.source_image_url == unicode(link)).count() > 0:
                print "Dulplicated image link: %s" % link
                continue

            image = Image()
            image.source_site = site
            image.source_image_url = unicode(link)
            image.state = Image.STATE_PENDING
            image.active_wallpaper = False

            try:
                image.source_link = unicode(p.xpath(site.link_xpath)[0])
            except (IndexError, TypeError):
                print "Failed to parse link."
                image.source_link = None
                continue

            try:
                image.source_title = unicode(p.xpath(site.title_xpath)[0])
            except (IndexError, TypeError):
                print "Failed to parse title."
                image.source_title = None
                continue

            try:
                image.source_description = unicode(p.xpath(site.description_xpath)[0])
            except (IndexError, TypeError):
                print "Failed to parse decription."
                image.source_description = None
                continue

            print "Created a new image object: %s" % image.source_image_url
            
            store().add(image)
            store().flush()
            store().commit()

            new_link = True

        return new_link

    def fetch_images(self):
        """
        Fetch latest pending images.
        """

        image_downloaded = False

        for image in store().find(Image, Image.state == Image.STATE_PENDING).order_by(Desc(Image.id)):
            temp_file = self.manager.generate_img_file(".jpg")

            if self.download_img_file(temp_file[0], image.source_image_url):                
                # os.close(temp_file[0])

                print "Downloaded %s: %s" % (image.source_image_url, temp_file[1])

                image.image_path = unicode(temp_file[1])
                image.download_time = datetime.now()
                image.state = Image.STATE_DOWNLOADED

                image_downloaded = True
            else:
                # os.close(temp_file[0])
                os.unlink(temp_file[1])
                print "Failed to download %s" % image.source_image_url

                image.state = Image.STATE_FAILED

            store().flush()
            store().commit()

        return image_downloaded

    def run(self):
        """
        Thread run callback.
        """

        if self.manager.update_lock is None:
            self.manager.update_lock = threading.Lock()

        if not self.manager.update_lock.acquire(False):
            # is updaing now, just return
            return

        GObject.idle_add(self.ui_controller.start_updating)

        try:
            print "Get URL..."

            print "Reconnected."

            self.fetch_links()
            self.fetch_images()

            self.manager.update_wallpaper()
        finally:
            if store() is not None:
                store().close()

            GObject.idle_add(self.ui_controller.finish_updating)
            self.manager.update_lock.release()

    def download_img_file(self, fd, url):
        """
        Download the image of url.
        """

        try:
            img = urlopen(url)
        except (HTTPError, URLError, IOError):
            return False

        f = os.fdopen(fd, 'w')
        f.write(img.read())
        f.close()

        return True
