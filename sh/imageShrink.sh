#! /bin/bash

max_dim=1000 # pixels

while getopts :d:h opt; do
  case $opt in
    d) max_dim=$OPTARG;;
    h) cat <<EoF
Usage: $0 [-d {max_dim}] [-h] FILE...
Shrink images files FILE...
where:
  -d {max_dim} is the maximum dimension (width or height) in pixels for the shrunk images, default $max_dim
  -h prints this help
FILE is unchanged, with shrunk images created in the current working directory (cwd).
If FILE is in some other directory (recommended usage), then the shrunk file in the cwd has the same name.
If FILE is in the cwd then the shrunk file name is based on FILE but with "_small" inserted before the last "."
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

for src in "$@"
do
    dst="${src##*/}" 	# basename (dir stripped)
    if [[ "$dst" == "$src" ]]; then
	# make dst differ from src, preserving filename extension by
	# inserting "_small" before last "."
        dst=`echo "$dst" | sed 's/\(.*\)\./\1_small./'`
    fi
    echo "$dst ..."
    # https://imagemagick.org/Usage/resize/#resize_colorspace
    convert "$src" -colorspace RGB -resize "$max_dim>" -colorspace sRGB "$dst"
done
echo "Done."
