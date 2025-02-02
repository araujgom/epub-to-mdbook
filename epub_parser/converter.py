import os
import shutil
import zipfile
from html import unescape
import xml.etree.ElementTree as ET
from urllib.parse import unquote

from bs4 import BeautifulSoup
from markdownify import markdownify as md
from slugify import slugify

from .utils import ensure_directory, parse_container

class EpubConverter:
    def __init__(self, epub_path, output_dir):
        self.epub_path = epub_path
        self.output_dir = output_dir
        self.temp_dir = os.path.join(output_dir, 'temp')
        self.assets_dir = os.path.join(output_dir, 'src', 'assets')
        self.md_dir = os.path.join(output_dir, 'src')
        self.toc = []

        ensure_directory(self.temp_dir)
        ensure_directory(self.assets_dir)
        ensure_directory(self.md_dir)

    def _extract_epub(self):
        with zipfile.ZipFile(self.epub_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)

    def _parse_opf(self):
        opf_path = parse_container(self.temp_dir)
        self.opf_dir = os.path.dirname(os.path.join(self.temp_dir, opf_path))

        tree = ET.parse(os.path.join(self.temp_dir, opf_path))
        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }

        self.title = "Untitled Book"
        self.author = "Unknown Author"
        self.manifest = {}
        self.spine_order = []

        metadata = tree.find('.//opf:metadata', ns)
        if metadata is not None:
            title_elem = metadata.find('dc:title', ns) or metadata.find('opf:title', ns)
            if title_elem is not None and title_elem.text:
                self.title = title_elem.text.strip()
            creator_elem = metadata.find('dc:creator', ns) or metadata.find('opf:creator', ns)
            if creator_elem is not None and creator_elem.text:
                self.author = creator_elem.text.strip()

        manifest = tree.find('.//opf:manifest', ns)
        if manifest is not None:
            for item in manifest.findall('opf:item', ns):
                self.manifest[item.attrib['id']] = {
                    'href': unquote(item.attrib['href']),
                    'media_type': item.attrib['media-type']
                }

        spine = tree.find('.//opf:spine', ns)
        if spine is not None:
            self.spine_order = [
                itemref.attrib['idref']
                for itemref in spine.findall('opf:itemref', ns)
                if 'idref' in itemref.attrib
            ]

    def _process_images(self, soup, xhtml_path):
        for img in soup.find_all('img'):
            src = img['src']
            abs_path = os.path.normpath(os.path.join(
                os.path.dirname(xhtml_path),
                unquote(src)
            ))
            if os.path.exists(abs_path):
                rel_path = os.path.relpath(abs_path, self.temp_dir)
                target_dir = os.path.join(self.assets_dir, os.path.dirname(rel_path))
                ensure_directory(target_dir)
                shutil.copy(abs_path, os.path.join(target_dir, os.path.basename(rel_path)))
                img['src'] = os.path.join('assets', rel_path)

    def convert_to_md(self):
        self._extract_epub()
        self._parse_opf()

        for item_id in self.spine_order:
            item = self.manifest[item_id]
            if item['media_type'] != 'application/xhtml+xml':
                continue

            xhtml_path = os.path.join(self.opf_dir, item['href'])
            with open(xhtml_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            self._process_images(soup, xhtml_path)

            md_content = md(str(soup), heading_style="ATX")
            md_filename = f"{slugify(os.path.basename(item['href']))}.md"
            md_path = os.path.join(self.md_dir, md_filename)

            with open(md_path, 'w', encoding='utf-8') as f:
                if soup.title and soup.title.string:
                    f.write(f"# {soup.title.string}\n\n")
                f.write(md_content)

            self.toc.append({
                'title': soup.title.string if (soup.title and soup.title.string) else md_filename,
                'path': md_filename
            })

        self._generate_summary()
        self._create_book_toml()
        shutil.rmtree(self.temp_dir)

    def _generate_summary(self):
        summary = "# Summary\n\n"
        for entry in self.toc:
            summary += f"* [{entry['title']}]({entry['path']})\n"
        with open(os.path.join(self.md_dir, 'SUMMARY.md'), 'w') as f:
            f.write(summary)

    def _create_book_toml(self):
        toml_content = f"""[book]
title = "{self.title}"
authors = ["{self.author}"]
"""
        with open(os.path.join(self.output_dir, 'book.toml'), 'w') as f:
            f.write(toml_content)
