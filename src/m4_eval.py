"""RAGAS 0.1.x adapter with explicit evaluator model provenance.

This function performs real network evaluation when called by the live runner.
There are no canned scores, ground-truth answers, or NaN substitutions.
"""
from __future__ import annotations

import math
import os
from copy import deepcopy
from types import SimpleNamespace


def evaluate_ragas(questions, answers, contexts, ground_truths) -> dict:
    size = len(questions)
    if not size or any(len(values) != size for values in (answers, contexts, ground_truths)):
        raise ValueError('Evaluation requires four non-empty lists of equal length.')
    if any(not isinstance(row, list) or any(not isinstance(c, str) for c in row) for row in contexts):
        raise ValueError('contexts must be list[list[str]].')
    from datasets import Dataset
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ragas import evaluate
    from ragas.run_config import RunConfig
    from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

    evaluator_model = os.getenv('RAGAS_LLM_MODEL', 'gpt-4o-mini').strip()
    embedding_model = os.getenv('RAGAS_EMBEDDING_MODEL', 'text-embedding-3-small').strip()
    if not evaluator_model or not embedding_model:
        raise ValueError('Evaluator model identifiers must be non-empty.')
    llm = ChatOpenAI(model=evaluator_model, temperature=0)
    embeddings = OpenAIEmbeddings(model=embedding_model)
    metric_names = ('faithfulness', 'answer_relevancy', 'context_precision', 'context_recall')
    metrics = [deepcopy(metric) for metric in
               (faithfulness, answer_relevancy, context_precision, context_recall)]
    dataset = Dataset.from_dict({'question': questions, 'answer': answers,
                                 'contexts': contexts, 'ground_truth': ground_truths})
    workers = int(os.getenv('RAGAS_MAX_WORKERS', '4'))
    if workers < 1:
        raise ValueError('RAGAS_MAX_WORKERS must be a positive integer.')
    result = evaluate(dataset, metrics=metrics, llm=llm, embeddings=embeddings,
                      run_config=RunConfig(max_workers=workers), raise_exceptions=True)
    rows = list(result.scores)
    if len(rows) != size:
        raise ValueError('RAGAS returned an unexpected number of rows.')
    per_question = []
    for index, row in enumerate(rows):
        values = {}
        for name in metric_names:
            value = float(row[name])
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f'RAGAS row {index + 1}: invalid {name}.')
            values[name] = value
        per_question.append(SimpleNamespace(**values))
    return {'per_question': per_question, 'metadata': {
        'evaluator_models': sorted({evaluator_model, embedding_model})}}
