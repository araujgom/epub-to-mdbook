import argparse
import sys
from converter import process_epub

def main():
    parser = argparse.ArgumentParser(
        description="Convert an EPUB file to an MDBook format (Markdown files + book.toml)."
    )
    parser.add_argument(
        "input",
        help="Path to the input EPUB file."
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Directory to store the output files (default: output)."
    )
    parser.add_argument(
        "--heading_style",
        default="ATX",
        choices=["ATX", "ATX_CLOSED", "SETEXT", "UNDERLINED"],
        help="Heading style for Markdown conversion (default: ATX)."
    )

    args = parser.parse_args()

    try:
        metadata, num_chapters = process_epub(args.input, args.output, args.heading_style)
        print(f"Conversion complete!")
        print(f"Title: {metadata['title']}")
        print(f"Authors: {', '.join(metadata['authors'])}")
        print(f"Chapters processed: {num_chapters}")
        print(f"Output stored in: {args.output}")
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
