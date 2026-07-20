# AI Engineer — Tiếng Anh cho Kỹ sư AI

Tài liệu này dành cho **AI engineer**, **ML engineer** và **data scientist** người Việt làm việc trong team quốc tế hoặc báo cáo cho stakeholder nước ngoài.
Dùng khi bạn trình bày kết quả thí nghiệm, giải thích giới hạn của model cho người không rành kỹ thuật, xin thêm ngân sách GPU, hoặc review một pipeline RAG trong sprint meeting.
Trình độ: **B1–B2**. Học xong bạn có thể nói về **accuracy**, **baseline** và **trade-off** một cách tự nhiên, không phải dịch từng chữ trong đầu.

---

## 1. Từ vựng cốt lõi (Core Vocabulary)

| Term | Definition (EN) | Example Sentence | Tiếng Việt |
| --- | --- | --- | --- |
| Model | A trained program that makes predictions from data | The new **model** is 4% more accurate but twice as slow. | Mô hình |
| Training | The process of teaching a model using data | **Training** took 18 hours on four A100 GPUs. | Huấn luyện |
| Inference | Running a trained model to get a prediction | **Inference** latency must stay under 800 ms for the chat feature. | Suy luận / chạy dự đoán |
| Dataset | The collection of examples used to train or test | We cleaned the **dataset** and removed 12,000 duplicate rows. | Tập dữ liệu |
| Test set | Held-out data used only for the final measurement | Never tune on the **test set**, or the result is meaningless. | Tập kiểm tra |
| Baseline | The simple reference result you must beat | Our **baseline** is keyword search at 0.61 recall. | Mốc đối chiếu |
| Accuracy | The share of predictions that are correct | **Accuracy** rose from 82% to 88% after the data cleanup. | Độ chính xác |
| Precision | Of the items predicted positive, how many are right | High **precision** matters here because false alarms are expensive. | Độ chuẩn xác |
| Recall | Of the real positives, how many the model found | We traded some precision for higher **recall**. | Độ bao phủ |
| Evaluation | Measuring model quality against defined metrics | The **evaluation** runs automatically on every pull request. | Đánh giá mô hình |
| Overfitting | When a model memorises training data and fails on new data | Validation loss went up while training loss fell, classic **overfitting**. | Học vẹt / quá khớp |
| Hyperparameter | A setting chosen before training, such as learning rate | We ran a sweep over three **hyperparameter** values. | Siêu tham số |
| Parameter | A value the model learns during training | The 7B model has seven billion **parameters**. | Tham số |
| Epoch | One full pass over the training data | Loss stopped improving after the third **epoch**. | Vòng huấn luyện |
| Checkpoint | A saved snapshot of model weights | We rolled back to the **checkpoint** from epoch two. | Điểm lưu mô hình |
| Fine-tuning | Further training a base model on your own data | **Fine-tuning** on 5,000 support tickets improved tone consistency. | Tinh chỉnh mô hình |
| LLM | Large Language Model, trained on very large text corpora | We compare three **LLM** providers on cost and latency. | Mô hình ngôn ngữ lớn |
| Prompt engineering | Designing instructions that make a model behave as needed | Better **prompt engineering** removed most of the formatting errors. | Thiết kế câu lệnh |
| Token | The smallest text unit an LLM processes | The document is 12,000 **tokens**, above the context limit. | Đơn vị văn bản |
| Context window | The maximum tokens a model can read at once | We chunk long files because of the 128k **context window**. | Cửa sổ ngữ cảnh |
| Embedding | A numeric vector representing meaning | We store one **embedding** per paragraph, not per document. | Vector ngữ nghĩa |
| Vector database | A store optimised for similarity search over embeddings | The **vector database** returns the top ten passages in 30 ms. | Cơ sở dữ liệu vector |
| RAG | Retrieval Augmented Generation, feeding retrieved text to an LLM | **RAG** lets the assistant answer from our internal policies. | Sinh có truy hồi dữ liệu |
| Hallucination | A confident but factually wrong model output | We reduced **hallucination** by forcing the model to cite sources. | Bịa đặt thông tin |
| Pipeline | The automated chain from raw data to deployed model | The **pipeline** runs nightly and retrains if drift is detected. | Chuỗi xử lý |
| MLOps | Practices for deploying and operating models reliably | Our **MLOps** setup gives us versioned datasets and one-click rollback. | Vận hành mô hình |
| Deployment | Putting a model into production so users can call it | The **deployment** is behind a feature flag for 10% of users. | Triển khai |
| GPU utilization | How fully the GPU is being used during a job | **GPU utilization** was only 35%, so the data loader is the bottleneck. | Mức sử dụng GPU |
| Drift | When live data slowly stops matching training data | We alert on **drift** when the input distribution shifts by 15%. | Trôi dữ liệu |
| Trade-off | Accepting a loss in one area to gain in another | The **trade-off** is 200 ms more latency for 6% better accuracy. | Đánh đổi |

> **Phát âm — người Việt hay sai**
> - **inference**: /ˈɪn.fər.əns/ — "IN-fer-ens", nhấn âm ĐẦU. Rất nhiều người đọc thành "in-FER-ens", nghe sai hẳn.
> - **epoch**: /ˈep.ək/ hoặc /ˈiː.pɒk/ — "EP-ok". KHÔNG đọc là "i-pốc-h" hay "e-pô-chờ".
> - **cache**: /kæʃ/ — đọc y hệt "cash". KHÔNG phải "ca-chê".
> - **query**: /ˈkwɪə.ri/ — "KWEER-ee". KHÔNG phải "quê-ri".
> - **parameter**: /pəˈræm.ɪ.tər/ — nhấn âm thứ HAI, "pa-RAM-e-ter".
> - **deploy**: /dɪˈplɔɪ/ — "di-PLOY", nhấn âm sau. Danh từ **deployment** cũng nhấn âm thứ hai.

---

## 2. Mẫu câu giao tiếp (Common Phrases)

### Báo cáo (Reporting)

1. **Formal** — "The fine-tuned model outperforms the baseline by 6 points on the test set." → Model đã tinh chỉnh vượt mốc đối chiếu 6 điểm trên tập kiểm tra.
2. **Formal** — "These numbers come from the held-out test set, not from validation, so they should generalise." → Các con số này lấy từ tập test giữ riêng, không phải validation, nên có thể khái quát được.
3. **Formal** — "Training completed in 18 hours at an estimated cost of 420 US dollars." → Việc huấn luyện mất 18 giờ, chi phí ước tính 420 đô la.
4. **Informal** — "Quick update: the eval finished, accuracy is up but latency doubled." → Cập nhật nhanh: eval xong rồi, accuracy tăng nhưng latency gấp đôi.
5. **Informal** — "Numbers are in the notebook, I'll walk you through them in standup." → Số liệu ở trong notebook, mai standup mình trình bày.

### Yêu cầu (Requesting)

6. **Formal** — "Could we allocate two additional A100 GPUs for the next two weeks?" → Chúng ta có thể cấp thêm hai GPU A100 trong hai tuần tới không ạ?
7. **Formal** — "I would like to request approval for a labelling budget of [amount]." → Tôi xin phê duyệt ngân sách gán nhãn dữ liệu là [số tiền].
8. **Formal** — "Before we proceed, could you confirm which metric the business cares about most?" → Trước khi làm tiếp, anh/chị xác nhận giúp chỉ số nào quan trọng nhất với kinh doanh?
9. **Informal** — "Can you share the eval script? I want to reproduce your run." → Gửi mình script eval nhé, mình muốn chạy lại kết quả của bạn.
10. **Informal** — "Could you review my prompt template before I ship it?" → Bạn review giúp prompt template trước khi mình đẩy lên nhé.

### Giải thích (Explaining)

11. **Formal** — "In simple terms, the model predicts the most likely next word. It does not verify facts." → Nói đơn giản, model dự đoán từ có khả năng xuất hiện tiếp theo. Nó không kiểm chứng sự thật.
12. **Formal** — "There is a trade-off here: we can have lower latency or higher accuracy, not both." → Có sự đánh đổi ở đây: hoặc độ trễ thấp hơn, hoặc độ chính xác cao hơn, không thể cả hai.
13. **Formal** — "The model is confident even when it is wrong, which is why we require citations." → Model tự tin ngay cả khi sai, nên chúng tôi bắt buộc phải trích nguồn.
14. **Informal** — "Think of the embedding as a coordinate for meaning, similar meanings sit close together." → Cứ hình dung embedding như toạ độ của ý nghĩa, nghĩa giống nhau thì nằm gần nhau.
15. **Informal** — "RAG basically gives the model an open book instead of asking it to memorise." → RAG về cơ bản là đưa cho model quyển sách mở, thay vì bắt nó học thuộc.

### Xử lý sự cố (Troubleshooting)

16. **Formal** — "We have identified the root cause as a mismatch between training and serving preprocessing." → Chúng tôi xác định nguyên nhân gốc là tiền xử lý lúc train và lúc phục vụ không khớp nhau.
17. **Formal** — "We have rolled back to the previous checkpoint while we investigate." → Chúng tôi đã quay lại checkpoint trước trong lúc điều tra.
18. **Informal** — "GPU utilization is only 35%, so I think the data loader is the bottleneck." → GPU chỉ dùng 35%, mình nghĩ nút thắt là ở data loader.
19. **Informal** — "Loss is not going down at all. Let me check the learning rate first." → Loss không giảm chút nào. Để mình kiểm tra learning rate trước.
20. **Informal** — "That output looks like a hallucination. Can you send me the exact prompt?" → Kết quả đó có vẻ là bịa. Gửi mình đúng prompt được không?

> **Lỗi lịch sự thường gặp:** khi stakeholder hỏi model có làm được việc X không, đừng trả lời cụt lủn *"No, impossible"*. Hãy dùng **"That's not reliable with the current approach, but here's what we can do instead…"** — vẫn từ chối, nhưng mở đường. Ngoài ra, tránh nói *"The model is stupid"* trong họp với khách; dùng **"The model has a known limitation in this area."**

---

## 3. Tình huống thực tế (Real-world Scenarios)

### Kịch bản 1 — Trình bày kết quả thí nghiệm trong sprint review

*Bối cảnh: Bạn báo cáo kết quả fine-tuning cho tech lead và product manager.*

**Lead:** How did the fine-tuning experiment go?
**Engineer:** Better than expected. The baseline scored 0.74 F1, the fine-tuned model reaches 0.81.
**PM:** Is that a big difference in practice?
**Engineer:** It means roughly one fewer wrong answer in every fourteen requests.
**Lead:** Which metric moved most, precision or recall?
**Engineer:** Recall, from 0.68 to 0.79. Precision stayed almost flat.
**PM:** And the cost?
**Engineer:** Training was about 420 dollars, and inference cost per request goes up 12% because the model is larger.
**Lead:** Did you check for overfitting?
**Engineer:** Yes. I evaluated on a held-out test set the model never saw, and the gap to validation is under one point.
**PM:** Good. Can we ship it next sprint?
**Engineer:** I'd like one week of shadow testing on live traffic first, then we decide with real data.

### Kịch bản 2 — Giải thích giới hạn của model cho stakeholder không rành kỹ thuật

*Bối cảnh: Giám đốc kinh doanh muốn dùng chatbot AI trả lời câu hỏi hợp đồng của khách hàng.*

**Director:** Can the assistant answer contract questions for customers directly?
**Engineer:** It can answer many of them, but I want to be clear about one limitation first.
**Director:** Go ahead.
**Engineer:** The model predicts likely text. It does not check whether the answer is legally true.
**Director:** So it can be wrong and still sound convincing?
**Engineer:** Exactly. We call that a hallucination, and it's the main risk in a contract context.
**Director:** How do we reduce that risk?
**Engineer:** Three things. We retrieve the real clause and show it, we force the model to cite the source, and we route anything about money or termination to a human.
**Director:** What accuracy can you promise?
**Engineer:** On our test set, 91% of answers were correct and fully cited. I would not promise more than that in production.
**Director:** That's acceptable if a human reviews the rest. Let's start with internal staff before customers.
**Engineer:** Agreed. That's exactly the rollout I would recommend.

### Kịch bản 3 — Thảo luận nội bộ về chi phí GPU

*Bối cảnh: Team họp vì hoá đơn GPU tháng này vượt ngân sách.*

**Manager:** Our GPU spend was 40% over budget last month. What happened?
**Engineer A:** Two things. We ran a hyperparameter sweep with sixteen configurations, and several jobs kept the GPUs idle.
**Manager:** Idle how?
**Engineer A:** GPU utilization averaged 38%. The data loader could not feed the GPU fast enough.
**Engineer B:** We also forgot to shut down two instances over the weekend.
**Manager:** That last one sounds avoidable.
**Engineer B:** It is. I'll add an auto-shutdown after two hours of inactivity.
**Engineer A:** And I'll cache the preprocessed dataset so we stop repeating the same work every epoch.
**Manager:** How much will those two changes save?
**Engineer A:** My estimate is 30 to 35%, mostly from better utilization.
**Manager:** Do both this sprint, and send me the numbers again in four weeks.

### Kịch bản 4 — Xử lý sự cố model chạy tốt lúc test, hỏng lúc production

*Bối cảnh: Model mới deploy hôm qua nhưng chất lượng trả lời tụt hẳn.*

**On-call:** Users are complaining that answers got worse since yesterday's deployment.
**Engineer:** Offline evaluation looked fine, so let's compare offline and online inputs.
**On-call:** What should I look at first?
**Engineer:** Send me ten real production requests and the exact text the model received.
**On-call:** Here they are. The text looks different from our samples, there's a lot of HTML in it.
**Engineer:** That's the cause. Our training pipeline strips HTML, the serving path does not.
**On-call:** So the model sees something it never saw in training?
**Engineer:** Correct. It's a training and serving mismatch, not a model quality issue.
**On-call:** Do we roll back?
**Engineer:** Yes, roll back to the previous version now, then I'll apply the same preprocessing on both sides and redeploy tomorrow.

### Kịch bản 5 — Review thiết kế pipeline RAG

*Bối cảnh: Hai kỹ sư review thiết kế RAG trước khi bắt tay code.*

**Engineer A:** Let me walk you through the RAG design before we start coding.
**Engineer B:** Sure. What's the chunking strategy?
**Engineer A:** 500 tokens per chunk with 50 tokens of overlap, so a sentence is never cut in half.
**Engineer B:** And the vector database?
**Engineer A:** We store one embedding per chunk and return the top ten, then rerank down to three.
**Engineer B:** Why rerank? That adds latency.
**Engineer A:** About 90 ms, but it removes most irrelevant passages, which cuts hallucinations noticeably.
**Engineer B:** What happens when nothing relevant is found?
**Engineer A:** The model must reply "I don't have that information" instead of guessing. That rule is in the system prompt and in the evaluation.
**Engineer B:** Good. How do we measure the whole thing?
**Engineer A:** Two metrics: retrieval recall at ten, and answer correctness judged against fifty reference questions.

### Kịch bản 6 — Báo cáo trạng thái hàng ngày

*Bối cảnh: Daily standup của team ML, mỗi người báo cáo trong hai phút.*

**Lead:** What's your status today?
**Engineer:** Yesterday I finished the dataset cleanup. I removed 12,000 duplicates and fixed the label noise in the support category.
**Lead:** Did that change the numbers?
**Engineer:** Yes, accuracy went from 82 to 88% on the same model, just from cleaner data.
**Lead:** That's a strong result. What's next?
**Engineer:** Today I'm running the evaluation on the full test set and writing up the comparison.
**Lead:** Any blockers?
**Engineer:** One. The GPU queue is full until this afternoon, so the run may finish late.
**Lead:** Can you use the smaller instance in the meantime?
**Engineer:** I can run a subset on it to sanity-check the script, then do the full run tonight.

### Kịch bản 7 — Escalation khi deadline không khả thi

*Bối cảnh: Product manager muốn ra tính năng trong hai tuần, bạn thấy không đủ thời gian.*

**PM:** Can we launch the AI summariser in two weeks?
**Engineer:** I want to be honest with you rather than agree and miss the date.
**PM:** Please be honest.
**Engineer:** Building the pipeline takes about five days. The problem is evaluation, we have no labelled reference summaries yet.
**PM:** How long does that take?
**Engineer:** Roughly one week to write 100 reference summaries, and we need a domain expert for that.
**PM:** What if we skip the evaluation?
**Engineer:** Then we ship without knowing whether it works, and we cannot tell if a later change makes it worse.
**PM:** Is there a middle option?
**Engineer:** Yes. Launch in two weeks as an internal beta with 30 reference summaries, then expand to customers in week four.
**PM:** I can sell that internally. Send me the plan with the two milestones today.

> **Ghi chú:** Trong kịch bản 7, kỹ sư KHÔNG nói *"Impossible"*. Cấu trúc dùng ở đây là: nói rõ ràng buộc → giải thích hậu quả nếu bỏ qua → đề xuất phương án trung gian. Đây là cách nói "không" mà vẫn giữ được sự tin tưởng.

---

## 4. Email mẫu (Email Templates)

### 4.1 Incident notification

```text
Subject: [INCIDENT] [P1] Degraded output quality on [MODEL_NAME] in production

Dear all,

We have identified a quality degradation affecting [SERVICE_NAME].

Detected at:       [DETECTION_TIME] [TIMEZONE]
Affected model:    [MODEL_NAME] version [MODEL_VERSION]
Affected traffic:  [PERCENT]% of requests
Symptom:           [SYMPTOM, e.g. irrelevant answers, missing citations]

Current status: [INVESTIGATING / MITIGATED / ROLLED BACK]

What we know so far:
[SHORT_TECHNICAL_SUMMARY]

Immediate action taken:
- [ACTION_1, e.g. rolled back to version X]
- [ACTION_2, e.g. disabled the feature flag for new users]

User impact and workaround:
[IMPACT_AND_WORKAROUND]

Next update: [NEXT_UPDATE_TIME]

Best regards,
[YOUR_NAME]
ML Platform, [COMPANY]
```

### 4.2 Maintenance announcement

```text
Subject: [SCHEDULED MAINTENANCE] [MODEL_NAME] retraining on [DATE]

Dear colleagues,

We will retrain and redeploy [MODEL_NAME] during the window below.

Date:            [DATE]
Window:          [START_TIME] - [END_TIME] [TIMEZONE]
Expected impact: [DOWNTIME_MINUTES] minutes of increased latency
Affected APIs:   [ENDPOINT_LIST]

Reason for the change:
[REASON, e.g. retraining on data up to DATE to correct observed drift]

What changes for you:
- Response format: [UNCHANGED / SEE_DETAILS]
- Expected quality: [EXPECTED_METRIC_CHANGE]
- Cost per request: [COST_CHANGE]

Rollback plan: the current model version [CURRENT_VERSION] remains
available and can be restored within [ROLLBACK_MINUTES] minutes.

Please reply by [DEADLINE] if this window conflicts with a critical
activity on your side.

Best regards,
[YOUR_NAME]
```

### 4.3 Status report

```text
Subject: [EXPERIMENT REPORT] [EXPERIMENT_NAME] - week [WEEK_NUMBER]

Hi [MANAGER_NAME],

Summary of the [EXPERIMENT_NAME] experiment for [DATE_RANGE].

Goal
[ONE_SENTENCE_GOAL]

Results (held-out test set, [SAMPLE_COUNT] examples)
- Baseline [BASELINE_NAME]: [METRIC] = [BASELINE_VALUE]
- New approach:             [METRIC] = [NEW_VALUE]  ([DELTA])
- Latency p95:              [BASELINE_MS] ms -> [NEW_MS] ms
- Cost per 1,000 requests:  [BASELINE_COST] -> [NEW_COST]

Trade-off
[WHAT_WE_GAIN] at the cost of [WHAT_WE_LOSE]

Resources used
- Training time:    [HOURS] hours on [GPU_COUNT] x [GPU_TYPE]
- GPU utilization:  [PERCENT]%
- Estimated spend:  [AMOUNT]

Known limitations
- [LIMITATION_1]
- [LIMITATION_2]

Recommendation
[SHIP / ITERATE / STOP] because [REASON]

Next steps
- [NEXT_STEP_1] - owner [NAME], due [DATE]
- [NEXT_STEP_2] - owner [NAME], due [DATE]

Best regards,
[YOUR_NAME]
```

### 4.4 Access request

```text
Subject: [ACCESS REQUEST] GPU quota and dataset access for [PROJECT_NAME]

Hi [APPROVER_NAME],

I would like to request the following resources for [PROJECT_NAME].

Requested by: [YOUR_NAME], [TEAM]
Business need: [BUSINESS_JUSTIFICATION]

Compute
- GPU type and count: [GPU_COUNT] x [GPU_TYPE]
- Duration:           [START_DATE] to [END_DATE]
- Estimated cost:     [AMOUNT]
- Expected usage:     [PERCENT]% average utilization

Data
- Dataset:       [DATASET_NAME]
- Access level:  [READ_ONLY / READ_WRITE]
- Contains PII:  [YES/NO]
- Handling:      data stays in [REGION] and is deleted after [DATE]

Controls
- Auto-shutdown after [HOURS] hours of inactivity
- Spend alert at [PERCENT]% of the approved budget

Could you approve or comment by [DEADLINE]? I am happy to walk through
the plan in a short call if that is easier.

Best regards,
[YOUR_NAME]
```

### 4.5 Resolution confirmation

```text
Subject: [RESOLVED] [INCIDENT_ID] - [MODEL_NAME] output quality

Dear all,

The incident affecting [SERVICE_NAME] has been resolved.

Incident ID:    [INCIDENT_ID]
Detected at:    [DETECTION_TIME]
Resolved at:    [RESOLUTION_TIME]
Total duration: [DURATION]

Root cause
[ROOT_CAUSE, e.g. preprocessing mismatch between the training pipeline
and the serving path: HTML tags were stripped during training but passed
through at inference time]

Resolution
[WHAT_WAS_DONE, e.g. aligned preprocessing in both paths and redeployed
model version X after a full evaluation run]

Verification
- [METRIC] back to [VALUE] on the reference set
- [SAMPLE_COUNT] production samples reviewed manually, all correct

Preventive actions
- [ACTION_1] - owner [NAME], due [DATE]
- [ACTION_2] - owner [NAME], due [DATE]

Thank you for reporting the issue and for your patience.

Best regards,
[YOUR_NAME]
```

---

## 5. Bài tập thực hành (Practice Exercises)

### 5.1 Điền từ vào chỗ trống (10 câu)

Từ gợi ý: *baseline, inference, overfitting, hallucination, embedding, fine-tuning, trade-off, drift, epoch, utilization*

1. Validation loss increased while training loss kept falling, which is a clear sign of ________.
2. Our ________ is simple keyword search, and any new approach must beat it.
3. ________ latency must stay under 800 ms or the chat feels sluggish.
4. The answer sounded confident but the clause does not exist, so it was a ________.
5. We store one ________ per chunk in the vector database.
6. ________ on 5,000 real support tickets made the tone much more consistent.
7. The ________ here is 200 ms more latency for 6% better accuracy.
8. We monitor for ________ so we know when live data no longer matches the training data.
9. The loss stopped improving after the third ________, so we saved that checkpoint.
10. GPU ________ was only 35%, so the bottleneck is the data loader, not the model.

### 5.2 Matching thuật ngữ ↔ định nghĩa (10 cặp)

| # | Term | | Letter | Definition |
| --- | --- | --- | --- | --- |
| 1 | RAG | | A | A saved snapshot of model weights |
| 2 | Token | | B | Of the real positives, how many the model found |
| 3 | Checkpoint | | C | Feeding retrieved documents to an LLM before it answers |
| 4 | Recall | | D | A setting chosen before training, such as learning rate |
| 5 | Hyperparameter | | E | The smallest text unit an LLM processes |
| 6 | MLOps | | F | The maximum number of tokens a model can read at once |
| 7 | Context window | | G | Practices for deploying and operating models reliably |
| 8 | Dataset | | H | Data held back and used only for the final measurement |
| 9 | Test set | | I | The collection of examples used to train or test |
| 10 | Precision | | J | Of the items predicted positive, how many are right |

### 5.3 Viết lại câu dùng từ cho trước (5 câu)

1. "The model is better now." → viết lại có số liệu, dùng **outperforms the baseline by**.
2. "It's impossible in two weeks." → viết lại mang tính xây dựng, dùng **a middle option would be**.
3. "The AI just made that up." → viết lại chuyên nghiệp, dùng **hallucination**.
4. "We need more GPUs." → viết lại trang trọng, dùng **allocate additional**.
5. "It's faster but less accurate." → viết lại rõ ràng, dùng **trade-off**.

### 5.4 Role-play

*Bạn là AI engineer. Đồng nghiệp đóng vai giám đốc vận hành muốn dùng LLM tự động duyệt đơn hoàn tiền của khách hàng, không cần người kiểm tra.*

Nhiệm vụ của bạn trong 8 lượt trao đổi:
1. Hỏi rõ mục tiêu kinh doanh và chỉ số nào quan trọng nhất.
2. Nêu ít nhất hai giới hạn kỹ thuật bằng ngôn ngữ phi kỹ thuật.
3. Đưa con số cụ thể từ đánh giá (kể cả khi là ước tính, phải nói rõ là ước tính).
4. Đề xuất phương án có người kiểm tra ở phần rủi ro cao.
5. Kết thúc bằng một bước tiếp theo rõ ràng, có mốc thời gian.

<details>
<summary>Đáp án</summary>

**5.1 Điền từ**
1. overfitting — 2. baseline — 3. Inference — 4. hallucination — 5. embedding — 6. Fine-tuning — 7. trade-off — 8. drift — 9. epoch — 10. utilization

**5.2 Matching**
1-C, 2-E, 3-A, 4-B, 5-D, 6-G, 7-F, 8-I, 9-H, 10-J

**5.3 Viết lại câu** (gợi ý, các cách diễn đạt tương đương đều chấp nhận được)
1. "The fine-tuned model outperforms the baseline by 7 points on the held-out test set."
2. "Two weeks is not realistic for a full launch, but a middle option would be an internal beta in two weeks and a customer release in week four."
3. "That output is a hallucination: the model produced a confident answer that is not supported by any source."
4. "Could we allocate additional GPU capacity, specifically two A100s for the next two weeks?"
5. "There is a trade-off: the smaller model is roughly twice as fast, but accuracy drops by about four points."

**5.4 Role-play — mẫu mở đầu**
- "Before we design this, what matters more to you: approving refunds faster, or never approving a wrong one?"
- "Two limitations to keep in mind. First, the model predicts likely text, it does not verify facts. Second, it stays confident even when it is wrong."
- "On our evaluation set of 300 past cases, the model agreed with the human decision 89% of the time. That is an estimate on historical data, not live traffic."
- "I'd suggest full automation below [amount], and human review above it, plus review for any case flagged as unusual."
- "If you agree, I'll run a two-week shadow test where the model decides but a human still approves, and I'll send you the comparison on [date]."

</details>
