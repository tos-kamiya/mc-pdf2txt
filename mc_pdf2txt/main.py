import argparse
import pathlib
from shlex import quote
from shutil import copy
import subprocess
import sys
import tempfile


try:
    from ._version import __version__
except:
    __version__ = "(unknown)"


def main():
    parser = argparse.ArgumentParser(description='Convert multi-column pdf to text with `poppler` and `tesseract`.')

    parser.add_argument(dest='input_file', nargs='+', help='Input PDF file(s).')

    parser.add_argument('--lang', '-l', dest='lang', help='Language, such as `eng`, `jpn`, or `eng+jpn`.')
    parser.add_argument('--output', '-o', dest='output', help='Output text file.')
    parser.add_argument('--resolution', '-r', dest='resolution', type=int, default=600, help='Resolution of temporary image file [default: 600].')
    parser.add_argument('--timeout', dest='timeout', type=int, default=60, help='Timeout in sec to exec `pdftoppm` [default: 60].')
    parser.add_argument('--page-separator', dest='page_separator', default='---', help='String to be output as page separator [default: "---"].')
    parser.add_argument('--psm', dest='psm', default=3, help='Page segmentation mode of `tesseract-ocr` [default: 3].')
    parser.add_argument('--verbose', action='store_true', help='Verbose.')
    parser.add_argument("--version", action="version", version="%(prog)s " + __version__)

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

    args = parser.parse_args()

    def verbose_message(msg):
        if args.verbose:
            print(msg, file=sys.stderr)

    def run(cmd, check=False, timeout=None):
        if args.verbose:
            print('> exec: ' + ' '.join(quote(c) for c in cmd), file=sys.stderr)
        subprocess.run(cmd, check=check, timeout=timeout)

    with tempfile.TemporaryDirectory() as temp_dir:
        verbose_message(f'> make temporary dir: {quote(str(temp_dir))}')
        temp_dir_path = pathlib.Path(temp_dir)

        suffix_len = len("%d" % len(args.input_file))
        for i, input_file in enumerate(args.input_file):
            image_file_name_body = f'image-%0{suffix_len}d' % i
            if input_file.lower().endswith('.pdf'):
                cmd = [
                    'pdftoppm',
                    '-r', '%d' % args.resolution,
                    '-gray',
                    '-png', input_file, 
                    str(temp_dir_path / image_file_name_body)
                ]
                try:
                    run(cmd, check=True, timeout=args.timeout)
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
        if args.lang:
            cmd0.extend(['-l', args.lang])
        cmd0.extend(['--psm', '%d' % args.psm])
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
                lines.append(args.page_separator)  # add separator
                text_lines.extend(L + '\n' for L in lines)

        verbose_message(f'> remove temporary dir: {quote(str(temp_dir))}')

    if args.output:
        verbose_message(f'> write text to file: {quote(args.output)}')
        with open(args.output, 'w') as outp:
            outp.writelines(text_lines)
    else:
        sys.stdout.writelines(text_lines)


if __name__ == '__main__':
    main()

