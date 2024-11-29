#! /bin/bash

max_dim=1000
resize="${max_dim}x${max_dim}>" # default resize arg

while getopts :d:w:j:h opt; do
  case $opt in
    h) cat <<EoF
Usage: $0 [-d|w|j {max_dim}] [-h] FILE...
Shrink images where:
  -d {max_dim} is the maximum dimension (width and height) in pixels for the shrunk images, default -d $max_dim
  -w {max_dim} is the maximum width in pixels for the shrunk images
  -j {max_dim} is the maximum height in pixels for the shrunk images
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
    d) resize="${OPTARG}x${OPTARG}>" ;;
    w) resize="${OPTARG}>" ;;
    j) resize="x${OPTARG}>" ;;
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
    convert "$src" -colorspace RGB -resize "$resize" -colorspace sRGB "$dst"
done
echo "Done."
