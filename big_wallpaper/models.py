from peewee import *
from gi.repository import Gio
from datetime import datetime
import tempfile

db = SqliteDatabase(None)


def store():
    global db

    return db


def init_pollute():
    SourceSite.create_table(fail_silently=True)
    Image.create_table(fail_silently=True)

    if SourceSite.select().count() == 0:
        SourceSite.create(
            name='Boston Bigpicture',
            description='Bigpicture from Boston',
            url='http://www.boston.com/bigpicture',
            link_xpath='//img[@class="bpImage"]/parent::a/@href',
            image_xpath='//img[@class="bpImage"]/@src',
            title_xpath='//div[@class="headDiv2"]/h2/a/text()',
            description_xpath='//div[@class="bpBody"]/text()',
            active=True
        )
        SourceSite.create(
            name='The Atlantic In Focus',
            description='In Focus with Alan Taylor',
            url='http://www.theatlantic.com/infocus/',
            link_xpath='//h1[@class="headline"]/a/@href',
            image_xpath='//span[@class="if1280"]//img/@src',
            title_xpath='//h1[@class="headline"]/a/text()',
            description_xpath='//div[@class="dek"]/p/text()',
            active=True
        )
        SourceSite.create(
            name='Los Angeles Times Framework',
            description='Capturing the world through photography, video and multimedia',
            url='http://framework.latimes.com/',
            link_xpath='//div[@class="entry-description"]/h1/a/@href',
            image_xpath='//div[@class="entry-body clearfix"]/a/img/@src',
            title_xpath='//div[@class="entry-description"]/h1/a/text()',
            description_xpath='//div[@class="entry-description"]/p[3]/text()',
            active=True
        )
        SourceSite.create(
            name='NBC News Photo Blog',
            description='Conversations sparked by photojournalism. Follow us on Twitter to keep up-to-date.',
            url='http://photoblog.nbcnews.com/',
            link_xpath='//article[@class="text_post"]//h2/a/@href',
            image_xpath='//article//img/@src',
            title_xpath='//article[@class="text_post"]//h2/a/text()',
            active=True
        )
        SourceSite.create(
            name='Reuters Full Focus',
            description='Reutuers Full Focus',
            url='http://blogs.reuters.com/fullfocus/',
            link_xpath='//div[@class="topStory"]/div[@class="photo"]/a/@href',
            image_xpath='//div[@class="topStory"]/div[@class="photo"]/a/img/@src',
            title_xpath='//div[@class="topStory"]/div[@class="ImageTitle"]/a/text()',
            description_xpath='//div[@class="topStory"]/div[@class="ImageCaption"]/text()',
            active=True
        )


def connect_db(path):
    global db

    db.init(path, check_same_thread=False)
    db.connect()

    init_pollute()


class BaseModel(Model):

    class Meta:
        database = db


class SourceSite(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    description = CharField(null=True)
    last_update = DateTimeField(null=True)
    url = TextField()
    link_xpath = CharField(null=True)
    image_xpath = CharField(null=True)
    title_xpath = CharField(null=True)
    description_xpath = CharField(null=True)
    active = BooleanField()


class Image(BaseModel):
    STATE_PENDING = u"PENDING"
    STATE_DOWNLOADED = u"DOWNLOADED"
    STATE_FAILED = u"FAILED"
    STATE_DELETED = u"DELETED"
    STATE_QUEUED = u"QUEUED"
    STATE_EXPIRED = u"EXPIRED"

    id = IntegerField(primary_key=True)
    source_site = ForeignKeyField(SourceSite, related_name='source_site')
    source_link = TextField(null=True)
    source_image_url = TextField(null=True)
    source_title = TextField(null=True)
    source_description = TextField(null=True)
    download_time = DateTimeField(null=True)
    image_path = TextField(null=True)
    state = CharField(default=STATE_PENDING)
                      # available state: PENDING, DOWNLOADED, FAILED, DELETED,
                      # QUEUED, EXPIRED
    active_wallpaper = BooleanField(default=False)
    active_time = DateTimeField(default=None, null=True)

SCHEMA = 'org.gnome.desktop.background'
KEY = 'picture-uri'
