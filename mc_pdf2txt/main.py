from typing import List, Optional

import importlib
import os
import pathlib
from shlex import quote
from shutil import copy
import subprocess
import sys
import tempfile

from docopt import docopt
from init_attrs_with_kwargs import InitAttrsWKwArgs


VERSION = importlib.metadata.version("mc-pdf2txt")


class CLArgs(InitAttrsWKwArgs):
    lang: Optional[str]
    input: List[str]
    output: Optional[str]
    resolution: int
    timeout: int
    page_separator: str
    psm: int
    verbose: bool
    help: bool
    version: bool


__doc__ = """Convert multi-column pdf to text with `poppler` and `tesseract`.

Usage:
  mc-pdf2txt [options] <input>...

Options:
  --lang=LANG, -l LANG          Language, such as `eng`, `jpn`, or `eng+jpn`.
  <input>                       Input PDF file(s).
  --output=OUTPUT, -o OUTPUT    Output text file.
  --resolution=DPI, -r DPI      Resolution of temporary image file [default: 600].
  --timeout=SEC                 Timeout in sec to exec `pdftoppm` [default: 60].
  --page-separator=LINE         String to be output as page separator [default: "---"].
  --psm=VALUE                   Page segmentation mode of `tessoract-ocr` [default: 3].
  --verbose                     Verbose.
"""


def main():
    try:
        subprocess.check_output(['which', 'tesseract'])
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            sys.exit("Error: command not found: tesseract. (perhaps need to install `tesseract-ocr`)")
    try:
        subprocess.check_output(['which', 'pdftoppm'])
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            sys.exit("Error: command not found: pdftoppm. (perhaps need to install `poppler-utils`)")

    raw_args = docopt(__doc__, argv=sys.argv[1:], version="mc-pdf2txt %s" % VERSION)
    a = CLArgs(_cast_str_values=True, **raw_args)

    def verbose_message(msg):
        if a.option_verbose:
            print(msg, file=sys.stderr)

    def run(cmd, check=False, timeout=None):
        if a.option_verbose:
            print('> exec: ' + ' '.join(quote(c) for c in cmd), file=sys.stderr)
        subprocess.run(cmd, check=check, timeout=timeout)

    with tempfile.TemporaryDirectory() as temp_dir:
        verbose_message(f'> make temporary dir: {quote(str(temp_dir))}')
        temp_dir_path = pathlib.Path(temp_dir)

        suffix_len = len("%d" % len(a.input_files))
        for i, input_file in enumerate(a.input_files):
            image_file_name_body = f'image-%0{suffix_len}d' % i
            if input_file.lower().endswith('.pdf'):
                cmd = [
                    'pdftoppm',
                    '-r', '%d' % a.resolution,
                    '-gray',
                    '-png', input_file, 
                    str(temp_dir_path / image_file_name_body)
                ]
                try:
                    run(cmd, check=True, timeout=a.timeout)
                except subprocess.TimeoutExpired as e:
                    sys.exit("Timeout expired in running `pdftoppm`. Re-try with the lower resolution (-r) or the larger timeout (--timeout).")
            elif input_file.lower().endswith(('.png', '.jpg', '.jpeg', '.tif')):
                image_file_name = f'image-%0{suffix_len}d.{temp_dir_path.suffix}' % i
                copy(input_file, temp_dir_path / image_file_name)
            else:
                sys.exit('Error: unrecognized file format.')

        page_images = list(temp_dir_path.iterdir())
        page_images.sort()
        # print("page images = %s" % repr(page_images))

        cmd0 = ['tesseract']
        if a.lang:
            cmd0.extend(['-l', a.lang])
        cmd0.extend(['--psm', '%d' % a.psm])
        for pi in page_images:
            run(cmd0 + [str(pi), str(pi) + '.txt'], check=True)

        page_texts = [str(p) for p in temp_dir_path.glob('*.txt')]
        page_texts.sort()
        # print("page texts = %s" % page_texts)

        verbose_message(f'> read and join texts from files: {", ".join(quote(pt) for pt in page_texts)}')
        text_lines = []
        for pt in page_texts:
            with open(pt) as inp:
                lines = [L.rstrip() for L in inp.readlines()]
                lines.append(a.page_separator)  # add separator
                text_lines.extend(L + '\n' for L in lines)

        verbose_message(f'> remove temporary dir: {quote(str(temp_dir))}')

    if a.output_file:
        verbose_message(f'> write text to file: {quote(a.output_file)}')
        with open(a.output_file, 'w') as outp:
            outp.writelines(text_lines)
    else:
        sys.stdout.writelines(text_lines)


if __name__ == '__main__':
    main()

