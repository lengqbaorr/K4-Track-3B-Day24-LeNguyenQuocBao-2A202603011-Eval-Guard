"""BM25 + BGE-M3/Qdrant retrieval fused by reciprocal ranks.

Libraries/models are loaded on construction/indexing, never at module import.
Indexing replaces points only in the configured lab collection.
"""
from __future__ import annotations

import re
import os
from dataclasses import dataclass
from uuid import NAMESPACE_URL, uuid5

from config import (BM25_TOP_K, COLLECTION_NAME, DENSE_TOP_K, EMBEDDING_DIM,
                    EMBEDDING_MODEL, HYBRID_TOP_K, QDRANT_HOST, QDRANT_PORT)


@dataclass
class SearchResult:
    text: str
    score: float
    metadata: dict


def _tokens(text: str) -> list[str]:
    return re.findall(r'\w+', text.casefold(), flags=re.UNICODE)


ONNX_EMBEDDING_REPO = 'Xenova/bge-m3'
ONNX_EMBEDDING_REVISION = '4de13258303883538bd53b696b452bf8099f0858'
ONNX_EMBEDDING_FILE = 'onnx/sentence_transformers_quantized.onnx'


class BgeM3OnnxEncoder:
    """Pinned int8 conversion of BGE-M3, with CPU-only dense embeddings.

    Small padded batches and a 512-token limit bound CPU RAM use. This differs
    from full-length FP32 inference and must be recorded in experiment reports.
    """

    def __init__(self):
        import onnxruntime as ort
        from huggingface_hub import hf_hub_download
        from transformers import AutoTokenizer

        if EMBEDDING_MODEL != 'BAAI/bge-m3' or EMBEDDING_DIM != 1024:
            raise ValueError('The pinned ONNX adapter requires BGE-M3 with dimension 1024.')
        path = hf_hub_download(repo_id=ONNX_EMBEDDING_REPO, filename=ONNX_EMBEDDING_FILE,
                               revision=ONNX_EMBEDDING_REVISION)
        self.tokenizer = AutoTokenizer.from_pretrained(
            ONNX_EMBEDDING_REPO, revision=ONNX_EMBEDDING_REVISION, trust_remote_code=False)
        options = ort.SessionOptions()
        options.intra_op_num_threads = min(4, os.cpu_count() or 1)
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(path, sess_options=options,
                                           providers=['CPUExecutionProvider'])
        if 'sentence_embedding' not in {node.name for node in self.session.get_outputs()}:
            raise ValueError('ONNX graph must expose the sentence_embedding output.')

    def encode(self, texts, normalize_embeddings=True, show_progress_bar=False, batch_size=8):
        import numpy as np

        single = isinstance(texts, str)
        values = [texts] if single else list(texts)
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError('Embedding inputs must be non-empty strings.')
        if type(batch_size) is not int or batch_size < 1:
            raise ValueError('Embedding batch_size must be a positive integer.')
        if not values:
            return np.empty((0, EMBEDDING_DIM), dtype=np.float32)
        arrays = []
        input_dtypes = {'tensor(int64)': np.int64, 'tensor(int32)': np.int32}
        for start in range(0, len(values), batch_size):
            tokens = self.tokenizer(values[start:start + batch_size], padding=True,
                                    truncation=True, max_length=512, return_tensors='np')
            feed = {}
            for node in self.session.get_inputs():
                if node.type not in input_dtypes:
                    raise ValueError(f'Unsupported ONNX input dtype: {node.type}')
                value = tokens.get(node.name)
                if value is None and node.name == 'token_type_ids':
                    value = np.zeros_like(tokens['input_ids'])
                if value is None:
                    raise ValueError(f'Tokenizer did not provide ONNX input {node.name}.')
                feed[node.name] = np.asarray(value, dtype=input_dtypes[node.type])
            embeddings = np.asarray(self.session.run(['sentence_embedding'], feed)[0],
                                    dtype=np.float32)
            expected = (min(batch_size, len(values) - start), EMBEDDING_DIM)
            if embeddings.shape != expected or not np.isfinite(embeddings).all():
                raise ValueError('ONNX sentence embeddings have invalid shape or non-finite values.')
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            if not np.isfinite(norms).all() or (norms <= 0).any():
                raise ValueError('ONNX sentence embeddings have zero/invalid norms.')
            if normalize_embeddings:
                embeddings = embeddings / norms
            arrays.append(embeddings)
        output = np.concatenate(arrays, axis=0)
        return output[0] if single else output


class HybridSearch:
    def __init__(self):
        self._chunks = []
        self._bm25 = self._encoder = self._client = None

    def index(self, chunks: list[dict]):
        if not chunks or any(not c.get('text', '').strip() for c in chunks):
            raise ValueError('Cannot index an empty corpus or empty chunks.')
        from rank_bm25 import BM25Okapi
        from qdrant_client import QdrantClient, models

        self._chunks = [{'text': c['text'], 'metadata': dict(c['metadata'])} for c in chunks]
        self._bm25 = BM25Okapi([_tokens(c['text']) for c in self._chunks])
        self._encoder = BgeM3OnnxEncoder()
        vectors = self._encoder.encode([c['text'] for c in self._chunks],
                                       normalize_embeddings=True, show_progress_bar=True)
        if vectors.shape[1] != EMBEDDING_DIM:
            raise ValueError('Embedding dimension differs from configured Qdrant dimension.')
        self._client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=60)
        # Reuse the configured lab collection, clearing stale points from prior runs.
        names = {collection.name for collection in self._client.get_collections().collections}
        if COLLECTION_NAME in names:
            self._client.delete_collection(collection_name=COLLECTION_NAME)
        self._client.create_collection(collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=EMBEDDING_DIM, distance=models.Distance.COSINE))
        for start in range(0, len(self._chunks), 64):
            points = [models.PointStruct(
                id=str(uuid5(NAMESPACE_URL, f'{COLLECTION_NAME}:{i}')),
                vector=vectors[i].tolist(), payload={'chunk_index': i, **self._chunks[i]})
                for i in range(start, min(start + 64, len(self._chunks)))]
            self._client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)

    def search(self, question: str) -> list[SearchResult]:
        if self._bm25 is None or self._client is None:
            raise RuntimeError('Call index() before search().')
        if not question.strip():
            raise ValueError('Question must be non-empty.')
        bm25_scores = self._bm25.get_scores(_tokens(question))
        lexical = sorted(range(len(self._chunks)), key=lambda i: (-float(bm25_scores[i]), i))
        lexical = [i for i in lexical[:BM25_TOP_K] if bm25_scores[i] > 0]
        vector = self._encoder.encode(question, normalize_embeddings=True).tolist()
        hits = self._client.search(collection_name=COLLECTION_NAME, query_vector=vector,
                                   limit=DENSE_TOP_K, with_payload=True)
        dense = [int(hit.payload['chunk_index']) for hit in hits]
        fused = {}
        for ranking in (lexical, dense):
            for rank, index in enumerate(ranking, 1):
                fused[index] = fused.get(index, 0.0) + 1.0 / (60 + rank)
        results, seen_parents = [], set()
        for index in sorted(fused, key=lambda i: (-fused[i], i)):
            chunk = self._chunks[index]
            metadata = dict(chunk['metadata'])
            parent = metadata.get('parent_id', f'chunk:{index}')
            if parent in seen_parents:
                continue
            seen_parents.add(parent)
            # Return the retrieved child's parent, preserving policy conditions.
            context = metadata.get('parent_text', chunk['text'])
            header = ' | '.join(str(metadata[field]) for field in
                                ('title', 'version', 'effective_date', 'status') if metadata.get(field))
            metadata['retrieval_method'] = 'bm25_dense_rrf_parent'
            results.append(SearchResult(header + '\n\n' + context if header else context,
                                        float(fused[index]), metadata))
            if len(results) >= HYBRID_TOP_K:
                break
        return results
