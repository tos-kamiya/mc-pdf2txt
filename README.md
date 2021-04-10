mc-pdf2txt
==========

Convert multi-column pdf to text with `poppler` and `tesseract`.

## Install

(1) Install dependencies:

Install poppler.

```sh
sudo apt install poppler-utils
```

Install tesseract-ocr

```sh
sudo apt install tesseract-ocr
```

with the language data files of your choice, e.g.,

```sh
sudo apt install tesseract-ocr-jpn
```

Install docopt.

```sh
sudo python3 -m pip install docopt
```

(2) Copy `mc-pdf2txt` to a directory on the path, such as `~/bin/`.

## Usage

```
Usage:
  mc-pdf2txt [options] <input>...

Options:
  -l LANG           Language, such as `eng`, `jpn`, or `eng+jpn`.
  <input>           Input PDF file.
  -o OUTPUT         Output text file.
  -r DPI            Resolution of temporary image file [default: 600].
  --timeout SEC     Timeout in sec to exec `pdftoppm` [default: 60].
  --page-separator LINE     String to be output as page separator [default: ---].
  --psm VALUE       Page segmentation mode of `tessoract-ocr` [default: 3].
```
