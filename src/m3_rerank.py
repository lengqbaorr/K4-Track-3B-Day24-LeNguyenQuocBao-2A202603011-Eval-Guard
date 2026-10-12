"""CPU multilingual FlashRank ONNX reranking, preserving source metadata.

The ms-marco-MultiBERT-L-12 quantized model uses a 512-token query/passage limit.
It replaces the larger BGE reranker for this CPU-constrained experiment.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path


RERANKER_MODEL = 'ms-marco-MultiBERT-L-12'
RERANKER_CACHE_DIR = Path.home() / '.cache' / 'eval-guard' / 'flashrank'


@dataclass
class RerankResult:
    text: str
    score: float
    metadata: dict


class CrossEncoderReranker:
    def __init__(self):
        from flashrank import Ranker
        self.model = Ranker(model_name=RERANKER_MODEL, cache_dir=str(RERANKER_CACHE_DIR),
                            max_length=512)

    def rerank(self, question: str, docs: list[dict], top_k: int = 3) -> list[RerankResult]:
        if not docs:
            return []
        if type(top_k) is not int or top_k < 1:
            raise ValueError('top_k must be a positive integer.')
        from flashrank import RerankRequest
        if not isinstance(question, str) or not question.strip():
            raise ValueError('Reranker question must be non-empty.')
        passages = [{'id': index, 'text': doc['text']} for index, doc in enumerate(docs)]
        ranked = self.model.rerank(RerankRequest(query=question, passages=passages))
        if len(ranked) != len(docs):
            raise ValueError('FlashRank must return one row per document.')
        values = {}
        for row in ranked:
            index = row.get('id')
            if type(index) is not int or not 0 <= index < len(docs) or index in values:
                raise ValueError('FlashRank returned invalid or duplicate document IDs.')
            if row.get('text') != docs[index]['text']:
                raise ValueError('FlashRank changed source document text.')
            score = row.get('score')
            if isinstance(score, (bool, str, bytes)) or score is None:
                raise ValueError('FlashRank returned a non-numeric score.')
            score = float(score)
            if not math.isfinite(score):
                raise ValueError('FlashRank returned a non-finite score.')
            values[index] = score
        order = sorted(values, key=lambda index: (-values[index], index))[:top_k]
        return [RerankResult(docs[index]['text'], values[index], dict(docs[index]['metadata']))
                for index in order]
