import os
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

def parse_container(extracted_dir):
    container_path = os.path.join(extracted_dir, 'META-INF', 'container.xml')
    tree = ET.parse(container_path)
    rootfile = tree.find('.//{*}rootfile')
    return unquote(rootfile.attrib['full-path'])

def ensure_directory(path):
    Path(path).mkdir(parents=True, exist_ok=True)