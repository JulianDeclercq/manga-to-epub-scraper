# One Piece Digital Colored Comics to EPUB Converter
This Python script downloads One Piece Digital Colored Comics chapters, processes the images, and converts them into EPUB files.

## Features
- Downloads chapters from the specified range.
- Splits landscape images into multiple pages.
- Creates one EPUB file per chapter.
 
## Planned Features
As the repository name suggest, I plan to make this script more generic in the close future, allowing users to input their own sources and url patterns so it can be used for different mangas.

## Installation

### Dependencies

#### Python Packages
```bash
python3 -m pip install requests beautifulsoup4 lxml imagesize
```

#### ImageMagick

**Windows:**
1. Download and install from the [ImageMagick official website](https://imagemagick.org/script/download.php).
2. Ensure to check the option to add ImageMagick to your system PATH during installation.

**macOS:**
```bash
brew install imagemagick
```

## Usage

Run the script with the following command:
```bash
python3 one_piece_epub.py <start_chapter> <end_chapter> [-d <direction>]
```

- `<start_chapter>`: The starting chapter number (inclusive).
- `<end_chapter>`: The ending chapter number (inclusive).
- `[-d <direction>]`: (Optional) The direction for sorting and processing images. It can be either `ltr` (left-to-right) or `rtl` (right-to-left). The default is `rtl`.

Example:
```bash
python3 one_piece_epub.py 100 105 -d rtl
```

This will download chapters 100 to 105, process the images with right-to-left sorting, and create EPUB files in the `output` directory.

Another example:
```bash
python3 one_piece_epub.py 100 105 -d ltr
```

This will download chapters 100 to 105, process the images with left-to-right sorting, and create EPUB files in the `output` directory.

## Sources

Big thanks to [this directory to epub gist](https://gist.github.com/daniel-j/613a506a0ec9c7037897c4b3afa8e41e) for doing most of the heavy lifting!

Also, shoutout to [this shell gist](https://gist.github.com/imkh/1e349de95879d22445550f3ac222fc0f) for the idea on checking and splitting up landscape pages.
