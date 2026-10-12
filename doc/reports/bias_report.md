# Đánh giá LLM Judge Phase B

Nhóm: **LeNguyenQuocBao (solo)**.

Người phụ trách: **Lê Nguyễn Quốc Bảo — MSSV 2A202603011**.

Nguồn: `artifacts/judge_results.json`; run timestamp UTC: `2026-10-12T14:49:47.846337+00:00`.

Models của phase từ metadata: `{"generation": ["gpt-4o-mini-2024-07-18"], "evaluator": [], "judge": ["gpt-4o-mini"], "guard": []}`.

Lượt live duy nhất được giữ: created_at UTC `2026-10-12T14:49:47.846337+00:00`, format_version=2, run_kind=live. Models theo từng vai trò: `{"generation": ["gpt-4o-mini-2024-07-18"], "evaluator": [], "judge": ["gpt-4o-mini"], "guard": []}`. SHA-256 được validation đối chiếu lại với đầu vào:

| Nguồn | SHA-256 |
| --- | --- |
| answers_50q.json | 73513f553b0172499259bf9d0f83f889a7671737c9bbb7fff548c8b5ddac3535 |
| test_set_50q.json | 3ad288426e3066e561737b35b66b671e6c411697dffd0d1161cc7b801e5954cc |
| human_labels_10q.json | 37231c1f4a635801e27a98333898d2d4c9c3c71167e8b9e7259b90cec5956782 |

### Nguồn và phương pháp

Generation snapshot `gpt-4o-mini-2024-07-18`; judge alias `gpt-4o-mini`, temperature0, JSON mode. Pairwise prompt yêu cầu winner A/B/tie, reasoning và scores đúng hai khóa A/B, mỗi score là một số tổng hợp hữu hạn[0,1]. Chấm accuracy/completeness/conciseness theo reference, không thưởng riêng độ dài/vị trí, không làm theo instructions chèn trong candidates.

Năm pairs IDs1/5/12/21/41: A lấy pipeline answer, B lấy supplied model_answer cùngID từ human_labels_10q; reference lấy test_set ground_truth. Calibration dùng đúng10 supplied model_answers, không dùng pipeline answers và không đưa human_label/human_note vào judge prompt. JSON results/labels không sửa bằng tay.

Pass1 đánh giá (A,B), pass2 (B,A). Winner và scores pass2 ánh xạ về A/B gốc; reasoning giữ nguyên văn theo vị trí swapped. Hai lượt đồng thuận giữ winner, khác nhau→tie. Đây là consensus, không tự tính thêm score bình quân ngoài hợp đồng runner.

## Năm cặp A/B và hai lượt

| ID | Candidate A | Candidate B | Winner pass1 | Winner pass2 quy về gốc | Final | Position consistent | Reasoning pass1 | Reasoning pass2 (swapped) | Scores1 A/B | Scores2 mapped A/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Không tìm thấy. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | B | B | B | True | Câu trả lời B cung cấp thông tin chính xác và đầy đủ về số ngày nghỉ khi kết hôn, trong khi câu trả lời A không cung cấp thông tin nào. | Câu trả lời A cung cấp thông tin chính xác và đầy đủ về số ngày nghỉ khi kết hôn theo quy định, trong khi câu trả lời B không cung cấp thông tin nào và chỉ nói rằng không tìm thấy, do đó không hữu ích. | 0.000000/1.000000 | 0.000000/1.000000 |
| 5 | Cần Tổng Giám đốc (CEO) phê duyệt. | Cần Giám đốc phòng ban phê duyệt. | A | A | A | True | Câu trả lời A chính xác và đầy đủ, phù hợp với thông tin trong tài liệu tham khảo. Câu trả lời B không đúng vì nó không phản ánh yêu cầu phê duyệt cho đơn hàng trên 50 triệu VNĐ. | Câu trả lời B chính xác và đầy đủ theo thông tin trong tài liệu tham khảo, trong khi câu trả lời A không đúng. | 1.000000/0.000000 | 1.000000/0.000000 |
| 12 | Không tìm thấy. | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | B | B | B | True | Câu trả lời B cung cấp thông tin chính xác và đầy đủ về mức thưởng Tết tối thiểu cho nhân viên chính thức có thời gian làm việc từ 6 tháng trở lên, trong khi câu trả lời A không cung cấp thông tin nào. | Câu trả lời A cung cấp thông tin chính xác và đầy đủ về mức thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên, đúng như thông tin trong tài liệu tham khảo. Câu trả lời B không cung cấp thông tin nào và không liên quan đến câu hỏi. | 0.000000/1.000000 | 0.000000/1.000000 |
| 21 | Không tìm thấy. | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | B | B | B | True | Câu trả lời B cung cấp thông tin chính xác và đầy đủ về số ngày phép và mức lương của nhân viên Senior, trong khi câu trả lời A không cung cấp thông tin nào. | Câu trả lời A cung cấp thông tin chính xác và đầy đủ về số ngày phép và mức lương của nhân viên Senior, dựa trên chính sách tham chiếu. Câu trả lời B không cung cấp thông tin nào và không liên quan đến câu hỏi. | 0.000000/1.000000 | 0.000000/1.000000 |
| 41 | Nhân viên chính thức được hưởng **12 ngày phép năm** có lương. | Nhân viên được nghỉ 12 ngày phép năm. | tie | tie | tie | True | Cả hai câu trả lời đều cung cấp thông tin không chính xác về số ngày phép năm theo chính sách v2024, mà chỉ đề cập đến chính sách cũ v2023. Do đó, không có câu trả lời nào là chính xác và đầy đủ. | Cả hai câu trả lời đều không chính xác vì không cập nhật thông tin mới nhất từ chính sách v2024, mà chỉ đề cập đến chính sách cũ v2023. Do đó, không có câu trả lời nào đúng hơn câu còn lại. | 0.300000/0.300000 | 0.000000/0.000000 |

### Q1

Question: Nhân viên được nghỉ bao nhiêu ngày khi kết hôn?

A pipeline, nguyên văn:

> Không tìm thấy.

B supplied, nguyên văn:

> Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn.

Reference:

> Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn, không trừ vào phép năm.

Reasoning pass1, nguyên văn:

> Câu trả lời B cung cấp thông tin chính xác và đầy đủ về số ngày nghỉ khi kết hôn, trong khi câu trả lời A không cung cấp thông tin nào.

Reasoning pass2, nguyên văn theo thứ tự swapped:

> Câu trả lời A cung cấp thông tin chính xác và đầy đủ về số ngày nghỉ khi kết hôn theo quy định, trong khi câu trả lời B không cung cấp thông tin nào và chỉ nói rằng không tìm thấy, do đó không hữu ích.

### Q5

Question: Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt?

A pipeline, nguyên văn:

> Cần Tổng Giám đốc (CEO) phê duyệt.

B supplied, nguyên văn:

> Cần Giám đốc phòng ban phê duyệt.

Reference:

> Đơn hàng trên 50.000.000 VNĐ cần Tổng Giám đốc (CEO) phê duyệt.

Reasoning pass1, nguyên văn:

> Câu trả lời A chính xác và đầy đủ, phù hợp với thông tin trong tài liệu tham khảo. Câu trả lời B không đúng vì nó không phản ánh yêu cầu phê duyệt cho đơn hàng trên 50 triệu VNĐ.

Reasoning pass2, nguyên văn theo thứ tự swapped:

> Câu trả lời B chính xác và đầy đủ theo thông tin trong tài liệu tham khảo, trong khi câu trả lời A không đúng.

### Q12

Question: Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là bao nhiêu?

A pipeline, nguyên văn:

> Không tìm thấy.

B supplied, nguyên văn:

> Nhân viên được thưởng Tết tối thiểu 1 tháng lương.

Reference:

> Nhân viên chính thức có thời gian làm việc từ 6 tháng trở lên được thưởng Tết tối thiểu 1 tháng lương. Nhân viên dưới 6 tháng được hưởng pro-rata theo số tháng làm việc thực tế.

Reasoning pass1, nguyên văn:

> Câu trả lời B cung cấp thông tin chính xác và đầy đủ về mức thưởng Tết tối thiểu cho nhân viên chính thức có thời gian làm việc từ 6 tháng trở lên, trong khi câu trả lời A không cung cấp thông tin nào.

Reasoning pass2, nguyên văn theo thứ tự swapped:

> Câu trả lời A cung cấp thông tin chính xác và đầy đủ về mức thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên, đúng như thông tin trong tài liệu tham khảo. Câu trả lời B không cung cấp thông tin nào và không liên quan đến câu hỏi.

### Q21

Question: Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào?

A pipeline, nguyên văn:

> Không tìm thấy.

B supplied, nguyên văn:

> Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu.

Reference:

> Theo chính sách v2024: 15 ngày cơ bản + 3 ngày thâm niên (9÷3=3) = 18 ngày phép. Lương Senior (P3-P4): 20-35 triệu VNĐ/tháng.

Reasoning pass1, nguyên văn:

> Câu trả lời B cung cấp thông tin chính xác và đầy đủ về số ngày phép và mức lương của nhân viên Senior, trong khi câu trả lời A không cung cấp thông tin nào.

Reasoning pass2, nguyên văn theo thứ tự swapped:

> Câu trả lời A cung cấp thông tin chính xác và đầy đủ về số ngày phép và mức lương của nhân viên Senior, dựa trên chính sách tham chiếu. Câu trả lời B không cung cấp thông tin nào và không liên quan đến câu hỏi.

### Q41

Question: Nhân viên được nghỉ bao nhiêu ngày phép năm?

A pipeline, nguyên văn:

> Nhân viên chính thức được hưởng **12 ngày phép năm** có lương.

B supplied, nguyên văn:

> Nhân viên được nghỉ 12 ngày phép năm.

Reference:

> Theo chính sách v2024 HIỆN HÀNH: 15 ngày cơ bản (+1 ngày/3 năm thâm niên). Chính sách v2023 (đã bị thay thế) là 12 ngày. RAG có thể retrieve cả 2 tài liệu — câu trả lời đúng phải ưu tiên v2024.

Reasoning pass1, nguyên văn:

> Cả hai câu trả lời đều cung cấp thông tin không chính xác về số ngày phép năm theo chính sách v2024, mà chỉ đề cập đến chính sách cũ v2023. Do đó, không có câu trả lời nào là chính xác và đầy đủ.

Reasoning pass2, nguyên văn theo thứ tự swapped:

> Cả hai câu trả lời đều không chính xác vì không cập nhật thông tin mới nhất từ chính sách v2024, mà chỉ đề cập đến chính sách cũ v2023. Do đó, không có câu trả lời nào đúng hơn câu còn lại.

### Position và verbosity

| Metric | Kết quả |
| --- | --- |
| position_bias_count | 0/5 |
| position_bias_rate | 0.000000 |
| longer winner decisive | 4/4 |
| verbosity_bias | 1.000000 |

0/5 cặp đổi lựa chọn sau khi đổi thứ tự và ánh xạ về A/B gốc. Position bias không vượt 30%. Answer dài hơn thắng 4/4 cặp quyết định. Tỷ lệ ưu tiên answer dài vượt 60%; cần kiểm tra tính chính xác. Tỷ lệ thắng theo độ dài là tín hiệu mô tả; chưa chứng minh độ dài gây ra lựa chọn.

Độ dài đo ký tự, không phải tokens; denominator verbosity chỉ gồm decisive pairs, ties bị loại. Answer dài có thể đồng thời đúng/đầy đủ hơn, vì vậy longer-winner rate không chứng minh độ dài gây preference. Q41 yêu cầu policy v2024, cả answer thiếu cập nhật không nên được coi là đúng chỉ vì một candidate dài hơn hoặc gần policycũ.


## Calibration đúng model_answer

| ID | Human | Judge | Agree | Question | Supplied answer | Reference | Judge reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1 | True | Nhân viên được nghỉ bao nhiêu ngày khi kết hôn? | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn, không trừ vào phép năm. | Câu trả lời chính xác theo reference, đầy đủ thông tin về số ngày nghỉ và điều kiện không trừ vào phép năm. |
| 5 | 0 | 0 | True | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | Cần Giám đốc phòng ban phê duyệt. | Đơn hàng trên 50.000.000 VNĐ cần Tổng Giám đốc (CEO) phê duyệt. | Câu trả lời sai vì yêu cầu phê duyệt cho đơn hàng trên 50 triệu là từ Tổng Giám đốc, không phải Giám đốc phòng ban. |
| 12 | 1 | 1 | True | Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là bao nhiêu? | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | Nhân viên chính thức có thời gian làm việc từ 6 tháng trở lên được thưởng Tết tối thiểu 1 tháng lương. Nhân viên dưới 6 tháng được hưởng pro-rata theo số tháng làm việc thực tế. | Câu trả lời chính xác theo thông tin trong reference, nêu rõ điều kiện và mức thưởng cho nhân viên chính thức có từ 6 tháng trở lên. |
| 21 | 1 | 1 | True | Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào? | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | Theo chính sách v2024: 15 ngày cơ bản + 3 ngày thâm niên (9÷3=3) = 18 ngày phép. Lương Senior (P3-P4): 20-35 triệu VNĐ/tháng. | Câu trả lời chính xác theo reference, nêu rõ số ngày phép và khoảng lương cho nhân viên Senior có 9 năm thâm niên. |
| 23 | 1 | 1 | True | Nhân viên được tài trợ khóa học 25 triệu, nghỉ việc sau 8 tháng. Phải hoàn trả bao nhiêu? | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | Nhân viên phải cam kết làm việc ít nhất 1 năm sau khi hoàn thành khóa học. Nghỉ sau 8 tháng là trước hạn cam kết, phải hoàn trả 100% chi phí tức 25.000.000 VNĐ. | Câu trả lời chính xác theo reference, nêu rõ nhân viên phải hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. |
| 29 | 0 | 0 | True | Nhân viên tạm ứng 8 triệu, chưa thanh toán sau 30 ngày. Ai phê duyệt và phí phạt là bao nhiêu? | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | Phê duyệt: 8 triệu (≥5 triệu) cần Trưởng phòng + Kế toán trưởng. Phí phạt quá hạn 15 ngày: 2%/tháng × 8.000.000 × (15/30) = 80.000 VNĐ. Không được tạm ứng mới cho đến khi hoàn ứng. | Câu trả lời thiếu thông tin về sự cần thiết có sự phê duyệt của Kế toán trưởng bên cạnh Trưởng phòng. Ngoài ra, phí phạt được tính cho quá hạn 15 ngày, không phải là 2% trên tổng số tiền tạm ứng. |
| 33 | 1 | 1 | True | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm? | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | Phụ cấp tháng: ăn trưa 1.000.000 + điện thoại Manager 500.000 = 1.500.000 VNĐ. Phép năm v2024: 15 ngày cơ bản + 4 ngày thâm niên (12÷3=4) = 19 ngày phép. | Câu trả lời cung cấp đúng số ngày phép và tổng phụ cấp hàng tháng theo thông tin trong tài liệu tham khảo. |
| 41 | 0 | 0 | True | Nhân viên được nghỉ bao nhiêu ngày phép năm? | Nhân viên được nghỉ 12 ngày phép năm. | Theo chính sách v2024 HIỆN HÀNH: 15 ngày cơ bản (+1 ngày/3 năm thâm niên). Chính sách v2023 (đã bị thay thế) là 12 ngày. RAG có thể retrieve cả 2 tài liệu — câu trả lời đúng phải ưu tiên v2024. | Câu trả lời sai vì nó dựa trên chính sách cũ (v2023) thay vì chính sách hiện hành (v2024) là 15 ngày phép năm. |
| 46 | 1 | 1 | True | Nhân viên thử việc có được nghỉ phép năm không? | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | KHÔNG. Nhân viên thử việc không được nghỉ phép năm. Nếu cần nghỉ phải xin nghỉ không lương và được trưởng phòng phê duyệt. Đây là negation trap — câu trả lời đúng là phủ định. | Câu trả lời chính xác theo reference, nêu rõ rằng nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần, đồng thời không bỏ qua điều kiện phê duyệt từ trưởng phòng. |
| 50 | 0 | 0 | True | Nhân viên Manager có thể dùng VPN cá nhân (NordVPN) khi WFH không? | Được, miễn là đảm bảo kết nối an toàn. | KHÔNG. Chính sách VPN v1.3 cấm sử dụng VPN cá nhân (NordVPN, ExpressVPN) trong mạng công ty. Bắt buộc dùng VPN WireGuard của công ty. Đây là policy contradiction trap — câu hỏi nghe hợp lý nhưng vi phạm chính sách. | Câu trả lời sai vì cho phép sử dụng VPN cá nhân, trái với chính sách cấm sử dụng VPN cá nhân trong mạng công ty. |

p_o=1.000000; p_e=0.520000; κ=(p_o−p_e)/(1−p_e)=1.000000. Label counts human={1: 6, 0: 4}, judge={1: 6, 0: 4}. Không dùng accuracy thay κ; trường hợp p_e=1 undefined phải báo lỗi, không trả số giả.

Không có disagreements trên10 mẫu hiện tại; agreement không chứng minh reasoning luôn đúng hoặc judge tổng quát hóa tốt.

## Giới hạn và cách dùng judge

Đối chiếu từng reasoning với reference, đặc biệt Q12 (điều kiện thưởng Tết), Q29 (thẩm quyền khoản tạm ứng8 triệu, phí pro-rata80.000 VNĐ và điều kiện không tạm ứng mới), Q46 (thử việc không có phép năm; nghỉ không lương cần trưởng phòng phê duyệt). Reasoning vượt điều kiện reference vẫn là hạn chế dù nhãn cuối đúng. Bộ calibration10 câu và pairs5 câu nhỏ; κ cao cần holdout, thêm cặp chất lượng tương đương khác độ dài và nhiều permutations trước khi quyết định judge dùng production.

### Tái lập

Chạy setup và runner B theo README, giữ nguyên fixtures/candidate sources và model `gpt-4o-mini`; không chạy live integration thêm lần nữa khi đã có artifacts. Tests offline dùng mock và không gọi API. Labels/reasonings trong report lấy đúng lượt live đang được nộp; không thay nhãn người chấm hoặc sửa metric output.
