"""Markdown corpus loader and deterministic parent/child chunking.

Local implementation for this lab; no previous-lab source was supplied.
Sizes are character budgets. Children retain their full parent for retrieval.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from config import DATA_DIR, HIERARCHICAL_CHILD_SIZE, HIERARCHICAL_PARENT_SIZE


@dataclass
class Chunk:
    text: str
    metadata: dict
    parent_id: str


def load_documents() -> list[dict]:
    documents = []
    for path in sorted(Path(DATA_DIR).rglob('*.md')):
        content = path.read_text(encoding='utf-8').strip()
        if not content:
            raise ValueError(f'Empty corpus document: {path.name}')
        title = next((line.lstrip('# ').strip() for line in content.splitlines()
                      if line.startswith('# ')), path.stem)
        metadata = {'source': path.relative_to(DATA_DIR).as_posix(), 'title': title}
        for field, label in [('version', 'Phiên bản'), ('effective_date', 'Ngày hiệu lực'),
                             ('department', 'Phòng ban'), ('status', 'Trạng thái')]:
            match = re.search(re.escape(label) + r':\s*([^|\n]+)', content)
            if match:
                metadata[field] = match.group(1).strip()
        documents.append({'text': content, 'metadata': metadata})
    if not documents:
        raise ValueError(f'No Markdown corpus found in {DATA_DIR}')
    return documents


def _split(text: str, size: int, overlap: int = 0) -> list[str]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError('Chunk size must be positive and overlap smaller than size.')
    pieces, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind('\n', start + size // 2, end)
            if boundary < 0:
                boundary = text.rfind(' ', start + size // 2, end)
            if boundary > start:
                end = boundary + 1
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return pieces


def chunk_hierarchical(text: str, metadata=None) -> tuple[list[Chunk], list[Chunk]]:
    metadata = dict(metadata or {})
    identity = hashlib.sha256((str(metadata.get('source', '')) + '\n' + text).encode()).hexdigest()
    parents, children = [], []
    for index, parent_text in enumerate(_split(text, HIERARCHICAL_PARENT_SIZE)):
        parent_id = f'{identity}:{index}'
        parent_meta = {**metadata, 'parent_index': index}
        parents.append(Chunk(parent_text, parent_meta, parent_id))
        for child_index, child_text in enumerate(_split(parent_text, HIERARCHICAL_CHILD_SIZE, 40)):
            children.append(Chunk(child_text, {**parent_meta, 'child_index': child_index,
                                               'parent_text': parent_text}, parent_id))
    return parents, children
