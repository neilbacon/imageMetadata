#! /bin/bash
set -e     # exit on error

BACKUP="photos"              # default backup type
MEDIA="/media/$USER"         # base dir for removable disks
if [[ "$USER" == neil ]]; then
  PHOTOS="$MEDIA/NB-Photo"   # dir(s) to backup for photos
  DEST="$MEDIA/NB2"
else
  PHOTOS="$MEDIA/KerryPhotoDisk"
  DEST="$MEDIA/KerryBackup2"
fi

while getopts :b:d:s:h opt; do
  case $opt in
    b) BACKUP=$OPTARG;;
    d) DEST=$OPTARG;;
    d) SRC=$OPTARG;;
    h) cat <<EoF
Usage: $0 [-b {backup}] [-d {disk}] [-h]
where:
  -b {backup} is what to backup, one of photos|desktop|laptop, default $BACKUP
  -d {dest} is the destination to write the backup to, default $DEST
  -s {src} is the source dir(s) to backup, default $PHOTOS/ for '-b photos' else $HOME/
     Note the trailing slash is significant for rsync.
  -h prints this help
EoF
      exit 0
      ;;
    \?)
      echo "Invalid option -$OPTARG. Try -h for help" >&2
      exit 1
      ;;
    :)
      echo "Invalid option: -$OPTARG requires an argument. Try -h for help" >&2
      exit 2
      ;;
  esac
done
shift $((OPTIND - 1))

# set SRC to dirs to backup and patterns to exclude, depending on -b {backup}
# trailing / in SRC dir affects rsync behaviour (contents of dir stored in backup without leading dir component in the path)
case $BACKUP in
  photos)
    [[ -n "$SRC" ]] || SRC="$PHOTOS/"
    EXCL=('/lost+found/' '/.*' '/*/.dtrash/')     # digikam uses .dtrash for its trash
    ;;
  desktop|laptop)
    [[ -n "$SRC" ]] || SRC="$HOME/"
    EXCL=('/.*' '/Downloads/' '/snap/' '/sw/' '/VirtualBox VMs/')     # quotes allow for spaces in patterns (with special care below)
    ;;
  *)
    echo "Unknown {backup} type -b $BACKUP. Try -h for help" >&2
    exit 1
    ;;
esac

# error if a dir to backup doesn't exist
for d in ${SRC}; do
  if [[ ! -e $d ]]; then
    echo "Missing source dir $d" >&2
    exit 1
  fi
done

DST_DIR="$DEST/backup-$BACKUP"
mkdir -p "${DST_DIR}"
DST=$( date "+%Y%m%d_%H%M%S" ).backup

OPTS=('--archive' '--progress')
# if "current" symlink exists then add options for incremental backup
[[ -e $DST_DIR/current ]] && OPTS+=('--delete' '--delete-excluded' "--link-dest=$DST_DIR/current")

# add --exclude options
for e in "${EXCL[@]}"; do
  OPTS+=("--exclude='$e'")                         # single quotes to handle exclude patterns with spaces
done

eval rsync "${OPTS[@]}" ${SRC} ${DST_DIR}/${DST}   # eval with double quotes preserves the single quotes!
rm -f ${DST_DIR}/current
ln -s ${DST} ${DST_DIR}/current                    # points to new backup

