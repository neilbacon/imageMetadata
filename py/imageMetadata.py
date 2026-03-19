#! /usr/bin/env python3

# ubuntu 16.04 LTS and 17.10 requirements: 
# sudo apt-get install python3-gi libexiv2-dev libgexiv2-2 gir1.2-gexiv2 

import argparse
import os
import re
import requests
import shutil
from datetime import datetime
from stat import S_IREAD, S_IRGRP, S_IROTH

# else PyGIWarning: GExiv2 was imported without specifying a version first
import gi
gi.require_version('GExiv2', '0.10') 

from gi.repository.GExiv2 import Metadata

DATE_RE = re.compile(r'(\d{4})[/-]?(\d{2})[/-]?(\d{2})')    

DATE_FORMAT = '%Y:%m:%d %H:%M:%S'
SEESTAR_DATE_FORMAT = '%Y.%m.%d %H:%M:%S'

# Google API for geocoding, now requires API key
API_URL='https://maps.googleapis.com/maps/api/geocode/json'
API_KEY=None # put your Google API key here or use --apikey

# Usage:
# curl "https://maps.googleapis.com/maps/api/geocode/json?address=Europe,France,Paris$ " > goo.json
# jq '.results[0] | { addr: .formatted_address, loc: .geometry.location } ' goo.json 
# {
#  "addr": "Paris, France",
#  "loc": {
#    "lat": 48.856614,
#    "lng": 2.3522219
#  }
# }
#
# For Sydney it's 
 # {
 #    "lat" : -33.8688197,
 #    "lng" : 151.2092955
 # }
 
geoCache = {
    'Oceania,Australia,NSW,Sydney': {'lat': -33.8688197, 'lng': 151.2092955},
    'Oceania,Australia,Sydney': {'lat': -33.8688197, 'lng': 151.2092955},
    'Oceania,New Zealand,North Island,Auckland,Domain - Auckland': {'lat': -36.858931, 'lng': 174.7754857}
}

# input : 'Europe, France, Paris' or an address etc. in the conventions for the country its in
# output: {'lat': 48.856614, 'lng': 2.3522219}
def geoCode(place, apikey):
    addr = ','.join(place)
    loc = geoCache[addr] if addr in geoCache else None
    if not loc:
        r = requests.get(API_URL, params={ 'address': addr, 'key': apikey } )
        resp = r.json()
        if resp['status'] == 'OK':
            loc = resp['results'][0]['geometry']['location']
            geoCache[addr] = loc
        else:
            print('error from google maps api for {}: {}'.format(place, resp['status']))
            if len(place) > 1:
                loc = geoCode(place[:-1], apikey) # recursively retry with last place component removed
                if loc: geoCache[addr] = loc
    print('geoCode: loc = {}'.format(loc))
    return loc
    
def dateFromPath(path):
    m = DATE_RE.search(path)
    if m:
        def g(i): return int(m.group(i))
        yyyy = g(1)
        if (yyyy > 1900 and yyyy < 2050): return datetime(yyyy, g(2), g(3))
    return None

def updateListMeta(m, tag, remove, add):
    vals = m.try_get_tag_multiple(tag)
    vals = [ v for v in vals if not remove in v ] if vals else [] # filter any existing v containing remove
    vals.append(add)
    m.try_set_tag_multiple(tag, vals)
    
def getMeta(path, args):
    m = Metadata(path)
    
    if args.print:
        print('getMeta: {} exif_tags, {} iptc_tags, {} xmp_tags, path {}, dateFromPath {}'.format(
            len(m.get_exif_tags()), 
            len(m.get_iptc_tags()),
            len(m.get_xmp_tags()),
            path,
         dateFromPath.strftime(DATE_FORMAT) if dateFromPath else None
        ))
        
        for t in m.get_tags():
            # if t != 'Exif.Photo.MakerNote': # avoid big binary? item
            if any(x in t for x in [ 'Date', 'Image.Make', 'Model', 'Categories', 'GPS', 'Latitude', 'Longitude' ]):
                print('getMeta: {} -> {}'.format(t, m.get(t)))
            if any(x in t for x in [ 'Tags', 'LastKeywordXMP', 'HierarchicalSubject', 'CatalogSets', 'Subject', 'Keywords' ]):
                print('getMeta: {} => [ {} ]'.format(t, ', '.join(m.get_tag_multiple(t))))
    
    return m
    
def dateFromMeta(m):
    for t in ['Exif.Photo.DateTimeOriginal', 'Exif.Photo.DateTimeDigitized', 'Exif.Image.DateTime' ]:
        d = m.get(t)
        if d:
            try:
                return datetime.strptime(d, DATE_FORMAT)
            except Exception as e:
                return datetime.strptime(d, SEESTAR_DATE_FORMAT) # SeeStar uses a different invalid? date format
    return None

def setDateFields(m, d):
    tagsToSet =  [ 'Exif.Image.DateTime', 'Exif.Photo.DateTimeOriginal' ]
    if not args.scanned: tagsToSet.append('Exif.Photo.DateTimeDigitized')
    ds = d.strftime(DATE_FORMAT)
    for t in tagsToSet:
        m[t] = ds # m.set(t, d) doesn't work for dates
    # delete proprietary date tags and tags in other formats
    for t in [ 'Xmp.exif.DateTimeOriginal', 'Xmp.photoshop.DateCreated', 'Xmp.tiff.DateTime', 'Xmp.video.DateTimeOriginal', 'Xmp.video.DateUTC', 'Xmp.video.ModificationDate', 'Xmp.xmp.CreateDate', 'Xmp.xmp.MetadataDate', 'Xmp.xmp.ModifyDate' ]:
        m.clear_tag(t)

def processImage(path, args, dateFromPath):
    metaPath = re.sub('\\.fit$', '.jpg', path) if args.seestar and path.endswith('.fit') else path
    print('processImage: metaPath = {}'.format(metaPath))
    m = getMeta(metaPath, args) # for .fit, get meta from .jpg

    if not args.tagfilter or any(t.startswith(args.tagfilter) for t in m.get_tag_multiple('Xmp.digiKam.TagsList')):
        d = dateFromMeta(m)
        dst = moveFile(path, d, args.moveimage)
        os.chmod(dst, S_IREAD|S_IRGRP|S_IROTH)

        mod = False
    
        if args.geocode and args.apikey and not m.get('Exif.GPSInfo.GPSLatitude'):
            place = [ x for x in m.get_tag_multiple('Xmp.digiKam.TagsList') if x.startswith('Places/') ]
            if len(place) > 0:
                place = place[0].replace('Places/', '').split('/')
                loc = geoCode(place, args.apikey)
                if loc:
                    m.set_gps_info(loc['lng'], loc['lat'], 0.0)
                    mod = True
        
        if args.seestar and d:
            setDateFields(m, d) # correct invalid SeeStar date format
            mod = True
            
        if args.datepath and dateFromPath and (args.datepathforce or args.scanned or not d):
            d = dateFromPath.strftime(DATE_FORMAT)
            print('processImage: setting date from dirname: d = {} for {}'.format(d, path))
            setDateFields(m, d)
            mod = True
            
        if args.scanned:
            t = 'Exif.Photo.DateTimeDigitized'
            d = m.get(t)
            print('scanned date = {}'.format(d))
            if not d:
                d = datetime.fromtimestamp(os.path.getmtime(path)).strftime(DATE_FORMAT)
                m[t] = d 
                mod = True
                
        if args.takenby:
            model = m.get('Exif.Image.Model')
            if not model and args.scanned: model = 'Scanned'
            if model:
                for t in [ 'Iptc.Application2.Keywords', 'Xmp.MicrosoftPhoto.LastKeywordXMP' ]:
                    while m.has_tag(t): m.clear_tag(t)  # delete; can get repeats
                # digiKam uses / separator
                remove = args.takenby
                add = remove + '/' + model
                for t in [ 'Xmp.digiKam.TagsList' ]:
                    updateListMeta(m, t, remove, add)
                # Adobe light room and mediapro use | separator
                remove = args.takenby.replace('/', '|')
                add = remove + '|' + model
                for t in [ 'Xmp.lr.hierarchicalSubject', 'Xmp.mediapro.CatalogSets' ]:
                    updateListMeta(m, t, remove, add)
                mod = True
        
        if mod:
            m.save_external('{}.xmp'.format(dst))

    
def processVideo(path, args, dateFromPath):
    moveFile(path, dateFromPath, args.movevideo)

def moveFile(path, d, dstBaseDir):
    if d and dstBaseDir:
        srcDir = os.path.dirname(path)
        dstDir = '{}/{:04d}/{:02d}/{:02d}'.format(dstBaseDir, d.year, d.month, d.day)
        if dstDir != srcDir:
            if not os.path.exists(dstDir): os.makedirs(dstDir)
            dst = uniquePath(dstDir, os.path.basename(path))
            print('moveFile: srcDir = {}, dstDir = {}, dst = {}'.format(srcDir, dstDir, dst))
            shutil.move(path, dst)
            return dst
    return path

# return a destination path that does not match an existing file
# first try {dir}/{basename}, but if that exists try {dir}/{name}_{i}{.ext} for i = 1, 2, 3 ...
# until we find a path that does not already exist
def uniquePath(dir, basename):
    name, ext = os.path.splitext(basename)
    path = os.path.join(dir, basename)
    i = 1
    # print('uniquePath: path = {}'.format(path))
    while os.path.isfile(path):
        path = os.path.join(dir, '{}_{}{}'.format(name, i, ext))
        # print('uniquePath: path = {}'.format(path))
        i = i + 1
    return path
    
  
# Example usage:
# python3 im.py --root /media/neil/NIKON\ Z\ 6_2/ --takenby 'Taken by/byNeil' --moveimage /media/neil/NB-Photo/Photos/
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser( description = '''Organise a photo collection by updating metadata and moving files.
This is tailored to my needs and will need hacking about to suit yours.

I use hierarchical tags in digikam which have / separated items. The hierarchical tags used
by Adobe light room and mediapro are | separated and these are also updated.

I use a tag tree Taken by/{photographer}/{camera model} so that I can search by photographer
or by which camera they used. This is set by the --takenby option.

I also use a tag tree Places/{continent}/{country}/... which can be populated by Digikam's reverse geocoder (using GPS location metadata) or can be manually
set and used to roughly geocode with the --geocode option (sets GPS location metadata only for photos with no existing GPS metadata, requires a Google Maps API key).

I like my photos stored under a folder yyyy/mm/dd reflecting the date taken and this is done
by the --moveimage option.
If moving would collide with another file name the new name is modified to make it unique by
adding _{number} just before the extention.
However date metadata is sometimes missing or wrong for old cameras and scanned
images, so images placed a folder with yyyy-mm-dd somewhere in the name can have the metadata
set to this date using the --datepath option (only if not already set or certain other conditions are met).
After moving, image files are made read-only and metadata is written to XMP sidecar files
which are recognized by most photo managers. 

Scanned images can have the digitized date metadata set from the file creation date using the
--scanned option.

With the --seestar option .fit and .jpg files are processed instead of the usual list of image types:
 - .fit astronomical image files are processed using metadata from the corresponding .jpg file (.fit files have other uses too, so we don't want to process them without --seestar)
 - *_thn.jpg thumbnail images are ignored (other jpg's are processed normally)

If image metadata is changed, your photo manager needs to resync its metadata from the XMP sidecar
files. Digikam does this automatically on startup or you can manually refresh.
''')
    parser.add_argument("--root",     help="ROOT dir of images to process (default .)")
    parser.add_argument("--tagfilter",  help="only operate on files with a tag starting with this")
    parser.add_argument("--takenby",  help="remove existing hierarcical tag containing TAKENBY and add {TAKENBY}/{camera model}")
    parser.add_argument("--moveimage", help="move image to MOVEIMAGE/yyyy/mm/dd/")
    parser.add_argument("--movevideo", help="move video to MOVEVIDEO/yyyy/mm/dd/")
    parser.add_argument("--seestar",  action="store_true", help="SeeStar telescope mode: move *.fit files and skip *_thn.jpg thumbnails")
    parser.add_argument("--geocode",  action="store_true", help="set missing GPS metadata from place name after 'Places/' hierarchical tag")
    parser.add_argument("--apikey",  help="your API key for Google Maps geocoding")
    parser.add_argument("--datepath", action="store_true", help="set lots of date tags from yyyy-mm-dd in dirname (only if not alreadt set)")
    parser.add_argument("--datepathforce", action="store_true", help="use datepath date to overwrite existing date dags")
    parser.add_argument("--scanned",  action="store_true", help="as datepathforce but leave {digitized date} as is if set, else set from file timestamp, also sets {camera model}=scanned")
    parser.add_argument("--print",  action="store_true", help="print selected metadata read from each image")
    args = parser.parse_args()
    if not args.apikey: args.apikey = API_KEY
    print('args: root = {}, datepath = {}, scanned = {}, takenby = {}'.format(args.root, args.datepath, args.scanned, args.takenby))
    
    for dirname, dirnames, filenames in os.walk(args.root if args.root else '.'):
        # process .fit files before .jpg files so the .fit processing can use the .jpg metadata
        ordered = [f for f in filenames if f.endswith('.fit')] + [f for f in filenames if not f.endswith('.fit')]
        for filename in ordered:
            name, ext = os.path.splitext(filename)
            path = os.path.join(dirname, filename)
            date = dateFromPath(path)
            isImage = ext.upper() in [ '.JPG', '.FIT' ] and not name.endswith('_thn') if args.seestar else ext.upper() in [ '.JPG', '.JPEG', '.WEBP', '.TIF', '.TIFF', '.PNG', '.HEIC', '.NEF', '.DNG', '.GIF' ] 
            isVideo = ext.upper() in [ '.AVI', '.MOV', '.MP4', '.MTS' ]
            print('path = {}, isImage = {}, isVideo = {}'.format(path, isImage, isVideo))
            try:
                if isImage:
                    processImage(path, args, date)
                    # Can't read video metadata: GLib.Error: GExiv2: unsupported format (501)
                    # Sony a6000 stores some images with no metadata at all: gi.repository.GLib.GError: GExiv2: corrupted image metadata (59)
                if isVideo and date:
                    processVideo(path, args, date)
            except Exception as e:
                print(e)
                
    # print('geoCache = {}'.format(geoCache))
