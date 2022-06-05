#! /bin/bash

if [[ $1 == "-duplex" ]]; then
  oddRotate="-rotate 180"
  shift
else
  oddRotate=""
fi

in=$1
pre=ima$$
pdfimages -all $in $pre
for i in $pre*; do
  if echo $i | grep --quiet '[02468][.]'; then
    convert $i -distort Resize 40% ${i}-small.jpg
  else
    convert $i -distort Resize 40% $oddRotate ${i}-small.jpg
  fi
  convert ${i}-small.jpg ${i}-small.pdf
done
pdftk $pre*-small.pdf cat output ${in%.pdf}-small.pdf
rm $pre*
  
