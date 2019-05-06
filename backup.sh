#!/bin/bash
# Usage: backup.sh [ dir ]
# where dir = destination dir for backup, defaults to /media/neil/WDPassport2/backup

SRC="/home/neil /media/neil/NB2/Photos /media/neil/NB2/Videos" 
for d in ${SRC}
do
  [[ -e $d ]] || ( echo "Missing $d" >&2; exit 1 )
done

DST_DIR=${1-/media/neil/NB4/backup}
DST=$( date "+%Y%m%d_%H%M%S" ).backup


OPTS=''
[[ -e $DST_DIR/current ]] && OPTS="--delete --delete-excluded --link-dest=$DST_DIR/current"

rsync --archive --progress --exclude='/neil/.*/' --exclude='/neil/sw/' --exclude='/neil/Music/' --exclude='/neil/tmp/' --exclude='/neil/workspace/' --exclude='/neil/mnt/' --exclude='/neil/snap/' --exclude='/neil/Downloads/' --exclude='/neil/VirtualBox VMs/' --exclude='/Photos/.dtrash' --exclude='/Videos/.dtrash'  ${OPTS} ${SRC} ${DST_DIR}/${DST}
rm -f ${DST_DIR}/current
ln -s ${DST} ${DST_DIR}/current
