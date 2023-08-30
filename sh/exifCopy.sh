#! /bin/bash
# Usage:
# cd photoDir
# exifCopy .NEF v2.JPG

input=$1
output=$2
shift 2

set -x

for i in *$input; do
  o=${i%$input}$output
  exiftool -overwrite_original -TagsFromFile $i $o
done
