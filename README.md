# Python

## Image Metadata

This python3 script facilitates maintaining a large photo collection by performing bulk metadata updates and moving photos and videos into a uniform directory structure. This is sufficiently dangerous that you should do a backup first. It is tailored to my needs and will need hacking about to suit yours. See the `--help` option output for a description of the options available.
Example usage:

    python3 ~/py/imageMetadata.py --root oldPics/2000-10-22/ \ # input
      --datepath \ # use above date to set missing date metadata
      --moveimage pics --movevideo video \
      --takenby 'Taken by/byNeil' \
      --geocode --apikey 'your-google-api-key-here'

### Dependencies
For Ubuntu 16.04 LTS and 17.10: 

    sudo apt-get install python3 python3-gi libexiv2-dev libgexiv2-2 gir1.2-gexiv2 

### Hierarchical Tags
I use hierarchical tags in digikam which have `/` separated items. The hierarchical tags used
by Adobe light room and mediapro are `|` separated are these are also updated.

I use a tag tree `Taken by/{photographer}/{camera model}` so that I can search by photographer or by which camera they used. This is set by the `--takenby` option. The `{camera model}` is of course useful in later correcting the `{photographer}` part.

I also use a tag tree `Places/{continent}/{country}/...` which can be used to geocode with the `--geocode` option (only photos with no existing GPS coordinates). A Google Maps API key is required and can either be set as API_KEY in the script or with the `--apikey` option.

### Dates
I like my photos stored under a folder `yyyy/mm/dd` reflecting the date taken and this is done by the `--moveimage` option. If moving would collide with another file name the new name is modified to make it unique by adding `_{number}` just before the extention. However date metadata is sometimes missing or wrong for old cameras and scanned images, so images placed in a folder with `yyyy-mm-dd` somewhere in the path can have the metadata set to this date using the `--datepath` option (only if not already set or certain other conditions are met).

Digikam's import can create date based folders as above (set Date format: `Custom`  `yyyy/MM/dd`), however I find it putting some images in the folder for the following day and have yet to track down the cause.

Scanned images can have the digitized date metadata set from the file creation date using the `--scanned` option, which also sets `{camera model}` mentioned above to `scanned`.

### Video
The `--movevideo` option moves videos using a date parsed from the existing file path, because the GExiv2 metadata library used by this script cannot handle video metadata.

### Resyncing Metadata
If image metadata is changed, your photo manager needs to resync its metadata from the image
files. DigiKam does this automatically on startup.

## Image Border Caption
`imageBorderCaption.py` Adds a border and caption to an image.

# Bash

## Backup

There are lots of articles on how to use rsync for incremental backups. `backup.sh` is my version.

## Functions

`functions.sh` contains some utility functions.

## Image Shrink
`imageShrink.sh` scales down the number of pixels, greatly reducing file size.

## Scan Shrink
`scanShrink.sh` greatly reduces the size of a PDF file produced by Epson's `Image Scan for Linux` which stores PNG images for each page in the PDF. The page images are extracted, shrunk as above and converted to JPG, then used to create a much smaller PDF file. For ADF duplux documents `Image Scan for Linux` stores even pages up-side-down with metadata to say it should be flipped. The above processing appears to ignore this metadata, so with `-duplex` the script flips these images.
