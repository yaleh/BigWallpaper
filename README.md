BigWallpaper
============

Python based wallpaper updating applet from Boston BigPicture for Unity.

## Building Debian/Ubuntu package

### Update changelog (optional)

    dch -v VERSION-1
	
### Update debian files with setup.py (optional)

    python setup.py sdist
	
### Build it

    debuild -us -uc -b
