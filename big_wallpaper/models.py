from storm.locals import *
from gi.repository import Gio
from datetime import datetime
import tempfile

_database = None
_store = None
_db_url = None

def store():
    global _database, _store

    if _database is not None and (_store is None or _store._connection._closed):
        _store = Store(_database)
    return _store

def init_pollute():
    if _store is None:
        return

    # see https://storm.canonical.com/Manual for the properties mapping

    _store.execute("""
CREATE TABLE IF NOT EXISTS source_site(
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    description VARCHAR,
    last_update VARCHAR,
    url VARCHAR,
    link_xpath VARCHAR,
    image_xpath VARCHAR,
    title_xpath VARCHAR,
    description_xpath VARCHAR,
    active INT
)
""")
    _store.execute("""
CREATE TABLE IF NOT EXISTS image(
id INTEGER PRIMARY KEY,
    source_site_id INTEGER,
    source_link VARCHAR,
    source_image_url VARCHAR,
    source_title VARCHAR,
    source_description VARCHAR,
    download_time VARCHAR,
    image_path VARCHAR,
    state VARCHAR,
    active_wallpaper INT
)
""")

    if _store.find(SourceSite).count() == 0:
        site = SourceSite()
        site.name = u"Boston BigPicture"
        site.description = u"Bigpicture from Boston"
        site.last_update = datetime(1900, 1, 1)
        site.url = u"http://www.boston.com/bigpicture"
        site.link_xpath = u'//img[@class="bpImage"]/parent::a/@href'
        site.image_xpath = u'//img[@class="bpImage"]/@src'
        site.title_xpath = u'//div[@class="headDiv2"]/h2/a/text()'
        site.description_xpath = u'//div[@class="bpBody"]/text()'
        site.active = True

        _store.add(site)
        _store.flush()
        _store.commit()

def connect_db(path):
    global _store, _db_url, _database
    _db_url = "sqlite:%s" % path

    _database = create_database(_db_url)
    _store = Store(_database)
    init_pollute()
    _store.close()
    _store = None

class SourceSite(object):
    __storm_table__ = "source_site"

    id = Int(primary = True)
    name = Unicode()
    description = Unicode()
    last_update = DateTime()
    url = Unicode()
    link_xpath = Unicode()
    image_xpath = Unicode()
    title_xpath = Unicode()
    description_xpath = Unicode()
    active = Bool()

SCHEMA = 'org.gnome.desktop.background'
KEY = 'picture-uri'

class Image(object):
    STATE_PENDING = u"PENDING"
    STATE_DOWNLOADED = u"DOWNLOADED"
    STATE_FAILED = u"FAILED"
    STATE_DELETED = u"DELETED"

    __storm_table__ = "image"

    id = Int(primary = True)
    source_site_id = Int()
    source_site = Reference(source_site_id, SourceSite.id)
    source_link = Unicode()
    source_image_url = Unicode()
    source_title = Unicode()
    source_description = Unicode()
    download_time = DateTime()
    image_path = Unicode()
    state = Unicode() # available state: PENDING, DOWNLOADED, FAILED, DELETED
    active_wallpaper = Bool()

    image_dir = ""

    @staticmethod
    def generate_img_file(suffix):
        return tempfile.mkstemp(suffix=suffix, dir=image_dir)

    @staticmethod
    def set_image_dir(path):
        image_dir = path

