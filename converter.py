import os
from ebooklib import epub
from markdownify import markdownify as md

def extract_metadata(book):
    # Extract title and authors using Dublin Core (DC) metadata.
    title_list = book.get_metadata('DC', 'title')
    title = title_list[0][0] if title_list else "Untitled"

    author_list = book.get_metadata('DC', 'creator')
    authors = [a[0] for a in author_list] if author_list else []

    # Optionally, extract cover metadata from the 'OPF' namespace.
    cover_meta = book.get_metadata('OPF', 'cover')
    cover = cover_meta[0][1].get('content') if cover_meta else None

    return {
        'title': title,
        'authors': authors,
        'cover': cover,
    }

def extract_html_documents(book):
    """Iterate over document items (chapters) and return a list of HTML strings."""
    html_docs = []
    # Instead of checking against epub.ITEM_DOCUMENT (which may not exist),
    # we check if the item is an instance of epub.EpubHtml.
    for item in book.get_items():
        if isinstance(item, epub.EpubHtml):
            # get_body_content() returns only the <body> part as bytes.
            try:
                body = item.get_body_content()
                if isinstance(body, bytes):
                    html_content = body.decode('utf-8')
                else:
                    html_content = body
                html_docs.append(html_content)
            except Exception as e:
                # In case of issues, fall back to get_content()
                try:
                    content = item.get_content().decode('utf-8')
                    html_docs.append(content)
                except Exception:
                    pass
    return html_docs

def convert_html_to_markdown(html_docs, heading_style="ATX"):
    """Convert each HTML document to Markdown using markdownify."""
    markdown_docs = []
    for html in html_docs:
        md_text = md(html, heading_style=heading_style)
        markdown_docs.append(md_text)
    return markdown_docs

def write_mdbook(markdown_docs, metadata, output_dir):
    """Write out the markdown chapters and a book.toml configuration file."""
    os.makedirs(output_dir, exist_ok=True)

    # Write each chapter as a separate Markdown file.
    for i, content in enumerate(markdown_docs, start=1):
        chapter_filename = os.path.join(output_dir, f'chapter{i}.md')
        with open(chapter_filename, 'w', encoding='utf-8') as f:
            f.write(content)

    # Create a book.toml file for mdBook.
    authors_str = ", ".join([f'"{author}"' for author in metadata['authors']])
    book_toml = f"""\
[book]
title = "{metadata['title']}"
authors = [{authors_str}]
"""
    config_path = os.path.join(output_dir, 'book.toml')
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(book_toml)

def process_epub(epub_path, output_dir="output", heading_style="ATX"):
    # Read the EPUB file.
    book = epub.read_epub(epub_path)

    # Extract metadata.
    metadata = extract_metadata(book)

    # Extract HTML documents from the EPUB.
    html_docs = extract_html_documents(book)

    if not html_docs:
        raise ValueError("No HTML content found in the EPUB file.")

    # Convert each HTML document to Markdown.
    markdown_docs = convert_html_to_markdown(html_docs, heading_style=heading_style)

    # Write out the markdown files and config file.
    write_mdbook(markdown_docs, metadata, output_dir)

    return metadata, len(markdown_docs)
