#! /bin/bash

for i in "$@"
do
    tiffcrop -N 1 $i ${i}.$$           # I think this is loosing the EXIF
    exiftool -overwrite_original -TagsFromFile $i ${i}.$$  # test this restores it
    mv ${i}.$$ $i
done
