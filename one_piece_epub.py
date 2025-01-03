﻿import os
import re
import requests
from bs4 import BeautifulSoup
import argparse
import subprocess
from lxml import etree
from html import escape
from uuid import uuid4
import datetime
import zipfile
import imagesize


# Function to download images from a given URL
def download_images_from_url(url, directory):
    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Send a request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all image tags
    img_tags = soup.find_all('img')

    # Download each image
    has_pngs = False
    for img in img_tags:
        img_url = img['src']

        # Remove potential broken query parameters from the URL
        img_url = img_url.split('?')[0].strip()

        file_extension = os.path.splitext(img_url)[1].lower()

        if file_extension in ['.jpg', '.jpeg', '.png']:
            # Get the image file name
            img_name = os.path.basename(img_url)
            img_path = os.path.join(directory, img_name)

            # Download the image and save it
            img_data = requests.get(img_url).content
            with open(img_path, 'wb') as handler:
                handler.write(img_data)

            # Convert .png to .jpg for file size and performance on ereader

            if file_extension == '.png':
                has_pngs = True

                # Generate the converted image path
                img_converted_path = os.path.splitext(img_path)[0] + '.jpg'

                # Use ImageMagick to convert the image from PNG to JPG
                result = subprocess.run(
                    ['magick', 'convert', img_path, '-quality', '70', img_converted_path],
                    capture_output=True, text=True
                )

                if result.returncode == 0:
                    # Remove the original PNG file
                    os.remove(img_path)
                else:
                    print(f"ImageMagick conversion failed: {result.stderr}")

    chapter = os.path.basename(directory)
    print(f"Finished downloading chapter {chapter}.")
    if has_pngs:
        print(F"Converted png images to jpgs for chapter {chapter}")


# Function to scrape and download images
def scrape_images(chapter):
    base_url = "https://ww10.readonepiece.com/chapter/one-piece-digital-colored-comics-chapter-"
    url = f"{base_url}{chapter:03}/"
    directory = f"scraped/one-piece-colored-{chapter}"
    print(f"Downloading images for chapter {chapter}...")
    download_images_from_url(url, directory)


# Function to split landscape images
def split_landscape_images(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                width, height = imagesize.get(file_path)
                if width > height:  # landscape
                    file_name, file_extension = os.path.splitext(file_path)
                    output_pattern = f"{file_name}_%d{file_extension}"
                    subprocess.run(['magick', file_path, '-crop', '2x1@', '+repage', output_pattern])
                    os.remove(file_path)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")


# Function to create EPUB
def create_epub(directory, output, title="Unknown Title", author="Unknown Author", direction="rtl"):
    uid_format = '{:03d}'
    namespaces = {'OPF': 'http://www.idpf.org/2007/opf', 'DC': 'http://purl.org/dc/elements/1.1/'}
    container_path = 'META-INF/container.xml'
    container_xml = '''<?xml version='1.0' encoding='utf-8'?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile media-type="application/oebps-package+xml" full-path="OEBPS/content.opf"/>
  </rootfiles>
</container>
'''
    ibooks_display_options_path = 'META-INF/com.apple.ibooks.display-options.xml'
    ibooks_display_options_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<display_options>
  <platform name="*">
    <option name="fixed-layout">true</option>
    <option name="open-to-spread">false</option>
  </platform>
</display_options>
'''
    imagestyle_css = '''
@page {
  padding: 0;
  margin: 0;
}
html,
body {
  padding: 0;
  margin: 0;
  height: 100%;
}
#image {
  width: 100%;
  height: 100%;
  display: block;
  margin: 0;
  padding: 0;
}
'''
    image_types = {'jpeg': 'image/jpeg', 'jpg': 'image/jpeg', 'png': 'image/png', 'svg': 'image/svg+xml'}

    def image2xhtml(imgfile, width, height, title, epubtype='bodymatter', lang='en'):
        content = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{lang}">
<head>
  <meta name="viewport" content="width={width}, height={height}"/>
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="imagestyle.css"/>
</head>
<body epub:type="{epubtype}">
  <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="image" version="1.1" viewBox="0 0 {width} {height}">
    <image width="{width}" height="{height}" xlink:href="{escape(imgfile)}"/>
  </svg>
</body>
</html>'''
        return content

    def create_opf(title, author, bookId, imageFiles):
        package_attributes = {'xmlns': namespaces['OPF'], 'unique-identifier': 'bookId', 'version': '3.0',
                              'prefix': 'rendition: http://www.idpf.org/vocab/rendition/#', 'dir': direction}
        nsmap = {'dc': namespaces['DC'], 'opf': namespaces['OPF']}
        root = etree.Element('package', package_attributes)
        metadata = etree.SubElement(root, 'metadata', nsmap=nsmap)
        etree.SubElement(metadata, 'meta', {'property': 'dcterms:modified'}).text = datetime.datetime.now().strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        etree.SubElement(metadata, '{' + namespaces['DC'] + '}identifier', {'id': 'bookId'}).text = bookId
        etree.SubElement(metadata, '{' + namespaces['DC'] + '}title').text = title
        etree.SubElement(metadata, '{' + namespaces['DC'] + '}creator', {'id': 'creator'}).text = author
        etree.SubElement(metadata, 'meta',
                         {'refines': '#creator', 'property': 'role', 'scheme': 'marc:relators'}).text = 'aut'
        etree.SubElement(metadata, '{' + namespaces['DC'] + '}language').text = 'en'
        etree.SubElement(metadata, 'meta', {'name': 'cover', 'content': 'img-' + uid_format.format(0)})
        etree.SubElement(metadata, 'meta', {'property': 'rendition:layout'}).text = 'pre-paginated'
        etree.SubElement(metadata, 'meta', {'property': 'rendition:orientation'}).text = 'portrait'
        etree.SubElement(metadata, 'meta', {'property': 'rendition:spread'}).text = 'landscape'
        width, height = imagesize.get(os.path.join(directory, imageFiles[0]))
        etree.SubElement(metadata, 'meta', {'name': 'original-resolution', 'content': f'{width}x{height}'})
        manifest = etree.SubElement(root, 'manifest')
        etree.SubElement(manifest, 'item', {'href': 'imagestyle.css', 'id': 'imagestyle', 'media-type': 'text/css'})
        for i, img in enumerate(imageFiles):
            uid = uid_format.format(i)
            ext = os.path.splitext(img)[1][1:]
            imgattrs = {'href': f'images/page-{uid}.{ext}', 'id': f'img-{uid}', 'media-type': image_types[ext]}
            if i == 0:
                imgattrs['properties'] = 'cover-image'
            etree.SubElement(manifest, 'item', imgattrs)
            etree.SubElement(manifest, 'item',
                             {'href': f'page-{uid}.xhtml', 'id': f'page-{uid}', 'media-type': 'application/xhtml+xml',
                              'properties': 'svg'})
        etree.SubElement(manifest, 'item',
                         {'href': 'toc.ncx', 'id': 'ncxtoc', 'media-type': 'application/x-dtbncx+xml'})
        etree.SubElement(manifest, 'item',
                         {'href': 'toc.xhtml', 'id': 'toc', 'media-type': 'application/xhtml+xml', 'properties': 'nav'})
        spine = etree.SubElement(root, 'spine', {'toc': 'ncxtoc', 'page-progression-direction': direction})
        for i, img in enumerate(imageFiles):
            uid = uid_format.format(i)
            props = 'page-spread-left' if (i % 2 == 0 and direction == 'ltr') or (
                    i % 2 != 0 and direction == 'rtl') else 'page-spread-right'
            etree.SubElement(spine, 'itemref', {'idref': f'page-{uid}', 'properties': props})
        return etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)

    def create_ncx(title, author, book_id):
        return f'''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<ncx:ncx xmlns:ncx="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <ncx:head>
    <ncx:meta name="dtb:uid" content="{book_id}"/>
    <ncx:meta name="dtb:depth" content="1"/>
    <ncx:meta name="dtb:totalPageCount" content="0"/>
    <ncx:meta name="dtb:maxPageNumber" content="0"/>
  </ncx:head>
  <ncx:docTitle>
    <ncx:text>{escape(title)}</ncx:text>
  </ncx:docTitle>
  <ncx:docAuthor>
    <ncx:text>{escape(author)}</ncx:text>
  </ncx:docAuthor>
  <ncx:navMap>
    <ncx:navPoint id="p1" playOrder="1">
      <ncx:navLabel><ncx:text>{escape(title)}</ncx:text></ncx:navLabel>
      <ncx:content src="page-000.xhtml"/>
    </ncx:navPoint>
  </ncx:navMap>
</ncx:ncx>'''

    def create_nav(title, page_count):
        pages = [f'          <li><a href="page-{uid_format.format(i)}.xhtml">{i}</a></li>' for i in range(page_count)]
        pages.pop(0)
        pages_string = '\n'.join(pages)
        return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">
  <head>
    <title>{escape(title)}</title>
  </head>
  <body>
    <section class="frontmatter" epub:type="frontmatter toc">
      <h1>Table of Contents</h1>
      <nav epub:type="toc" id="toc">
        <ol>
          <li epub:type="chapter"><a href="page-000.xhtml">{escape(title)}</a></li>
{pages_string}
        </ol>
      </nav>
    </section>
  </body>
</html>'''

    # Function to extract parts from the filename
    def extract_parts(filename):
        match = re.search(r'(\d+)(_?[0-1])?\.', filename)
        if match:
            num_part = int(match.group(1))
            sub_part = match.group(2)
            if sub_part:
                sub_part = int(sub_part.replace('_', ''))
            else:
                sub_part = -1  # Use -1 for filenames without _0 or _1
            return num_part, sub_part
        return -1, -1  # Use -1, -1 for filenames that don't match the pattern

    # Function to sort the filenames
    def sort_files(filenames, direction='ltr'):
        print('before sort:', filenames)
        reverse = direction == 'rtl'

        def sort_key(filename):
            import re
            # Extract the numerical and alphabetical parts
            match = re.match(r"(\d+)([a-z]?)\.(jpg|jpeg|png)", filename)
            number = int(match.group(1))
            letter = match.group(2)
            return number, letter  # Sort by number, then by letter

        return sorted(filenames, key=sort_key, reverse=reverse)

    image_files = sort_files([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
                              and os.path.splitext(f)[1][1:] in image_types])

    if len(image_files) < 1:
        print('Too few images:', len(image_files))
        return

    prev_compression = zipfile.zlib.Z_DEFAULT_COMPRESSION
    zipfile.zlib.Z_DEFAULT_COMPRESSION = 9

    output_zip = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    output_zip.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
    output_zip.writestr(container_path, container_xml)
    output_zip.writestr(ibooks_display_options_path, ibooks_display_options_xml)
    output_zip.writestr('OEBPS/content.opf', create_opf(title, author, f'urn:uuid:{uuid4()}', image_files))
    output_zip.writestr('OEBPS/toc.ncx', create_ncx(title, author, f'urn:uuid:{uuid4()}'))
    output_zip.writestr('OEBPS/toc.xhtml', create_nav(title, len(image_files)))
    output_zip.writestr('OEBPS/imagestyle.css', imagestyle_css)

    for i, img in enumerate(image_files):
        uid = uid_format.format(i)
        page_title = 'Cover' if i == 0 else f'Page {i}'
        epubtype = 'cover' if i == 0 else 'bodymatter'
        ext = os.path.splitext(img)[1][1:]
        width, height = imagesize.get(os.path.join(directory, img))
        html = image2xhtml(f'images/page-{uid}.{ext}', width, height, page_title, epubtype)
        output_zip.writestr(f'OEBPS/page-{uid}.xhtml', html)
        output_zip.write(os.path.join(directory, img), f'OEBPS/images/page-{uid}.{ext}')

    output_zip.close()
    zipfile.zlib.Z_DEFAULT_COMPRESSION = prev_compression

    print('Complete! Saved EPUB as ' + output, flush=True)


# Main function to handle argument parsing and execution
def main():
    parser = argparse.ArgumentParser(
        description='Download, process, and convert One Piece Digital Colored Comics chapters into EPUB format.')
    parser.add_argument('start_chapter', type=int, help='The starting chapter number (inclusive)')
    parser.add_argument('end_chapter', type=int, help='The ending chapter number (inclusive)')
    parser.add_argument('-d', '--dir', choices=['ltr', 'rtl'], default='rtl',
                        help='The direction for sorting and processing images (default: rtl)')

    args = parser.parse_args()

    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for chapter in range(args.start_chapter, args.end_chapter + 1):
        # print(f"Scraping images for chapter {chapter}...", flush=True)
        # scrape_images(chapter)
        # directory = f"scraped/one-piece-colored-{chapter}"
        # print(f"Processing images for chapter {chapter}...", flush=True)
        # split_landscape_images(directory)

        title = f"One Piece Colored {chapter}"
        author = "Eiichiro Oda"

        output_file = os.path.join(output_dir, f"one_piece_colored_{chapter}.epub")
        directory = f"scraped/one-piece-colored-{chapter}"
        create_epub(directory, output_file, title, author, args.dir)


if __name__ == "__main__":
    main()
