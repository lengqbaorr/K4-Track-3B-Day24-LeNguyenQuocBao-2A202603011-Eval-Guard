# Bài thực hiện solo K4 Track 3B

Người thực hiện: **Lê Nguyễn Quốc Bảo — 2A202603011**. Hình thức solo theo yêu cầu người thực hiện; coach chấp nhận hình thức này chưa được xác nhận trong phiên làm việc.
Repo bài làm: [K4-Track-3B-Day24-LeNguyenQuocBao-2A202603011-Eval-Guard](https://github.com/lengqbaorr/K4-Track-3B-Day24-LeNguyenQuocBao-2A202603011-Eval-Guard). Branch nộp: `main`; tên repo đang dùng theo remote người thực hiện, khác mẫu tên nhóm trong SUBMISSION. Phiên bản kỹ thuật sẽ được chốt bằng commit sau kiểm tra cuối.
Ngày lab và deadline cần đối chiếu thông báo coach: README ghi 11:59 AM ngày 13/10/2026, còn ASSIGNMENT/RULES/SUBMISSION ghi 23:59 ngày lab, UTC+07:00. Không suy ra ngày lab từ thời gian máy.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Công việc | Bằng chứng |
|---|---|---|---|---|
| 1 | Lê Nguyễn Quốc Bảo | 2A202603011 | Phụ trách Tasks 1–13, pipeline, tích hợp và nộp bài; AI hỗ trợ triển khai, chạy và viết báo cáo theo yêu cầu | m1–m5, ba module phase, bốn artifacts và ba báo cáo của lượt hiện tại |

## Môi trường và cấu hình

Chạy trên WSL2/Linux 6.18.33.2-microsoft-standard-WSL2, Python 3.11.13, g++ 15.2.0. Workspace nằm trên `/mnt/c`; interpreter thực chạy là `/home/lnqbao/.cache/eval-guard-runtime/bin/python` trên filesystem Linux để giảm thời gian I/O. RAM khoảng 7.6 GiB, swap 2 GiB, không có NVIDIA GPU khả dụng.
Người thực hiện đã cài requirements. Runtime giữ các pins lõi: RAGAS 0.1.22, NeMo 0.10.0, NumPy 1.26.4, OpenAI SDK 1.109.1. PyArrow 26 từng import lỗi với NumPy nên sửa về 17.0.0; spaCy en_core_web_lg 3.8.0 đã cache. Khi xóa kết quả cũ, dependencies và model caches được giữ lại, không cài lại toàn bộ requirements.
Qdrant v1.9.7 chạy qua Docker Desktop Windows executable, dùng collection riêng `lab24_production`; 25 Markdown được chia thành 115 child chunks. Embedding CPU dùng BGE-M3 ONNX INT8 từ Xenova, revision `4de13258303883538bd53b696b452bf8099f0858`, dimension 1024, tối đa 512 tokens, batch 8. Reranker là FlashRank `ms-marco-MultiBERT-L-12`, tối đa 512 tokens; không khai đã chạy FP32/full-length hoặc BGE-reranker-v2-m3.

LLM trở lại template: generation, judge và NeMo main dùng `gpt-4o-mini`; `config.py` khớp nguyên văn HEAD của starter. Evaluator m4 mặc định và environment cũng dùng mini. Embedding m4/NeMo auxiliary là `text-embedding-3-small`, được khai riêng vì không phải LLM. Guard policy và implementation bài làm được giữ khi khôi phục model defaults. Key người thực hiện vẫn nằm trong `.env`, bị Git ignore, không in hoặc đưa vào bộ nộp.

## Thực nghiệm hiện tại

Theo yêu cầu, artifacts, báo cáo và log của các lượt trước đã xóa. Setup và A/B/C được chạy mới; không lấy lại số liệu cũ. API generation trả snapshot `gpt-4o-mini-2024-07-18`: 50 answers đều LLM, không fallback; 27/50 answers đúng chuỗi “Không tìm thấy.”.

| Checkpoint | Kết quả | Bằng chứng |
|---|---|---|
| CP0 | 50 answers: 20 factual / 20 multi_hop / 10 adversarial; 50 LLM, 0 fallback | [answers_50q.json](../artifacts/answers_50q.json) |
| CP1 | 50 × 4 metrics, bottom 10, matrix; global avg 0.434770 | [failure_clusters](reports/failure_clusters.md) |
| CP2 | 5 pairs, 10 calibration judgments; κ=1.000000 | [bias_report](reports/bias_report.md) |
| CP3 | 20/20 attacks, 8/8 clean, 4/4 outputs; input P95=923.559508 ms | [blueprint](reports/blueprint.md) |

Task 12 có 20 timed samples và 2 warm-ups, scope `input_layers_sequential`. Full RAG/output/request latency chưa đo; endpoint, CI/CD và monitoring là đề xuất. Quality RAG chưa đạt gates CI đề xuất và input P95 vượt mục tiêu 500 ms; kết quả được giữ trung thực.
Bộ nộp giữ đúng bốn artifacts và ba báo cáo theo SUBMISSION. File usage/log/checklist bổ sung đã dọn theo yêu cầu; kết quả kiểm tra cuối được ghi trực tiếp tại đây. Kiểm tra cuối sau khi dọn: **86 tests passed, 3 integration deselected, 0 failed checks**, chạy `python scripts/check_lab.py --with-tests`. Bộ tests starter được giữ; file test adapter bổ sung (4 tests) ngoài danh sách nộp đã xóa, nên số tests cuối là86 thay vì90.

## INDIVIDUAL

### LeNguyenQuocBao-2A202603011

- Phần được giao: toàn bộ Tasks 1–13, pipeline, tích hợp, thực nghiệm và báo cáo cho bài solo. Người thực hiện cung cấp danh tính, cài requirements, điền key và yêu cầu khôi phục model. Codex hỗ trợ triển khai, chạy và viết báo cáo; không khai mọi thao tác là tự viết tay.
- Nguồn: starter, corpus, fixtures, tests, schemas và PIPELINE_INTERFACE. m1–m5 viết mới theo giao diện, không khai là mã đã chạy ở bài trước. Cấu hình inference CPU được ghi rõ trong báo cáo.
- AI hỗ trợ: Orchestration phân công Plan, Code A/B, Code Guard và Review subagents; root chạy API tập trung và đối chiếu JSON. Khi subagents đạt hạn mức phiên, root tiếp tục tích hợp và hoàn thiện báo cáo. Không tự điền metric, không sửa human labels hoặc lấy ground truth thay pipeline answer.
- Kiểm chứng: imports, model và Qdrant thật; setup và runners A/B/C live; schema, metadata và source hashes; suite offline và checker cuối được ghi trong TEAM. Tests mock không chứng minh API đã chạy; bốn artifacts live giữ model IDs và metadata theo hợp đồng.
- Các điểm cần tự giải thích: faithfulness theo contexts có thể vẫn sai policy hiện hành; swap phải ánh xạ winner/scores về A/B gốc; κ dùng supplied answers; longer-winner rate chỉ mô tả; P95 tổng tính từ tổng từng sample. Người thực hiện cần đọc và tự trình bày các kết luận này trước khi nộp.
- Giới hạn: bộ 50/20/8/4 nhỏ, inference CPU có lượng tử hóa/truncation, RAG coverage và abstentions, input latency ngoài budget. Tests/checker pass không phải điểm rubric hoặc chứng nhận production; các gates chưa đạt được ghi trong blueprint.

## Nộp bài và cập nhật

Bộ nộp local đã chuẩn bị để commit/push lên origin/main theo yêu cầu người thực hiện. Gửi link/SHA qua kênh coach là bước riêng, chưa thực hiện trong phiên này; deadline vẫn cần thông báo coach. Phiên bản commit được cập nhật sau khi chốt kỹ thuật.
