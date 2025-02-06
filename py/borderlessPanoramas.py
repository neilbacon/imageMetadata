#! /usr/bin/env python3

import argparse
from PIL import Image

# return (imageFile, widthPixels, heightPixels, imageHeightPoints)
def imageWidthHeightPixels(pageWidthPoints, imageFile):
  i = Image.open(imageFile)
  aspect =  i.height / i.width
  r = (imageFile, i.width, i.height, pageWidthPoints * aspect)
  i.close()
  return r

# yOffsetPoints is the offset from the bottom of the page to the bottom of where the image will be rendered
# return PS redering for image
def render(imageFile, imageWidthPixels, imageHeightPixels, imageWidthPoints, imageHeightPoints, yOffsetPoints):
  return f"""gsave
  0 {yOffsetPoints} translate
  {imageWidthPoints} {imageHeightPoints} scale                              % rendered image size in points, [0..1) for both x & y will scale to the rendered image size
  {imageWidthPixels}
  {imageHeightPixels}
  8                                                                         % bits per color channel (1, 2, 4, or 8)
  [{imageWidthPixels} 0 0 {-imageHeightPixels} 0 {imageHeightPixels}]       % transform image pixels to unit square, [0..1) for both x & y
  ({imageFile}) (r) file /DCTDecode filter                                  % opens the file and filters the image data
  false                                                                     % pull channels from separate sources
  3                                                                         % 3 color channels (RGB)
  colorimage
grestore
"""

pageSizes = { 'A4': (297, 210), 'A3': (420, 297), 'A3+': (483, 329) }       # landscape by default

def createPS(args, imageFiles):
  pageWidthMm, pageHeightMm = pageSizes[args.pageSize]
  if args.portrait:
     pageWidthMm, pageHeightMm = pageHeightMm, pageWidthMm
  if args.pageWidth:
     pageWidthMm = args.pageWidth
  if args.pageHeight:
     pageHeightMm = args.pageHeight
  pageWidthPoints = pageWidthMm * 72 / 25.4
  pageHeightPoints = pageHeightMm * 72 / 25.4
  imageDims = [imageWidthHeightPixels(pageWidthPoints, imageFile) for imageFile in imageFiles ]
  sumHeightPoints = sum([i[3] for i in imageDims])
  
  # distance from page bottom to bottom of first image = distance from top of last image to top of page
  # the gap between images is twice this
  heightMarginPoints = (pageHeightPoints - sumHeightPoints) / (2 * len(imageFiles)) if pageHeightPoints > sumHeightPoints else 0

  psImages = ""
  yOffsetPoints = heightMarginPoints
  for imageFile, imageWidthPixels, imageHeightPixels, imageHeightPoints in imageDims:
    psImages = psImages + render(imageFile, imageWidthPixels, imageHeightPixels, pageWidthPoints, imageHeightPoints, yOffsetPoints)
    yOffsetPoints = yOffsetPoints + imageHeightPoints + 2 * heightMarginPoints
      
  with open(args.output, 'w') as f:
      f.write(f"""%!PS
  %%BeginSetup
  %%BeginFeature: *PageSize A4
  << /PageSize [{pageWidthPoints} {pageHeightPoints}]
  /ImagingBBox null
  >> setpagedevice
  %%EndFeature
  %%EndSetup
  {psImages}
  showpage 
  """
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser( description = '''Generate a Postscript page of panoramic images.
The page will generally be in landscape orientation with each image taking up the entire width with no border/margin.
Vertically there is some margin around images.
''', epilog = '''You can convert PS to PDF with:
gs -dNOSAFER  -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=a.pdf a.ps
''')
    parser.add_argument("--pageSize", choices=('A4', 'A3', 'A3+'), help="the page size (or use pageWidth and pageHeight)", default='A4')
    parser.add_argument("--pageWidth",  help="page width (mm)", type=int)
    parser.add_argument("--pageHeight",  help="page height (mm)", type=int)
    parser.add_argument("--portrait", action="store_true", help="use portrait orientation for pageSize")
    parser.add_argument("--output", help="output Postscript file name", default="output.ps")
    args, imageFiles = parser.parse_known_args()
    createPS(args, imageFiles)

