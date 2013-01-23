#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'big_wallpaper',
    version = '0.1',
    description = 'Update Unity wallpaper with images from Boston Bigpicture',
    author = 'Yale Huang',
    author_email = 'yale.huang@trantect.com',
    url = 'https://github.com/yaleh/BigWallpaper',
    packages = ['big_wallpaper'],
    scripts = ['bin/big_wallpaper'],
    license = "LICENSE.txt",
    data_files = [
        ('share/applications', ["share/big_wallpaper.desktop"]),
        ('share/big_wallpaper', ["share/big_wallpaper.desktop"]),
        ('share/big_wallpaper/pixmaps', ["share/pixmaps/big_wallpaper_small.png"]),
        ('/usr/share/icons/hicolor/64x64/apps', ["share/pixmaps/big_wallpaper.png"]),
        ],
    install_requires = [
	"urllib2 >= 2.7",
	"lxml >= 2.3.2",
	"sh >= 1.07",
	"gi >= 3.2.2",
	"dbus.service >= 1.0.0"
        ]
    )
