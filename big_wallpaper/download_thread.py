from gi.repository import GObject
from urllib2 import urlopen
from lxml.html import parse

import threading

class DownloadThread(threading.Thread):
    """
    Thread for fetch homepage and image from Boston Big Picture.
    """

    def __init__(self, manager, ui_controller):
        """
        Constructor of DownloadThread.
        """
        super(DownloadThread, self).__init__()
        self.manager = manager
        self.ui_controller = ui_controller

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

            url = self.get_bigpicture_url()
            print url

            if self.manager.saved_url is not None:
                print self.manager.saved_url

            if url is not None and url == self.manager.saved_url:
                # Duplicated URL, don't download
                print "Duplicated URL"
                return

            temp_file = self.manager.generate_img_file(".jpg")
            self.download_img_file(temp_file[0], url)
            print "Downloaded %s: %s" % (url, temp_file[1])

            self.manager.on_image_downloaded(image_file = temp_file[1], 
                                        url = url)
        finally:
            GObject.idle_add(self.ui_controller.finish_updating)
            self.manager.update_lock.release()

    def get_bigpicture_url(self):
        """
        Find the first bpImage at http://www.boston.com/bigpicture .
        """
        page = urlopen('http://www.boston.com/bigpicture')
        p = parse(page)
        i = p.xpath('/descendant::img[@class="bpImage"]')[0]
        return i.get('src')

    def download_img_file(self, fd, url):
        """
        Download the image of url.
        """
        img = urlopen(url)
        f = os.fdopen(fd, 'w')
        f.write(img.read())
        f.close()
