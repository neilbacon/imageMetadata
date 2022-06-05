#! /bin/bash
set -e     # exit on error

MEDIA="/media/$USER"       # base dir for removable disks
PHOTOS="$MEDIA/NB-Photo/"  # dir(s) to backup for photos (trailing slash significant for rsync, see below)

# defaults for command line options
BACKUP="photos"
DISK="$MEDIA/NB2"

while getopts :b:d:h opt; do
  case $opt in
    b) BACKUP=$OPTARG;;
    d) DISK=$OPTARG;;
    h) cat <<EoF
Usage: $0 [-b {backup}] [-d {disk}] [-h]
where:
  -b {backup} is what to backup, one of photos|desktop|laptop, default $BACKUP
  -d {disk} is the disk to write the backup to, default $DISK
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
    SRC="$PHOTOS"
    EXCL=('/lost+found/' '/.*' '/*/.dtrash/')              # digikam uses .dtrash for its trash
    ;;
  desktop)
    SRC="$HOME/"
    EXCL=('/.*' '/Downloads/' '/snap/' '/VirtualBox VMs/')     # quotes allow for spaces in patterns (with special care below)
    ;;
  laptop)
    SRC="$HOME/"
    EXCL=('/.*' '/Downloads/' '/snap/' '/sw/' '/VirtualBox VMs/')
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

DST_DIR="$DISK/backup-$BACKUP"
if [[ ! -e $DST_DIR ]]; then
  echo "Missing backup destination $DST_DIR" >&2
  exit 2
fi
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

