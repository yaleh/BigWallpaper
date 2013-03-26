from peewee import *
from gi.repository import Gio
import tempfile

db = SqliteDatabase(None)

def init_pollute():
    SourceSite.create_table(fail_silently=True)
    Image.create_table(fail_silently=True)

    try:
        SourceSite.get()
        return
    except DoesNotExist:
        site = SourceSite.create(name = "Boston Bigpicture",
                                 description = "Bigpicture from Boston",
                                 last_update = "1900-1-1",
                                 url = "http://www.boston.com/bigpicture",
                                 xpath = '/descendant::img[@class="bpImage"]')
        site.save()

def connect_db(path):
    global db
    db.init(path, check_same_thread=False)
    init_pollute()

class BaseModel(Model):
    class Meta:
        database = db

class SourceSite(BaseModel):
    name = CharField()
    description = CharField(null=True)
    last_update = DateTimeField(null=True)
    url = CharField()
    xpath = CharField()

SCHEMA = 'org.gnome.desktop.background'
KEY = 'picture-uri'

class Image(BaseModel):
    source_site = ForeignKeyField(SourceSite, related_name = "images")
    source_page_url = CharField()
    source_image_url = CharField()
    source_title = CharField()
    source_description = CharField()
    download_time = DateTimeField()
    image_path = CharField()
    available = BooleanField()
    active_wallpaper = BooleanField()

    image_dir = ""

    def activate_wallpaper(self):
        if self.active_wallpaper:
            return True

        if self.saved_path is None:
            return False

        gsettings = Gio.Settings.new(SCHEMA)
        gsettings.set_string(KEY, "file://" + self.image_path)
        GObject.idle_add(self.ui_controller.notify_wallpaper_update)

        self.active_wallpaper = True
        self.save()

        return True        

    @staticmethod
    def generate_img_file(suffix):
        return tempfile.mkstemp(suffix=suffix, dir=image_dir)

    @staticmethod
    def set_image_dir(path):
        image_dir = path

    @staticmethod
    def set_wallpaper(image):
        org_wallpaper = Image.get(Image.active_wallpaper == True)
        if org_wallpaper.id == image.id:
            return

        org_wallpaper.active_wallpaper = False
        org_wallpaper.save()

        image.activate_wallpaper()
        

