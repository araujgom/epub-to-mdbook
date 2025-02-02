import sys
from epub_parser.converter import EpubConverter

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python main.py <input.epub> <output_dir>")
        sys.exit(1)

    converter = EpubConverter(sys.argv[1], sys.argv[2])
    converter.convert_to_md()
    print(f"mdBook project created at {sys.argv[2]}")