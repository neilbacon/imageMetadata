#! /usr/bin/env python3

import os
import argparse
from PIL import Image

# return (widthPixels, heightPixels)
def imageWidthHeightPixels(imageFile):
  i = Image.open(imageFile)
  r = (i.width, i.height)
  i.close()
  return r

pageSizes = { 'A4': (210, 297), 'A3': (297, 420), 'A3+': (329, 483) }       # landscape by default

def createPS(args, imageFile):
  pageWidthMm, pageHeightMm = pageSizes[args.pageSize]
  if args.portrait:
     pageWidthMm, pageHeightMm = pageHeightMm, pageWidthMm
  if args.pageWidth:
     pageWidthMm = args.pageWidth
  if args.pageHeight:
     pageHeightMm = args.pageHeight
  (imageWidthPixels, imageHeightPixels) = imageWidthHeightPixels(imageFile)
  pixelsPerMm = imageWidthPixels / args.imageWidth
  pageWidthPixels = pageWidthMm * pixelsPerMm
  pageHeightPixels = pageHeightMm * pixelsPerMm
  os.system(f"convert {imageFile} -density {pixelsPerMm * 25.4} -gravity center -extent {pageWidthMm * pixelsPerMm}x{pageHeightMm * pixelsPerMm} {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser( description = '''Generate a Postscript page of centred image.
''', epilog = '''You can convert PS to PDF with:
gs -dNOSAFER  -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=a.pdf a.ps
''')
    parser.add_argument("--pageSize", choices=('A4', 'A3', 'A3+'), help="the page size (or use pageWidth and pageHeight)", default='A4')
    parser.add_argument("--pageWidth",  help="page width (mm)", type=int)
    parser.add_argument("--pageHeight",  help="page height (mm)", type=int)
    parser.add_argument("--portrait", action="store_true", help="use portrait orientation for pageSize (not applied if pageWidth and pageHeight are used)")
    parser.add_argument("--imageWidth",  help="image width (mm)", type=int)
    parser.add_argument("--output", help="output Postscript file name", default="output.ps")
    args, imageFiles = parser.parse_known_args()
    createPS(args, imageFiles[0])

