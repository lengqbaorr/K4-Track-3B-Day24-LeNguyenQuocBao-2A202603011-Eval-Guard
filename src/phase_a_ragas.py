from __future__ import annotations

"""Phase A: RAGAS Production Evaluation — 50q, 3 distributions, cluster analysis."""

import json
import math
import os
import sys
from collections.abc import Mapping
from dataclasses import asdict, dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH, ANSWERS_PATH, ARTIFACTS_DIR
from src.experiment_support import write_json

Distribution = str  # "factual" | "multi_hop" | "adversarial"

DIAGNOSTIC_TREE = {
    "faithfulness":      ("LLM hallucinating", "Tighten system prompt, lower temperature"),
    "context_recall":    ("Missing relevant chunks", "Improve chunking or add BM25"),
    "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
    "answer_relevancy":  ("Answer doesn't match question", "Improve prompt template"),
}


@dataclass
class RagasResult:
    question_id: int
    distribution: Distribution
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

    @property
    def avg_score(self) -> float:
        return (self.faithfulness + self.answer_relevancy +
                self.context_precision + self.context_recall) / 4

    @property
    def worst_metric(self) -> str:
        scores = {
            "faithfulness":      self.faithfulness,
            "answer_relevancy":  self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall":    self.context_recall,
        }
        return min(scores, key=scores.get)


# ─── Đã implement sẵn ────────────────────────────────────────────────────────

@dataclass
class RagasEvaluation:
    """Task 2 output: measured rows plus model identifiers reported by m4."""
    results: list[RagasResult]
    evaluator_models: list[str]

def load_test_set_50q(path: str = TEST_SET_PATH) -> list[dict]:
    """Load 50q test set với 3 distributions."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_answers(path: str = ANSWERS_PATH) -> list[dict]:
    """Load pre-generated answers từ setup_answers.py."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"answers_50q.json không tìm thấy tại {path}\n"
            "→ Chạy trước: python scripts/setup_answers.py --live"
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict]) -> dict:
    """Provided exporter: preserve the student-produced Task 3 rows verbatim."""
    per_dist: dict[str, dict] = {}
    for dist in ["factual", "multi_hop", "adversarial"]:
        subset = [r for r in results if r.distribution == dist]
        if subset:
            per_dist[dist] = {
                "count": len(subset),
                "faithfulness":      sum(r.faithfulness for r in subset) / len(subset),
                "answer_relevancy":  sum(r.answer_relevancy for r in subset) / len(subset),
                "context_precision": sum(r.context_precision for r in subset) / len(subset),
                "context_recall":    sum(r.context_recall for r in subset) / len(subset),
                "avg_score":         sum(r.avg_score for r in subset) / len(subset),
            }

    report = {
        "total_questions": len(results),
        "per_question": [asdict(r) for r in results],
        "per_distribution": per_dist,
        "failure_clusters": clusters,
        "bottom_10": bottom,
    }
    return report


def save_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict],
                        path: str = os.path.join(ARTIFACTS_DIR, "ragas_50q.json")) -> None:
    write_json(path, build_phase_a_report(results, clusters, bottom))



# ─── Tasks 1-4: Sinh viên implement ──────────────────────────────────────────

def group_by_distribution(test_set: list[dict]) -> dict[str, list[dict]]:
    """Task 1: Nhóm 50 câu hỏi theo 3 distributions.

    Returns:
        {"factual": [...], "multi_hop": [...], "adversarial": [...]}
    """
    groups = {"factual": [], "multi_hop": [], "adversarial": []}
    for item in test_set:
        distribution = item["distribution"]
        if distribution not in groups:
            raise ValueError(f"Unknown distribution: {distribution!r}")
        groups[distribution].append(item)
    return groups


def run_ragas_50q(answers: list[dict]) -> RagasEvaluation:
    """Task 2: Chạy RAGAS 4 metrics trên toàn bộ 50 câu hỏi.

    Gợi ý — import từ Day 18 của bạn:
        from src.m4_eval import evaluate_ragas

    Steps:
        1. Extract questions, answers, contexts, ground_truths từ answers list
        2. Gọi evaluate_ragas() từ m4_eval.py
        3. Kết hợp kết quả với distribution info từ answers list
        4. Return RagasEvaluation(results, raw["metadata"]["evaluator_models"])
           m4 must report its actual LLM/embedding models; never guess JUDGE_MODEL.
    """
    if not answers:
        raise ValueError("RAGAS evaluation requires at least one answer.")
    group_by_distribution(answers)
    if len({a["id"] for a in answers}) != len(answers):
        raise ValueError("Duplicate answer IDs would make evaluation ambiguous.")
    try:
        from src.m4_eval import evaluate_ragas
    except ImportError as exc:
        raise ImportError("Install the evaluator dependencies and provide src/m4_eval.py.") from exc

    raw = evaluate_ragas(
        [a["question"] for a in answers], [a["answer"] for a in answers],
        [a["contexts"] for a in answers], [a["ground_truth"] for a in answers],
    )
    if not isinstance(raw, Mapping):
        raise ValueError("m4 must return a mapping with per_question and metadata.")
    per_question = raw.get("per_question")
    if not isinstance(per_question, (list, tuple)) or len(per_question) != len(answers):
        raise ValueError("m4 must return one metric row per answer, in input order.")
    metadata = raw.get("metadata")
    models = metadata.get("evaluator_models") if isinstance(metadata, Mapping) else None
    if (not isinstance(models, list) or not models
            or any(not isinstance(model, str) or not model.strip() for model in models)):
        raise ValueError("m4 must report its actual evaluator_models; no model fallback is allowed.")

    results = []
    for answer, row in zip(answers, per_question):
        scores = {}
        for metric in ("faithfulness", "answer_relevancy", "context_precision", "context_recall"):
            value = row.get(metric) if isinstance(row, Mapping) else getattr(row, metric, None)
            if isinstance(value, (bool, str, bytes)) or value is None:
                raise ValueError(f"Question {answer['id']}: invalid {metric}: {value!r}")
            try:
                score = float(value)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"Question {answer['id']}: non-numeric {metric}.") from exc
            if not math.isfinite(score) or not 0 <= score <= 1:
                raise ValueError(f"Question {answer['id']}: {metric} must be finite in [0, 1].")
            scores[metric] = score
        results.append(RagasResult(
            question_id=answer["id"], distribution=answer["distribution"],
            question=answer["question"], answer=answer["answer"],
            contexts=answer["contexts"], ground_truth=answer["ground_truth"], **scores,
        ))
    return RagasEvaluation(results, list(models))


def bottom_10(results: list[RagasResult]) -> list[dict]:
    """Task 3: Lấy 10 câu hỏi có avg_score thấp nhất.

    Returns:
        [{"rank": 1, "question_id": ..., "distribution": ...,
          "question": ..., "avg_score": ..., "worst_metric": ...,
          "diagnosis": ..., "suggested_fix": ...}, ...]
    """
    output = []
    for rank, result in enumerate(sorted(results, key=lambda r: r.avg_score)[:10], 1):
        metric = result.worst_metric
        diagnosis, fix = DIAGNOSTIC_TREE[metric]
        output.append({
            "rank": rank, "question_id": result.question_id,
            "distribution": result.distribution, "question": result.question,
            "avg_score": result.avg_score, "worst_metric": metric,
            "diagnosis": (
                f"Q{result.question_id} ({result.distribution}): {metric}="
                f"{getattr(result, metric):.4f}, avg={result.avg_score:.4f}; "
                f"{len(result.contexts)} retrieved contexts. Hypothesis: {diagnosis}. "
                "Verify against this answer, retrieved contexts and ground truth before attributing cause."
            ),
            "suggested_fix": f"{fix}; inspect retrieval and policy-version evidence for Q{result.question_id}.",
        })
    return output


def cluster_analysis(results: list[RagasResult]) -> dict:
    """Task 4: Phân tích failure clusters theo (worst_metric × distribution).

    Matrix thống kê worst_metric của mọi câu, không coi mọi câu là một failure.
    Nhóm yếu nhất = distribution có avg_score trung bình thấp nhất (bỏ nhóm rỗng).
    Tổng matrix theo cột chỉ là kích thước nhóm 20/20/10, không đo chất lượng.

    Returns:
        {
          "matrix": {
            "faithfulness":      {"factual": 3, "multi_hop": 5, "adversarial": 2},
            "answer_relevancy":  {...},
            "context_precision": {...},
            "context_recall":    {...},
          },
          "dominant_failure_distribution": "multi_hop",
          "dominant_failure_metric": "context_recall",
          "insight": "..."
        }
    """
    distributions = ("factual", "multi_hop", "adversarial")
    matrix = {metric: {dist: 0 for dist in distributions} for metric in DIAGNOSTIC_TREE}
    grouped = {dist: [] for dist in distributions}
    for result in results:
        if result.distribution not in grouped:
            raise ValueError(f"Unknown distribution: {result.distribution!r}")
        matrix[result.worst_metric][result.distribution] += 1
        grouped[result.distribution].append(result.avg_score)
    means = {dist: sum(scores) / len(scores) for dist, scores in grouped.items() if scores}
    if not means:
        return {"matrix": matrix, "distribution_avg_scores": {},
                "dominant_failure_distribution": None, "dominant_failure_metric": None,
                "insight": "Chưa có kết quả đo; chưa thể xác định nhóm yếu hoặc metric chủ đạo."}
    dominant_dist = min(means, key=means.get)
    dominant_metric = max(matrix, key=lambda metric: sum(matrix[metric].values()))
    return {
        "matrix": matrix, "distribution_avg_scores": means,
        "dominant_failure_distribution": dominant_dist,
        "dominant_failure_metric": dominant_metric,
        "insight": (
            f"Distribution '{dominant_dist}' có điểm trung bình thấp nhất ({means[dominant_dist]:.4f}). "
            f"Metric '{dominant_metric}' là metric thấp nhất thường gặp nhất "
            f"({sum(matrix[dominant_metric].values())}/{len(results)} câu). "
            "Matrix đếm metric thấp nhất của mọi câu, kể cả câu điểm cao; không phải số failures. "
            f"Gợi ý cần kiểm chứng: {DIAGNOSTIC_TREE[dominant_metric][1]}."
        ),
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from scripts.run_experiments import main
    raise SystemExit(main(["--phase", "a", *sys.argv[1:]]))
