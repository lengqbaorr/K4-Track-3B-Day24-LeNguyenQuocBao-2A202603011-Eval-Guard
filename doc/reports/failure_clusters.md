# Phân tích lỗi Phase A

Nhóm: **LeNguyenQuocBao (solo)**.

Người phụ trách: **Lê Nguyễn Quốc Bảo — MSSV 2A202603011**.

Nguồn: `artifacts/ragas_50q.json`; run timestamp UTC: `2026-10-12T14:51:58.759223+00:00`.

Models của phase từ metadata: `{"generation": ["gpt-4o-mini-2024-07-18"], "evaluator": ["gpt-4o-mini", "text-embedding-3-small"], "judge": [], "guard": []}`.

Lượt live duy nhất được giữ: created_at UTC `2026-10-12T14:51:58.759223+00:00`, format_version=2, run_kind=live. Models theo từng vai trò: `{"generation": ["gpt-4o-mini-2024-07-18"], "evaluator": ["gpt-4o-mini", "text-embedding-3-small"], "judge": [], "guard": []}`. SHA-256 được validation đối chiếu lại với đầu vào:

| Nguồn | SHA-256 |
| --- | --- |
| answers_50q.json | 73513f553b0172499259bf9d0f83f889a7671737c9bbb7fff548c8b5ddac3535 |
| test_set_50q.json | 3ad288426e3066e561737b35b66b671e6c411697dffd0d1161cc7b801e5954cc |

### Điều kiện chạy và pipeline

Corpus và fixtures giữ nguyên, có cả policy cũ/mới. M1 đọc 25 Markdown, hierarchical parent/child budgets 2048/256 ký tự, overlap 40 ký tự; m5 enrichment metadata không sinh facts. M2 BM25 + dense Qdrant/RRF trả parent contexts, m3 rerank top 3, generation chỉ nhận question và contexts; không đưa ground_truth vào prompt generation.

Runtime retrieval thực dùng BGE-M3 ONNX INT8 `Xenova/bge-m3`, revision `4de13258303883538bd53b696b452bf8099f0858`, file `onnx/sentence_transformers_quantized.onnx`, dimension 1024, CPUExecutionProvider, batch 8/max 512 tokens/L2 normalization. Reranker FlashRank multilingual `ms-marco-MultiBERT-L-12`, quantized ONNX CPU, max 512 tokens. Đây là cấu hình CPU của bài làm, không khai là BGE reranker v2-m3 hoặc FP32/full8192-token. Chưa đo đối chứng lượng tử hóa/truncation.

Generation/judge và NeMo main LLM khôi phục **gpt-4o-mini** đúng template starter; `config.py` giữ giá trị LLM mặc định của starter. M4 dùng evaluator **gpt-4o-mini** và embedding **text-embedding-3-small**, RAGAS 0.1.22, 4 workers. NeMo auxiliary embedding `text-embedding-3-small` là cấu hình runtime bổ sung, không phải LLM và không nằm trong latency timed samples. Policy rail và implementation bài làm được giữ; khôi phục model defaults không xóa phần code đã hoàn thiện.

API generation thực trả `gpt-4o-mini-2024-07-18`: **50 LLM answers, 0 fallback**, 27/50 answers đúng chuỗi “Không tìm thấy.”. Đó là output abstention từ LLM, không phải extractive fallback. Adapter m4 gọi RAGAS thật trên 50 × 4 metric; từ chối thiếu rows, NaN/inf và điểm ngoài [0,1], không thay điểm giả. JSON giữ full precision; bảng hiển thị sáu chữ số.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
| --- | --- | --- | --- |
| faithfulness | 0.600000 | 0.191667 | 0.500000 |
| answer_relevancy | 0.305271 | 0.176314 | 0.348906 |
| context_precision | 0.600000 | 0.516667 | 0.650000 |
| context_recall | 0.625000 | 0.400000 | 0.366667 |
| avg_score | 0.532568 | 0.321162 | 0.466393 |

| Metric toàn 50 câu | Mean |
| --- | --- |
| faithfulness | 0.416667 |
| answer_relevancy | 0.262415 |
| context_precision | 0.576667 |
| context_recall | 0.483333 |
| avg_score | 0.434770 |

Global mean tính có trọng số20/20/10, không trung bình ba nhóm không trọng số. Gates CI đề xuất faithfulness≥0.75 và avg_score≥0.65 được phân biệt với yêu cầu lab về thực nghiệm, schema và phân tích; không tự khai đạt điểm rubric.

## Bottom 10 và nguyên nhân

| Rank | ID | Question | Distribution | Avg | Worst | Diagnosis nguyên văn | Suggested fix nguyên văn |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | Nhân viên được nghỉ bao nhiêu ngày khi kết hôn? | factual | 0.000000 | faithfulness | Q1 (factual): faithfulness=0.0000, avg=0.0000; 3 retrieved contexts. Hypothesis: LLM hallucinating. Verify against this answer, retrieved contexts and ground truth before attributing cause. | Tighten system prompt, lower temperature; inspect retrieval and policy-version evidence for Q1. |
| 2 | 8 | Nhân viên được nghỉ bao nhiêu ngày khi cha hoặc mẹ mất? | factual | 0.000000 | faithfulness | Q8 (factual): faithfulness=0.0000, avg=0.0000; 3 retrieved contexts. Hypothesis: LLM hallucinating. Verify against this answer, retrieved contexts and ground truth before attributing cause. | Tighten system prompt, lower temperature; inspect retrieval and policy-version evidence for Q8. |
| 3 | 10 | Nhân viên chính thức được phép làm việc từ xa tối đa bao nhiêu ngày một tuần? | factual | 0.000000 | faithfulness | Q10 (factual): faithfulness=0.0000, avg=0.0000; 3 retrieved contexts. Hypothesis: LLM hallucinating. Verify against this answer, retrieved contexts and ground truth before attributing cause. | Tighten system prompt, lower temperature; inspect retrieval and policy-version evidence for Q10. |
| 4 | 12 | Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là bao nhiêu? | factual | 0.000000 | faithfulness | Q12 (factual): faithfulness=0.0000, avg=0.0000; 3 retrieved contexts. Hypothesis: LLM hallucinating. Verify against this answer, retrieved contexts and ground truth before attributing cause. | Tighten system prompt, lower temperature; inspect retrieval and policy-version evidence for Q12. |
| 5 | 16 | Tài khoản VPN bị khóa tự động sau bao nhiêu ngày không hoạt động? | factual | 0.000000 | faithfulness | Q16 (factual): faithfulness=0.0000, avg=0.0000; 3 retrieved contexts. Hypothesis: LLM hallucinating. Verify against this answer, retrieved contexts and ground truth before attributing cause. | Tighten system prompt, lower temperature; inspect retrieval and policy-version evidence for Q16. |
| 6 | 19 | Thời gian thử việc tiêu chuẩn và tối đa (dành cho Manager trở lên) là bao nhiêu ngày? | factual | 0.000000 | faithfulness | Q19 (factual): faithfulness=0.0000, avg=0.0000; 3 retrieved contexts. Hypothesis: LLM hallucinating. Verify against this answer, retrieved contexts and ground truth before attributing cause. | Tighten system prompt, lower temperature; inspect retrieval and policy-version evidence for Q19. |
| 7 | 21 | Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào? | multi_hop | 0.000000 | faithfulness | Q21 (multi_hop): faithfulness=0.0000, avg=0.0000; 3 retrieved contexts. Hypothesis: LLM hallucinating. Verify against this answer, retrieved contexts and ground truth before attributing cause. | Tighten system prompt, lower temperature; inspect retrieval and policy-version evidence for Q21. |
| 8 | 26 | Nhân viên vừa kết hôn và cùng tuần đó có con kết hôn. Tổng số ngày nghỉ đặc biệt có lương là bao nhiêu? | multi_hop | 0.000000 | faithfulness | Q26 (multi_hop): faithfulness=0.0000, avg=0.0000; 3 retrieved contexts. Hypothesis: LLM hallucinating. Verify against this answer, retrieved contexts and ground truth before attributing cause. | Tighten system prompt, lower temperature; inspect retrieval and policy-version evidence for Q26. |
| 9 | 28 | Nhân viên cấp Lead nhận tổng phụ cấp hàng tháng (ăn trưa + điện thoại) là bao nhiêu? | multi_hop | 0.000000 | faithfulness | Q28 (multi_hop): faithfulness=0.0000, avg=0.0000; 3 retrieved contexts. Hypothesis: LLM hallucinating. Verify against this answer, retrieved contexts and ground truth before attributing cause. | Tighten system prompt, lower temperature; inspect retrieval and policy-version evidence for Q28. |
| 10 | 36 | Kết quả đánh giá hiệu suất tháng 6 và tháng 12 được dùng để làm gì khác nhau? | multi_hop | 0.000000 | faithfulness | Q36 (multi_hop): faithfulness=0.0000, avg=0.0000; 3 retrieved contexts. Hypothesis: LLM hallucinating. Verify against this answer, retrieved contexts and ground truth before attributing cause. | Tighten system prompt, lower temperature; inspect retrieval and policy-version evidence for Q36. |

Diagnosis do Task 3 xuất là **giả thuyết**, không phải quan sát đã xác minh hallucination. Nếu answer là abstention và context thiếu policy cần thiết, gán nguyên nhân hallucination không phù hợp; hạ temperature không cung cấp policy bị thiếu.

### Đối chiếu answer, contexts và reference

| ID | Answer thực | Titles/version/date contexts | Reference |
| --- | --- | --- | --- |
| 1 | Không tìm thấy. | Chính sách nghỉ ốm \| 1.0 \| 01/01/2024; Chính sách hoàn chi đào tạo \| 1.1 \| 01/07/2023; Quy trình chi phí và hoàn ứng \| 1.3 \| 01/01/2024 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn, không trừ vào phép năm. |
| 8 | Không tìm thấy. | Chính sách hoàn chi đào tạo \| 1.1 \| 01/07/2023; Chính sách nghỉ ốm \| 1.0 \| 01/01/2024; Chính sách nghỉ phép năm (Phiên bản 2023) \| 1.0 \| 01/01/2023 | Nhân viên được nghỉ 3 ngày làm việc có lương khi cha mẹ mất (tang lễ). Không trừ vào phép năm. |
| 10 | Không tìm thấy. | Chính sách VPN và truy cập từ xa \| 1.3 \| 01/04/2024; Chính sách nghỉ phép đặc biệt \| 1.1 \| 01/03/2024; Chính sách thưởng Tết \| 2.0 \| 01/11/2024 | Nhân viên chính thức được phép làm việc từ xa tối đa 2 ngày/tuần. Lịch WFH phải được quản lý trực tiếp phê duyệt vào thứ Hai đầu tuần. |
| 12 | Không tìm thấy. | Chính sách tạm ứng \| 1.0 \| 01/01/2024; Chính sách hoàn chi đào tạo \| 1.1 \| 01/07/2023; Chính sách nghỉ phép không lương \| 1.2 \| 01/07/2023 | Nhân viên chính thức có thời gian làm việc từ 6 tháng trở lên được thưởng Tết tối thiểu 1 tháng lương. Nhân viên dưới 6 tháng được hưởng pro-rata theo số tháng làm việc thực tế. |
| 16 | Không tìm thấy. | Chính sách hoàn chi đào tạo \| 1.1 \| 01/07/2023; Quy trình xử lý sự cố bảo mật \| 1.1 \| 01/05/2024; Chính sách tạm ứng \| 1.0 \| 01/01/2024 | Tài khoản VPN tự động bị khóa sau 60 ngày không hoạt động. Để kích hoạt lại cần gửi ticket IT kèm xác nhận quản lý trực tiếp, thời gian xử lý 1-2 ngày làm việc. |
| 19 | Không tìm thấy. | Chính sách tạm ứng \| 1.0 \| 01/01/2024; Chính sách hoàn chi đào tạo \| 1.1 \| 01/07/2023; Chương trình Mentor & Buddy \| 1.0 \| 01/06/2024 | Thời gian thử việc tiêu chuẩn là 60 ngày. Đối với vị trí Manager trở lên, có thể kéo dài đến 90 ngày. |
| 21 | Không tìm thấy. | Chính sách phụ cấp \| 2.1 \| 01/01/2024; Chính sách hoàn chi đào tạo \| 1.1 \| 01/07/2023; Chương trình Mentor & Buddy \| 1.0 \| 01/06/2024 | Theo chính sách v2024: 15 ngày cơ bản + 3 ngày thâm niên (9÷3=3) = 18 ngày phép. Lương Senior (P3-P4): 20-35 triệu VNĐ/tháng. |
| 26 | Không tìm thấy. | Chương trình Mentor & Buddy \| 1.0 \| 01/06/2024; Chính sách bảo hiểm sức khỏe \| 1.5 \| 01/04/2024; Chính sách hoàn chi đào tạo \| 1.1 \| 01/07/2023 | Kết hôn bản thân: 3 ngày. Con kết hôn: 1 ngày. Tổng: 4 ngày làm việc có lương, tất cả không trừ vào phép năm. |
| 28 | Không tìm thấy. | Chương trình Mentor & Buddy \| 1.0 \| 01/06/2024; Chính sách nghỉ phép không lương \| 1.2 \| 01/07/2023; Quy chế chi trả lương \| 1.1 \| 01/01/2024 | Phụ cấp ăn trưa: 1.000.000 VNĐ. Phụ cấp điện thoại cấp Lead: 300.000 VNĐ. Tổng: 1.300.000 VNĐ/tháng. |
| 36 | Không tìm thấy. | Quy chế chi trả lương \| 1.1 \| 01/01/2024; Chương trình Mentor & Buddy \| 1.0 \| 01/06/2024; Chính sách tạm ứng \| 1.0 \| 01/01/2024 | Tháng 6 (giữa năm): dùng để điều chỉnh mục tiêu cho nửa năm còn lại. Tháng 12 (cuối năm): dùng để xét tăng lương và tính thưởng Tết. Cả hai đều dựa trên KPI 70% + Peer review 30%. |

Cả 10 bottom answers là “Không tìm thấy.”, với bốn metric đều bằng 0. Các contexts trong bảng cho thấy thiếu nguồn chứa facts thiết yếu, phù hợp với lỗi retrieved-context coverage thay vì bằng chứng LLM bịa. Chưa có candidates trước rerank để xác định misses phát sinh tại search hay reranker.

Q1/Q8 thiếu policy nghỉ phép đặc biệt; Q10 thiếu policy WFH quy định 2 ngày/tuần; Q12 thiếu thưởng Tết; Q16 thiếu quy định khóa VPN 60 ngày; Q19 thiếu policy thử việc 60/90 ngày. Không dùng số ngày trong nghỉ ốm hoặc policy gần nghĩa để suy đáp án.

Q21 cần kết hợp phép năm v2024 (15+9/3=18 ngày) và bảng lương Senior (20–35 triệu); context phụ cấp không thay được bảng lương. Q26 cần hai điều khoản nghỉ đặc biệt để cộng 3+1=4 ngày. Q28 cần nguồn phụ cấp ăn trưa 1 triệu và điện thoại Lead 300 nghìn để cộng 1,3 triệu; ba contexts đang có không chứa policy phụ cấp. Q36 cần policy đánh giá hiệu suất để phân biệt điều chỉnh mục tiêu tháng 6 với xét tăng lương/thưởng Tết tháng 12; quy chế chi trả lương không thay được nguồn đó. Ưu tiên đo source coverage/decomposed retrieval cho các câu này, không chỉ hạ temperature generation.

## Matrix và nhóm yếu nhất

| Worst metric | factual | multi_hop | adversarial | Tổng |
| --- | --- | --- | --- | --- |
| faithfulness | 8 | 16 | 5 | 29 |
| answer_relevancy | 10 | 2 | 1 | 13 |
| context_precision | 2 | 1 | 2 | 5 |
| context_recall | 0 | 1 | 2 | 3 |

Distribution 'multi_hop' có điểm trung bình thấp nhất (0.3212). Metric 'faithfulness' là metric thấp nhất thường gặp nhất (29/50 câu). Matrix đếm metric thấp nhất của mọi câu, kể cả câu điểm cao; không phải số failures. Gợi ý cần kiểm chứng: Tighten system prompt, lower temperature.

Matrix phân loại metric thấp nhất của **mọi** câu, kể cả câu tốt; tổng50 không đồng nghĩa50 failures. Khi metrics đồng điểm, quy tắc tie-order chọn worst metric đầu tiên, nên số faithfulness=0 không tự chứng minh LLM bịa.

### Đề xuất sửa và kiểm chứng

1. Ghi top20 candidates trước/sau fusion/rerank cùng source/title để xác định policy cần thiết bị mất tại bước nào; đo coverage theo reference source, không đưa ground_truth vào generation.
2. Decompose multi-hop thành các ý, hợp nhất nguồn trước rerank; chạy lại cùng50 câu để kiểm recall và tỷ lệ answer trả lời đủ ý.
3. Thêm version/effective-date resolution khi câu hỏi yêu cầu hiện hành; giữ cả corpus cũ/mới và kiểm Q41/Q42/Q49 cùng phiên bản mật khẩu Q43/Q44/Q45 thay vì bỏ tài liệu khó.
4. Kiểm ảnh hưởng parent truncation512tokens và multilingual reranker trên CPU; so cấu hình bằng cùng evaluator/model/seed phù hợp, không khẳng định quantization là nguyên nhân khi chưa đo.
5. Giữ abstention khi thiếu nguồn, nhưng theo dõi tỷ lệ coverage/abstention riêng; cải thiện retrieval trước ép generation trả lời.


## Bẫy adversarial và giới hạn

| ID | Question | Answer | Reference | Contexts titles | Faithfulness | Relevancy | Precision | Recall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | Nhân viên được nghỉ bao nhiêu ngày phép năm? | Nhân viên chính thức được hưởng **12 ngày phép năm** có lương. | Theo chính sách v2024 HIỆN HÀNH: 15 ngày cơ bản (+1 ngày/3 năm thâm niên). Chính sách v2023 (đã bị thay thế) là 12 ngày. RAG có thể retrieve cả 2 tài liệu — câu trả lời đúng phải ưu tiên v2024. | Chính sách nghỉ phép năm (Phiên bản 2023) \| 1.0 \| 01/01/2023; Chính sách nghỉ ốm \| 1.0 \| 01/01/2024; Chính sách nghỉ phép đặc biệt \| 1.1 \| 01/03/2024 | 1.000000 | 0.451201 | 1.000000 | 0.333333 |
| 42 | Thâm niên bao nhiêu năm thì được cộng thêm ngày phép? | Không tìm thấy. | Theo v2024 (hiện hành): từ 3 năm thâm niên, cứ mỗi 3 năm thêm 1 ngày. Chính sách v2023 (đã hết hiệu lực) yêu cầu 5 năm. Câu trả lời đúng là theo v2024. | Chính sách hoàn chi đào tạo \| 1.1 \| 01/07/2023; Chính sách tạm ứng \| 1.0 \| 01/01/2024; Chính sách bảo hiểm sức khỏe \| 1.5 \| 01/04/2024 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 43 | Mật khẩu phải có tối thiểu bao nhiêu ký tự? | Mật khẩu phải có tối thiểu 12 ký tự. | Theo v2.0 HIỆN HÀNH: tối thiểu 12 ký tự. Chính sách v1.0 (đã thay thế) yêu cầu 8 ký tự. RAG có thể lấy cả 2 tài liệu — câu trả lời đúng là 12 ký tự. | Quy trình xử lý sự cố bảo mật \| 1.1 \| 01/05/2024; Chính sách mật khẩu (Phiên bản hiện hành) \| 2.0 \| 01/07/2024; Chính sách phân loại dữ liệu \| 1.0 \| 01/06/2024 | 1.000000 | 0.567930 | 0.500000 | 0.666667 |
| 44 | Bao lâu phải đổi mật khẩu một lần? | Mật khẩu phải được thay đổi mỗi 120 ngày. | Theo v2.0 HIỆN HÀNH: mỗi 120 ngày. Chính sách v1.0 (đã hết hiệu lực) là 90 ngày. Câu trả lời đúng là 120 ngày. | Chính sách mật khẩu (Phiên bản hiện hành) \| 2.0 \| 01/07/2024; Chính sách tạm ứng \| 1.0 \| 01/01/2024; Quy trình xử lý sự cố bảo mật \| 1.1 \| 01/05/2024 | 1.000000 | 0.853545 | 1.000000 | 0.666667 |
| 45 | Có cần kích hoạt xác thực đa yếu tố (MFA) không? | Không tìm thấy. | Có, theo v2.0 HIỆN HÀNH, MFA bắt buộc cho tất cả nhân viên: email, VPN và hệ thống nội bộ. Policy v1.0 cũ không yêu cầu MFA — đây là bẫy version conflict. | Chính sách làm việc từ xa (WFH) \| 2.0 \| 01/07/2024; Chính sách hoàn chi đào tạo \| 1.1 \| 01/07/2023; Quy trình chi phí và hoàn ứng \| 1.3 \| 01/01/2024 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| 46 | Nhân viên thử việc có được nghỉ phép năm không? | Không tìm thấy. | KHÔNG. Nhân viên thử việc không được nghỉ phép năm. Nếu cần nghỉ phải xin nghỉ không lương và được trưởng phòng phê duyệt. Đây là negation trap — câu trả lời đúng là phủ định. | Chính sách nghỉ phép không lương \| 1.2 \| 01/07/2023; Chính sách nghỉ phép năm (Phiên bản 2023) \| 1.0 \| 01/01/2023; Chính sách nghỉ phép đặc biệt \| 1.1 \| 01/03/2024 | 0.000000 | 0.000000 | 1.000000 | 0.666667 |
| 47 | Khi phát hiện malware trên máy tính công ty, nhân viên có nên tự xử lý không? | Không, nhân viên **không được tự ý xử lý malware** hoặc tìm cách khắc phục mà không có sự hướng dẫn của đội CNTT. | KHÔNG. Tuyệt đối không tự xử lý. Phải báo cáo trong vòng 1 giờ qua helpdesk@cty.vn hoặc hotline CNTT (ext. 9999). Tự xử lý bị coi là vi phạm nghiêm trọng. | Quy trình xử lý sự cố bảo mật \| 1.1 \| 01/05/2024; Quy trình chi phí và hoàn ứng \| 1.3 \| 01/01/2024; Chính sách nghỉ phép không lương \| 1.2 \| 01/07/2023 | 1.000000 | 0.807151 | 1.000000 | 1.000000 |
| 48 | Nhân viên thử việc có được hưởng bảo hiểm sức khỏe PVI không? | Không tìm thấy. | KHÔNG. Nhân viên thử việc chưa được hưởng gói PVI. Chỉ được tham gia BHXH bắt buộc. Đây là negation trap — pipeline hay nhầm vì tài liệu PVI không đề cập rõ exclusion. | Chính sách bảo hiểm sức khỏe \| 1.5 \| 01/04/2024; Chính sách hoàn chi đào tạo \| 1.1 \| 01/07/2023; Chính sách phụ cấp \| 2.1 \| 01/01/2024 | 0.000000 | 0.000000 | 1.000000 | 0.333333 |
| 49 | Theo chính sách nghỉ phép cũ (v2023), nhân viên được nghỉ bao nhiêu ngày? Còn chính sách nào đang có hiệu lực hiện tại? | Theo chính sách nghỉ phép không lương cũ (v2023), nhân viên được nghỉ tối đa **30 ngày** trong một năm dương lịch. Chính sách hiện tại đang có hiệu lực là **Chính sách nghỉ phép không lương** phiên bản 1.2, có hiệu lực từ **01/07/2023**. | Chính sách cũ v2023 (ĐÃ HẾT HIỆU LỰC): 12 ngày phép, thêm 1 ngày/5 năm thâm niên. Chính sách HIỆN HÀNH v2024: 15 ngày cơ bản, thêm 1 ngày/3 năm thâm niên. Pipeline tốt phải nhận ra v2024 là bản hiệu lực. | Chính sách phụ cấp \| 2.1 \| 01/01/2024; Chính sách nghỉ phép không lương \| 1.2 \| 01/07/2023; Chính sách công tác phí \| 1.5 \| 01/01/2024 | 1.000000 | 0.809229 | 0.000000 | 0.000000 |
| 50 | Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? | Không tìm thấy. | KHÔNG. Chính sách VPN v1.3 cấm sử dụng VPN cá nhân (NordVPN, ExpressVPN) trong mạng công ty. Bắt buộc dùng VPN WireGuard của công ty. Đây là policy contradiction trap — câu hỏi nghe hợp lý nhưng vi phạm chính sách. | Chính sách làm việc từ xa (WFH) \| 2.0 \| 01/07/2024; Chính sách phụ cấp \| 2.1 \| 01/01/2024; Chương trình Mentor & Buddy \| 1.0 \| 01/06/2024 | 0.000000 | 0.000000 | 1.000000 | 0.000000 |

Đối chiếu Q41 với phép năm v2024: policy 2023=12 ngày/+1 mỗi5 năm, policy 2024=15 ngày/+1 mỗi3 năm; faithful theo context cũ vẫn có thể sai đáp án hiện hành. Q43/Q44/Q45 kiểm phiên bản mật khẩu hiện hành (12 ký tự/120 ngày/MFA bắt buộc). Q46/Q48 kiểm phủ định quyền nghỉ phép năm/PVI của thử việc; Q47 yêu cầu báo malware trong1 giờ, không tự xử lý; Q50 cấm VPN cá nhân dù câu hỏi nghe hợp lý. Phải giữ phủ định/điều kiện. Q49 phân biệt đăng ký nghỉ phép năm với nghỉ không lương. Các answer/metrics trong bảng là bằng chứng; abstention không đồng nghĩa pipeline đã nhận ra bẫy. Nếu adversarial mean thấp hơn factual thì đó chỉ là mô tả kết quả, cần đọc policy/answer để quy nguyên nhân.

### Giới hạn

Bộ50 câu nhỏ, cùng corpus nội bộ, score RAGAS phụ thuộc evaluator. Chưa có holdout hoặc CI đã triển khai. Lượt này không được so với số liệu lịch sử đã xóa. Đánh giá gates và monitoring xem blueprint; checker/tests pass không phải điểm chất lượng RAG.
