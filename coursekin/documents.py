"""Isolated, bounded document extraction. Never fetch links or execute document content."""
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

MAX_TEXT = 8_000_000
MAX_FILE = 30 * 1024 * 1024

def extract(name, raw):
    if len(raw) > MAX_FILE:
        raise ValueError('Each file must be smaller than 30 MB.')
    ext = name.rsplit('.', 1)[-1].lower()
    pages = []
    if ext == 'pdf':
        from pypdf import PdfReader
        from pypdf import filters
        filters.ZLIB_MAX_OUTPUT_LENGTH = 16_000_000
        reader = PdfReader(io.BytesIO(raw), strict=False)
        if reader.is_encrypted:
            raise ValueError('This PDF is password protected. Please upload an unlocked copy.')
        if len(reader.pages) > 2000:
            raise ValueError('Please split PDFs longer than 2,000 pages into smaller volumes.')
        total = 0
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ''
            total += len(text)
            if total > MAX_TEXT:
                raise ValueError('This document contains too much text. Please upload a smaller section.')
            if text.strip():
                pages.append({'location': f'PDF page {i + 1}', 'text': text})
    elif ext == 'docx':
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            entries = z.infolist()
            if len(entries) > 3000 or sum(x.file_size for x in entries) > 60_000_000:
                raise ValueError('This DOCX expands beyond the safe import limit.')
            item = z.getinfo('word/document.xml')
            if item.file_size > 16_000_000:
                raise ValueError('This DOCX is too large to read safely.')
            xml = z.read(item)
            if b'<!DOCTYPE' in xml or b'<!ENTITY' in xml:
                raise ValueError('Unsupported XML declarations in this DOCX.')
            root = ET.fromstring(xml)
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = [''.join(p.itertext()) for p in root.findall('.//w:p', ns)]
            for i in range(0, len(paragraphs), 12):
                pages.append({'location': f'Paragraphs {i + 1} to {min(i + 12, len(paragraphs))}', 'text': '\n'.join(paragraphs[i:i+12])})
    elif ext in ('txt', 'md'):
        text = raw.decode('utf-8-sig')
        lines = text.splitlines()
        for i in range(0, len(lines), 40):
            pages.append({'location': f'Lines {i + 1} to {min(i + 40, len(lines))}', 'text': '\n'.join(lines[i:i+40])})
    else:
        raise ValueError('Please use PDF, DOCX, TXT or Markdown.')
    if sum(len(p['text']) for p in pages) > MAX_TEXT:
        raise ValueError('The extracted text is too large. Upload a smaller section.')
    chunks = []
    for p in pages:
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', p['text']).strip()
        for offset in range(0, len(text), 1400):
            chunk = text[offset:offset+1700].strip()
            if chunk:
                chunks.append({'location': p['location'], 'text': chunk})
    if not chunks:
        raise ValueError('No readable text was found. Scanned PDFs need OCR before importing; please use a searchable PDF or paste the text.')
    return chunks

if __name__ == '__main__':
    # Parent enforces a deadline; a fresh process releases parser memory after every file.
    try:
        from .limits import limit_parser_memory
        limit_parser_memory()
        result = extract(sys.argv[1], sys.stdin.buffer.read(MAX_FILE + 1))
        print(json.dumps({'chunks': result}))
    except Exception as exc:
        msg = str(exc) if isinstance(exc, ValueError) else 'Could not read this file. It may be damaged or use an unsupported format.'
        print(json.dumps({'error': msg}))
