"""Structural enrichment from corpus metadata; does not generate policy facts."""
from dataclasses import dataclass


@dataclass
class EnrichedChunk:
    enriched_text: str
    auto_metadata: dict


def enrich_chunks(chunks: list[dict]) -> list[EnrichedChunk]:
    enriched = []
    for chunk in chunks:
        metadata = dict(chunk['metadata'])
        header = ' | '.join(f'{field}: {metadata[field]}'
                            for field in ('title', 'version', 'effective_date', 'status')
                            if metadata.get(field))
        enriched.append(EnrichedChunk(
            (header + '\n\n' + chunk['text']) if header else chunk['text'],
            {'enrichment_method': 'corpus_metadata'}))
    return enriched
