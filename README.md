mc-pdf2txt
==========

**NOTICE: As of September 2024, https://github.com/VikParuchuri/marker offers a far superior tool. This repository will be archived.**

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

(2) Install mc-pdf2txt

```sh
pip3 install mc-pdf2txt
```

## Usage

```
Usage:
  mc-pdf2txt [options] <input>...

Options:
  -l LANG           Language, such as `eng`, `jpn`, or `eng+jpn`.
  <input>           Input PDF file.
  -o OUTPUT         Output text file.
  -r DPI            Resolution of temporary image file [default: 600].
  --page-separator LINE     String to be output as page separator [default: ---].
  --psm VALUE       Page segmentation mode of `tessoract-ocr` [default: 3].
  --verbose         Verbose.
```
