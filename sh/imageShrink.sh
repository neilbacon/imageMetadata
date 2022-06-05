#! /bin/bash

# see http://www.imagemagick.org/Usage/filter/nicolas/#downsample

perc=50%
if [[ $1 = *% ]]
then
  perc=$1
  shift
fi

for src in "$@"
do
    dst="${src##*/}" 	# basename (dir stripped)
    if [[ "$dst" == "$src" ]]; then
	# make dst differ from src, preserving filename extension by
	# inserting "_small" before last "."
        dst=`echo "$dst" | sed 's/\(.*\)\./\1_small./'`
    fi
    echo "$dst ..."
    convert "$src" -colorspace RGB -distort Resize $perc -colorspace sRGB "$dst"
done
echo "Done."
