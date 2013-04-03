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

### Build DSC file (optional, for PPA)
	
	debuild -tc -S -sa

### Clean folder debian (optional)

	debuild clean

## Install with PPA repository (Ubuntu)

	sudo add-apt-repository ppa:yale-huang/ppa
	sudo apt-get update
	sudo apt-get install python-big-wallpaper
	
## Run it

Type ```BigWallpaper``` in the *Dash Home* of Unity launcher, and click the icon.
