#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright 2012-2013, Yale Huang, yale.huang@trantect.com
#
#    This file is part of BigWallpaper.
#
#    Pyrit is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Pyrit is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BigWallpaper.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
import glob

setup(
    name = 'big_wallpaper',
    version = '0.2',
    description = 'Update Unity wallpaper with images from Boston Bigpicture',
    author = 'Yale Huang',
    author_email = 'yale.huang@trantect.com',
    url = 'https://github.com/yaleh/BigWallpaper',
    packages = ['big_wallpaper'],
#    package_dir={'big_wallpaper': 'big_wallpaper'},
    scripts = ['bin/big_wallpaper'],
    license = "LICENSE.txt",
    data_files = [
        ('share/applications', ["share/big_wallpaper.desktop"]),
        ('share/big_wallpaper', ["share/big_wallpaper.desktop"]),
        ('share/big_wallpaper/pixmaps', glob.glob("share/pixmaps/*.png")),
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
