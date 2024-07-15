# One Piece Digital Colored Comics to EPUB Converter
This Python script downloads One Piece Digital Colored Comics chapters, processes the images, and converts them into EPUB files.

## Features
- Downloads chapters from the specified range.
- Splits landscape images into multiple pages.
- Creates one EPUB file per chapter.

## Installation

### Dependencies

#### Python Packages
```bash
pip install requests beautifulsoup4 lxml imagesize
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
python one_piece_epub.py <start_chapter> <end_chapter>
```

- `<start_chapter>`: The starting chapter number (inclusive).
- `<end_chapter>`: The ending chapter number (inclusive).

Example:
```bash
python one_piece_epub.py 100 105
```

This will download chapters 100 to 105, process the images, and create EPUB files in the `output` directory.

## Planned Features
As the repository name suggest, I plan to make this script more generic in the close future, allowing users to input their own sources and url patterns so it can be used for different mangas.
