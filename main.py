import sys
import subprocess
from epub_parser.converter import EpubConverter

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <input.epub> [output_dir]")
        sys.exit(1)

    epub_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output/"

    converter = EpubConverter(epub_path, output_dir)
    converter.convert_to_md()
    print(f"mdBook project created at {output_dir}")

    # Build the mdBook project.
    subprocess.run(["mdbook", "build"], cwd=output_dir, check=True)
    print("mdBook project built.")

    # Serve the mdBook project.
    subprocess.run(["mdbook", "serve"], cwd=output_dir, check=True)