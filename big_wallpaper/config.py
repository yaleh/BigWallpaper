from optparse import OptionParser
import ConfigParser
import os

class Config:
    BIGWALLPAPER_SECTION = "BigWallpaper"

    def __init__(self, args):
        parser = OptionParser()
        parser.add_option("-c", "--config-file", dest="config", default="",
                          metavar="FILE", help="Config file")
        parser.add_option("-p", "--prefix", dest="prefix", type="string",
                          help="path prefix for app resources [default: %default]",
                          default="/usr/share/big_wallpaper")
        parser.add_option("-d", "--dest", dest="dest", type="string",
                          help="dest dir for download image files [default: %default]",
                          default=os.path.expanduser('~/.big_wallpaper'))
        parser.add_option("-i", "--interval", dest="interval", type="int",
                          help="interval of updating in seconds [default: %default]",
                          default=1800000)
        parser.add_option("-k", "--keep", dest="keep", type="int",
                          help="Duration to keep the downloaded images (in seconds) [default: %default]",
                          default=60*60*24)
        parser.add_option("-t", "--timeout", dest="timeout", type="int",
                          help="Timeout of every page/image downloading (in seconds) [default: %default]",
                          default=60)

        # Actually, only CONFIG is necessary for this parse_arg()
        (self.options, pending_args) = parser.parse_args(args)

        config = ConfigParser.SafeConfigParser()

        if self.options.config:
            config.read(self.options.config)
        else:
            config.read(['big_wallpaper.conf',
                         os.path.expanduser('~/.big_wallpaper.conf')])
        try:
            defaults = dict(config.items(self.BIGWALLPAPER_SECTION))
        except ConfigParser.NoSectionError:
            defaults = {}
        print defaults

        # Parse again with default values from config file
        parser.set_defaults(**defaults)
        (self.options, args) = parser.parse_args(args)

        print self.options

    def get_options(self):
        return self.options

    def save(self):
        config = ConfigParser.SafeConfigParser()

        config.add_section(self.BIGWALLPAPER_SECTION)

        config.set(self.BIGWALLPAPER_SECTION, 'interval',
                   "%d" % self.options.interval)
        config.set(self.BIGWALLPAPER_SECTION, 'dest', 
                   self.options.dest)
        config.set(self.BIGWALLPAPER_SECTION, 'prefix', 
                   self.options.prefix)
        config.set(self.BIGWALLPAPER_SECTION, 'keep',
                   "%d" % self.options.keep)
        config.set(self.BIGWALLPAPER_SECTION, 'timeout',
                   "%d" % self.options.timeout)

        f = None

        f = open(self.options.config if self.options.config \
                     else os.path.expanduser('~/.big_wallpaper.conf'), 
                 'wb')

        if f:
            try:
                config.write(f)
            finally:
                f.close()
