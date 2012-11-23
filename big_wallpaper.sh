#!/bin/bash

IMGFILE="${HOME}/Pictures/wallpaper.jpg"
URLFILE="${HOME}/.big_wallpaper.url"
WALLPAPER_URL_COFFEE=$(dirname $0)"/wallpaper_url.coffee"
COFFEE="/usr/local/bin/coffee"

touch "${URLFILE}"
OLD_URL=`cat ${HOME}/.big_wallpaper.url`
NEW_URL=`${COFFEE} ${WALLPAPER_URL_COFFEE}`

if [ "${NEW_URL}" == "${OLD_URL}" ]; then
    echo No change.
    exit 1
fi

OLD_IMGFILE=`ls -al ${IMGFILE} |sed -n -e 's/^.*\-> //p'`
NEW_IMGFILE=`mktemp -u --tmpdir=${HOME}/Pictures/ --suffix=.jpg`

/usr/bin/wget -O ${NEW_IMGFILE} ${NEW_URL}
if [ $? -ne 0 ]; then
    echo Downloading failed.
    exit 1
fi

echo ${NEW_URL} >${URLFILE}
ln -sf "${NEW_IMGFILE}" "${IMGFILE}"
gsettings set org.gnome.desktop.background picture-uri "file://${IMGFILE}"
rm "${OLD_IMGFILE}"
