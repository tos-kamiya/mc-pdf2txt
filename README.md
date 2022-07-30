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

(2) Install mc-pdf2txt

To make `mc-pdf2txt` compatible with both `docopt` and `docopt-ng`, dependencies on them are now explicitly extra dependencies.

If you know either `docopt` or `docopt-ng` is already installed on your system, just try the following:

```sh
pip3 install mc-pdf2txt
```

If you are unsure `docopt` or `docopt-ng` is installed on your system, try the following:

```sh
pip3 install mc-pdf2txt[docopt-ng]
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
  --timeout SEC     Timeout in sec to exec `pdftoppm` [default: 60].
  --page-separator LINE     String to be output as page separator [default: ---].
  --psm VALUE       Page segmentation mode of `tessoract-ocr` [default: 3].
  --verbose         Verbose.
```
