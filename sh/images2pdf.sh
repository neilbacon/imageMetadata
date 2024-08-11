#! /bin/bash

# based on https://unix.stackexchange.com/questions/20026/convert-images-to-pdf-how-to-make-pdf-pages-same-size

PDF=out.pdf
DPI=150
QTY=90

SHORT=210  # short edge in mm; convert to inches with: * 10 / 254
LONG=297
ORIENTATION=landscape

while getopts :p:d:q:s:l:p:o:h opt; do
  case $opt in
    p) PDF=$OPTARG;;
    d) DPI=$OPTARG;;
    q) QTY=$OPTARG;;
    s) SHORT=$OPTARG;;
    l) LONG=$OPTARG;;
    o) ORIENTATION=$OPTARG;;
    h) cat <<EoF
Usage: $0 [options] images...
Create a PDF with each of the input images on a separate page. 
where:
  -p {pdf} is the output PDF file (must end in .pdf), default $PDF
  -d {density} is dots-per-inch of images written to the PDF, default $DPI
  -q {quality} is JPG quality of images written to the PDF, default $QTY
  -s {short} is length of the short edge of the page in mm (210 for A4), default $SHORT
  -l {long} is length of the long edge of the page in mm (297 for A4), default $LONG
  -o portait|landscape is page orientation, default $ORIENTATION
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

SHORT_PX=$(( DPI * SHORT * 10 / 254 ))  # short edge in pixels
LONG_PX=$(( DPI * LONG * 10 / 254 ))
case $ORIENTATION in
  [Pp]*) SIZE=${SHORT_PX}x${LONG_PX};; # {width}x{height} in pixels
  *)     SIZE=${LONG_PX}x${SHORT_PX}
esac

convert $* -compress jpeg -quality $QTY -density ${DPI}x${DPI} -units PixelsPerInch -resize $SIZE -repage $SIZE $PDF

