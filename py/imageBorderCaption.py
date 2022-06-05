import subprocess

# To Do: replace these with command line args and options
inImg = 'b.jpg'
outImg = 'b2.jpg'
caption = 'Sunset over the Nile'
font = 'Shadows-Into-Light'
fontSize = 200
paperSize = [ 75, 100 ]

paperAspect = paperSize[0] / paperSize[1]

p = subprocess.run(['identify', '-format', "%w %h", inImg], stdout=subprocess.PIPE, universal_newlines=True)
arr = p.stdout.split()
imageSize = [ int(arr[0]), int(arr[1]) ]

borderSize = [ int(imageSize[0] * 0.03), max(int(imageSize[1] * 0.03), 2 * fontSize) ]
outSize = [ imageSize[0] + borderSize[0] * 2, imageSize[1] + borderSize[1] * 2 ]

# increase a border to fit paperAspect (avoid any cropping when printed)                                            
if outSize[0] / outSize[1] > paperAspect:
  outSize[1] = outSize[0] / paperAspect
  borderSize[1] = int((outSize[1] - imageSize[1]) / 2)
else:
  outSize[0] = outSize[1] * paperAspect
  borderSize[0] = int((outSize[0] - imageSize[0]) / 2)

textOffset = int(imageSize[1] / 2 + fontSize)
args = ['convert', '-border', '{:d}x{:d}'.format(borderSize[0], borderSize[1]), '-bordercolor', 'white', '-pointsize', str(fontSize), '-gravity', 'center', '-font', font, '-draw', 'text 0,{:d} "{:s}"'.format(textOffset, caption), inImg, outImg]
# print('args:', args)
p = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=True)

  


