#! /bin/bash

for i in "$@"
do
    tiffcrop -N 1 $i ${i}.$$
    mv ${i}.$$ $i
done
