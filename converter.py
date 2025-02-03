import os
import ebooklib
from ebooklib import epub
from markdownify import markdownify as md
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def extract_metadata(book):
    """Extracts title, authors, and (optionally) cover metadata from the EPUB."""
    title_list = book.get_metadata('DC', 'title')
    title = title_list[0][0] if title_list else "Untitled"

    author_list = book.get_metadata('DC', 'creator')
    authors = [a[0] for a in author_list] if author_list else []

    cover_meta = book.get_metadata('OPF', 'cover')
    cover = cover_meta[0][1].get('content') if cover_meta else None

    return {
        'title': title,
        'authors': authors,
        'cover': cover,
    }

def extract_html_documents(book):
    """
    Iterates over the EPUB items and returns a list of tuples:
    (chapter_title, HTML_content, html_path)
    If a chapter's title is missing in the EPUB metadata, None is returned as title.
    """
    chapters = []
    for item in book.get_items():
        if isinstance(item, epub.EpubHtml):
            title = item.title if item.title else None
            try:
                body = item.get_body_content()
                if isinstance(body, bytes):
                    html_content = body.decode('utf-8')
                else:
                    html_content = body
            except Exception:
                try:
                    html_content = item.get_content().decode('utf-8')
                except Exception:
                    continue
            html_path = item.file_name
            chapters.append((title, html_content, html_path))
    return chapters

def extract_and_save_images(book, output_dir):
    """
    Extracts all images from the EPUB and saves them under output_dir/src/images.
    Returns a dictionary mapping original image hrefs to their new filenames.
    """
    images_dir = os.path.join(output_dir, 'src', 'images')
    os.makedirs(images_dir, exist_ok=True)
    image_map = {}
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_IMAGE:
            original_href = item.file_name
            filename = os.path.basename(original_href)
            # Handle duplicate filenames
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(images_dir, filename)):
                filename = f"{base}_{counter}{ext}"
                counter += 1
            # Save the image
            image_path = os.path.join(images_dir, filename)
            with open(image_path, 'wb') as f:
                f.write(item.get_content())
            image_map[original_href] = filename
    return image_map

def replace_image_links(html_content, html_path, image_map):
    """
    Replaces image src attributes in the HTML content with the new paths.
    Uses BeautifulSoup to parse and modify the HTML.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            # Resolve the src relative to the HTML's path
            absolute_src = urljoin(html_path, src)
            new_filename = image_map.get(absolute_src)
            if new_filename:
                img['src'] = f'images/{new_filename}'
    return str(soup)

def convert_html_to_markdown(chapters, heading_style="ATX"):
    """
    Converts each chapter's HTML to Markdown.
    Each chapter is a tuple (title, html_content) and this returns a list of
    tuples (title, markdown_text). If no title exists, the function will try to
    extract the first Markdown heading or default to "Untitled Chapter".
    """
    markdown_chapters = []
    for title, html in chapters:
        md_text = md(html, heading_style=heading_style)
        if not title:
            # Try to extract the first Markdown heading as title
            for line in md_text.splitlines():
                if line.startswith("#"):
                    title = line.lstrip("#").strip()
                    break
            if not title:
                title = "Untitled Chapter"
        markdown_chapters.append((title, md_text))
    return markdown_chapters

def write_mdbook(markdown_chapters, metadata, output_dir):
    """
    Writes out:
      - Each chapter as a separate Markdown file in the `src` subfolder.
      - A book.toml file with the book metadata in the output folder.
      - A SUMMARY.md file in the output folder that lists links to the chapter files.
    """
    # Create output and src directories
    os.makedirs(output_dir, exist_ok=True)
    src_dir = os.path.join(output_dir, 'src')
    os.makedirs(src_dir, exist_ok=True)

    chapter_files = []
    # Write each chapter to its own Markdown file in the src folder.
    for i, (chapter_title, content) in enumerate(markdown_chapters, start=1):
        chapter_filename = f'chapter{i}.md'
        full_path = os.path.join(src_dir, chapter_filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        # Store only the filename since SUMMARY.md is written in the same src folder.
        chapter_files.append((chapter_title, chapter_filename))

    # Create book.toml for mdBook.
    authors_str = ", ".join([f'"{author}"' for author in metadata['authors']])
    book_toml = f"""\
[book]
title = "{metadata['title']}"
authors = [{authors_str}]
"""
    with open(os.path.join(output_dir, 'book.toml'), 'w', encoding='utf-8') as f:
        f.write(book_toml)

    # Create SUMMARY.md file in the src folder with correct relative links.
    summary_lines = ["# Summary", ""]
    for chapter_title, chapter_filename in chapter_files:
        summary_lines.append(f"* [{chapter_title}]({chapter_filename})")
    summary_content = "\n".join(summary_lines)
    with open(os.path.join(src_dir, 'SUMMARY.md'), 'w', encoding='utf-8') as f:
        f.write(summary_content)

def process_epub(epub_path, output_dir="output", heading_style="ATX"):
    """
    Process the EPUB file:
      1. Read the EPUB.
      2. Extract metadata.
      3. Extract HTML chapters.
      4. Extract and save images, updating their references in the HTML.
      5. Convert HTML chapters to Markdown.
      6. Write out the markdown files, book.toml, and SUMMARY.md.
    Returns the metadata and the number of chapters processed.
    """
    book = epub.read_epub(epub_path)
    metadata = extract_metadata(book)
    chapters_with_paths = extract_html_documents(book)

    if not chapters_with_paths:
        raise ValueError("No HTML content found in the EPUB file.")

    # Extract and save images, get the mapping from original paths to new filenames
    image_map = extract_and_save_images(book, output_dir)

    # Process each chapter's HTML to replace image links
    processed_chapters = []
    for title, html_content, html_path in chapters_with_paths:
        modified_html = replace_image_links(html_content, html_path, image_map)
        processed_chapters.append((title, modified_html))

    markdown_chapters = convert_html_to_markdown(processed_chapters, heading_style=heading_style)
    write_mdbook(markdown_chapters, metadata, output_dir)

    return metadata, len(markdown_chapters)