#!/bin/bash

IMGFILE="${HOME}/Pictures/wallpaper.jpg"
URLFILE="${HOME}/.big_wallpaper.url"
WALLPAPER_URL_COFFEE=$(dirname $0)"/wallpaper_url.coffee"
COFFEE="/usr/local/bin/coffee"

OLD_IMGFILE=`ls -al ${IMGFILE} |sed -n -e 's/^.*\-> //p'`
# correct wallpaper setting in case last update was missed, i.e. desktop is
# not running when updating image
OLD_IMGURL="file://${OLD_IMGFILE}"
WP_URL=`gsettings get org.gnome.desktop.background picture-uri`
if [ "$WP_URL" != "'file://$OLD_IMGFILE'" ]; then
    echo "Correct wallpaper setting..."
    gsettings set org.gnome.desktop.background picture-uri "file://$OLD_IMGFILE"
fi

touch "${URLFILE}"
OLD_URL=`cat ${HOME}/.big_wallpaper.url`
NEW_URL=`${COFFEE} ${WALLPAPER_URL_COFFEE}`

if [ "${NEW_URL}" == "${OLD_URL}" ]; then
    echo No change.
    exit 1
fi

NEW_IMGFILE=`mktemp -u --tmpdir=${HOME}/Pictures/ --suffix=.jpg`

/usr/bin/wget -O ${NEW_IMGFILE} ${NEW_URL}
if [ $? -ne 0 ]; then
    echo Downloading failed.
    exit 1
fi

echo ${NEW_URL} >${URLFILE}
ln -sf "${NEW_IMGFILE}" "${IMGFILE}"
echo "Apply new wallpaper..."
gsettings set org.gnome.desktop.background picture-uri "file://${NEW_IMGFILE}"
rm "${OLD_IMGFILE}"
