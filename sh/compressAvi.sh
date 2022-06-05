#! /bin/bash

for file in "$@"
do
  bak="$file".bak
  mv -f "$file" "$bak"
  transcode -i "$bak" -y xvid4 -N 0x1 -o "$file"
done
