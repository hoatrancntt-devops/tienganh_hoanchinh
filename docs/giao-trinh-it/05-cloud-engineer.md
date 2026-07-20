# Cloud Engineer — Tiếng Anh cho Kỹ sư đám mây

Tài liệu này dành cho kỹ sư vận hành hạ tầng trên **Azure**, **AWS** hoặc GCP: người viết **Terraform**, quản lý **Kubernetes**, chạy migration, và phải giải trình chi phí với sếp hoặc khách hàng nước ngoài.
Dùng khi bạn cần viết email xin duyệt kế hoạch migration, báo cáo **downtime**, thương lượng **SLA**, hoặc trình bày phương án **cost optimization** trong cuộc họp.
Trình độ mục tiêu: B1–B2. Mọi câu ví dụ đều lấy từ tình huống làm việc thật.

**Phát âm hay sai (người Việt lưu ý):**
- **Azure** — /ˈæʒər/ ("A-zhơ"), KHÔNG đọc "a-diu-rờ". Trọng âm ở âm đầu.
- **deploy** — /dɪˈplɔɪ/, trọng âm ở âm **sau**: "đi-PLOI", không phải "ĐI-ploi".
- **provision** — /prəˈvɪʒən/ ("prơ-VI-zhần"), chữ *s* đọc như /ʒ/, không đọc "prô-vi-sần".
- **availability** — /əˌveɪləˈbɪləti/ — 6 âm tiết, trọng âm chính ở "BIL". Đọc chậm lại: "ơ-vây-lơ-BI-lơ-ti".
- **Kubernetes** — /ˌkuːbərˈnetiːs/ ("cu-bơ-NÉT-tiz"), 4 âm tiết. Viết tắt **K8s** đọc là "kates".

---

## 1. Từ vựng cốt lõi (Core Vocabulary)

| Term | Definition (EN) | Example Sentence | Tiếng Việt |
|---|---|---|---|
| provision | To set up and allocate cloud resources | We'll **provision** three new VMs in the West Europe region tonight. | cấp phát, khởi tạo tài nguyên |
| deploy | To release code or infrastructure into an environment | We **deploy** to staging first, then to production on Friday. | triển khai |
| workload | An application or service running on infrastructure | This **workload** needs at least 8 GB of memory per node. | tải công việc, ứng dụng chạy trên hệ thống |
| region | A geographic location where a cloud provider hosts data centers | Latency dropped after we moved the API to the Singapore **region**. | vùng (địa lý) |
| availability zone | An isolated data center inside a region | Spread the nodes across three **availability zones** for resilience. | vùng sẵn sàng (AZ) |
| high availability (HA) | Design that keeps a service running despite failures | Our **high availability** setup survived the AZ outage last month. | tính sẵn sàng cao |
| failover | Automatic switch to a standby system when the primary fails | The database **failover** completed in 40 seconds. | chuyển đổi dự phòng |
| scale out / scale in | To add or remove instances horizontally | Traffic spiked, so the cluster **scaled out** to twelve pods. | mở rộng / thu hẹp theo chiều ngang |
| scale up / scale down | To increase or decrease the size of a single instance | We **scaled up** the SQL instance from 4 to 8 vCPUs. | nâng / hạ cấu hình một máy |
| autoscaling | Automatic adjustment of capacity based on demand | **Autoscaling** kicks in when CPU stays above 70% for five minutes. | tự động co giãn |
| Infrastructure as Code (IaC) | Managing infrastructure through version-controlled files | All our subnets are defined as **Infrastructure as Code** in Terraform. | hạ tầng dưới dạng mã |
| Terraform state | The file that tracks what Terraform has created | Never edit the **Terraform state** by hand — use `terraform import`. | tệp trạng thái Terraform |
| drift | Difference between actual infrastructure and the code | `terraform plan` showed **drift** because someone changed it in the portal. | lệch cấu hình |
| container | A lightweight, isolated package of an app and its dependencies | Each **container** runs the same image in dev and production. | container |
| image | A read-only template used to create containers | Please push the new Docker **image** to the registry with a version tag. | ảnh container |
| orchestration | Automated management of containers across many machines | Kubernetes handles **orchestration**, so we don't place pods manually. | điều phối |
| pod | The smallest deployable unit in Kubernetes | The **pod** keeps restarting because the liveness probe fails. | pod |
| node | A worker machine in a Kubernetes cluster | We added two **nodes** to handle the Black Friday load. | node, máy chủ trong cluster |
| namespace | A logical partition inside a Kubernetes cluster | Deploy the test build into the `staging` **namespace** only. | không gian tên |
| migration | Moving systems or data from one platform to another | The on-premises to Azure **migration** is planned for three weekends. | di chuyển hệ thống |
| lift and shift | Moving an app to the cloud with minimal changes | We'll start with **lift and shift**, then refactor next quarter. | chuyển nguyên trạng |
| cutover | The moment traffic switches to the new environment | **Cutover** is scheduled for Saturday 02:00 ICT. | thời điểm chuyển đổi |
| rollback | Returning to the previous working version | If error rates exceed 2%, we trigger an automatic **rollback**. | quay lui phiên bản cũ |
| downtime | Period when a service is unavailable | Expected **downtime** is under fifteen minutes. | thời gian ngừng dịch vụ |
| SLA (Service Level Agreement) | A contractual uptime and support commitment | Our **SLA** guarantees 99.9% monthly uptime. | cam kết chất lượng dịch vụ |
| cost optimization | Reducing cloud spend without hurting performance | This **cost optimization** review saved us $4,200 per month. | tối ưu chi phí |
| reserved instance | Prepaid capacity bought at a discount for 1–3 years | Switching to **reserved instances** cut compute cost by 38%. | máy chủ trả trước |
| rightsizing | Matching instance size to actual usage | **Rightsizing** removed eight oversized VMs nobody was using. | chuẩn hoá kích thước tài nguyên |
| egress cost | The charge for data leaving the cloud provider's network | Most of the bill increase came from **egress costs**, not compute. | phí truyền dữ liệu ra ngoài |
| load balancer | A service distributing traffic across instances | Add the new node to the **load balancer** pool after the health check passes. | bộ cân bằng tải |
| blue-green deployment | Running two environments and switching traffic between them | **Blue-green deployment** gives us a rollback in one second. | triển khai xanh–lam |

> **Lưu ý người Việt hay sai:** *deploy* là động từ, danh từ là **deployment** — nói "the deploy" nghe rất "Vietnamese English". Nói **"the deployment"**.
> Tương tự, đừng nói "open a new server"; dùng **"provision"** hoặc **"spin up"** a server.

---

## 2. Mẫu câu giao tiếp (Common Phrases)

### Báo cáo (Reporting)

1. **Formal** — "The migration completed successfully with 12 minutes of downtime, well within our agreed window." → *Migration đã xong, downtime 12 phút, nằm trong khung đã thống nhất.*
2. **Formal** — "As of this morning, all workloads are running in the new region and monitoring shows normal traffic." → *Tính đến sáng nay, toàn bộ workload đã chạy ở region mới, giám sát cho thấy lưu lượng bình thường.*
3. **Formal** — "Monthly cloud spend came in at $18,400, which is 9% below the forecast." → *Chi phí cloud tháng này là 18.400 USD, thấp hơn dự báo 9%.*
4. **Informal** — "Cluster's stable now — all pods green for the last two hours." → *Cluster ổn rồi, pod xanh hết hai tiếng nay.*
5. **Informal** — "Heads up: the staging deployment is done, prod is next." → *Báo trước: staging xong rồi, tới lượt prod.*

### Yêu cầu (Requesting)

6. **Formal** — "Could you please approve the migration plan attached so we can book the maintenance window?" → *Anh/chị duyệt giúp kế hoạch migration đính kèm để chúng tôi đặt lịch bảo trì.*
7. **Formal** — "We would like to request an additional budget of $600 per month for the reserved instances." → *Chúng tôi xin thêm 600 USD/tháng cho reserved instance.*
8. **Formal** — "Would it be possible to schedule the cutover for the weekend to minimise business impact?" → *Có thể xếp lịch cutover vào cuối tuần để giảm ảnh hưởng không?*
9. **Informal** — "Can you bump the quota for us? We're hitting the vCPU limit." → *Nâng quota giúp bọn mình nhé, đang chạm trần vCPU.*
10. **Informal** — "Mind reviewing my Terraform PR before standup?" → *Review giúp PR Terraform trước standup nhé?*

### Giải thích (Explaining)

11. **Formal** — "The cost increase is driven mainly by egress traffic, not by compute usage." → *Chi phí tăng chủ yếu do lưu lượng đi ra, không phải do compute.*
12. **Formal** — "To put it simply, we are paying for capacity we reserved but never used." → *Nói đơn giản, chúng ta đang trả tiền cho phần đã đặt trước nhưng không dùng.*
13. **Formal** — "High availability means the service stays up even if one data center fails; it does not mean zero downtime." → *HA nghĩa là dịch vụ vẫn chạy khi một trung tâm dữ liệu hỏng, không có nghĩa là không bao giờ gián đoạn.*
14. **Informal** — "Basically, autoscaling adds pods when CPU goes over 70%." → *Về cơ bản, autoscaling thêm pod khi CPU vượt 70%.*
15. **Informal** — "Think of Terraform state as the source of truth for what actually exists." → *Coi Terraform state như nguồn sự thật về những gì đang tồn tại.*

### Xử lý sự cố (Troubleshooting)

16. **Formal** — "We have identified the root cause and are applying a fix; I will send an update in thirty minutes." → *Chúng tôi đã xác định nguyên nhân gốc và đang xử lý, 30 phút nữa sẽ cập nhật.*
17. **Formal** — "We are initiating a rollback to the previous stable release as a precaution." → *Chúng tôi đang rollback về bản ổn định trước đó để phòng ngừa.*
18. **Informal** — "Give me five minutes, I'm checking the load balancer health probes." → *Cho mình 5 phút, đang kiểm tra health probe của load balancer.*
19. **Informal** — "It's not the app — the node ran out of disk." → *Không phải lỗi app, node hết dung lượng đĩa.*
20. **Informal** — "Let's roll back first and investigate after. Users come first." → *Rollback trước, điều tra sau. Người dùng là ưu tiên.*

> **Mẹo:** trong sự cố, người Việt hay nói "I will try to fix" — nghe thiếu tự tin. Dùng **"We are applying a fix now"** hoặc **"We have a workaround in place"**.

---

## 3. Tình huống thực tế (Real-world Scenarios)

### Scenario 1 — Giải trình hoá đơn cloud tăng vọt với sếp

*Bối cảnh: Hoá đơn Azure tháng này tăng 40%. Giám đốc tài chính (CFO) muốn biết lý do.*

**CFO:** Our Azure bill jumped 40% this month. What happened?
**Cloud Engineer:** I've broken it down. About 70% of the increase is **egress traffic** from the new reporting feature.
**CFO:** Meaning what, in plain terms?
**Cloud Engineer:** Every time a customer exports a report, we send the file out of Azure, and we pay per gigabyte leaving the network.
**CFO:** Is that avoidable?
**Cloud Engineer:** Partly. If we cache the reports and compress them, we can cut that traffic by roughly half.
**CFO:** And the remaining 30%?
**Cloud Engineer:** Two oversized VMs from the load test in May. Nobody shut them down. I've already scheduled them for deletion.
**CFO:** Good. Can you give me a number for next month?
**Cloud Engineer:** With compression and the cleanup, I expect us to land back around $19,000, and I'll send a weekly cost report so there are no surprises.

### Scenario 2 — Xin duyệt kế hoạch migration

*Bối cảnh: Kỹ sư trình bày kế hoạch chuyển hệ thống on-premises lên Azure cho quản lý dự án.*

**Engineer:** I'd like to walk you through the migration plan before we commit to a date.
**PM:** Go ahead. What's the approach?
**Engineer:** Phase one is **lift and shift** — we move the servers as they are, no code changes. Phase two, we refactor into containers.
**PM:** Why not do it all at once?
**Engineer:** Risk. Lift and shift is reversible. If we refactor at the same time and something breaks, we won't know which change caused it.
**PM:** How much downtime for phase one?
**Engineer:** We estimate under two hours, on a Saturday night. The database sync runs in advance, so the **cutover** itself is short.
**PM:** What if it fails?
**Engineer:** We keep the on-premises environment running for two weeks. **Rollback** is just a DNS change back — about five minutes.
**PM:** That's reassuring. Send me the plan and I'll approve it today.
**Engineer:** Thanks. I'll include the rollback criteria so everyone knows when we pull the trigger.

### Scenario 3 — Thông báo downtime cho khách hàng

*Bối cảnh: Kỹ sư gọi cho khách hàng để thông báo cửa sổ bảo trì có gián đoạn dịch vụ.*

**Engineer:** I'm calling about the maintenance window this Sunday. There will be a short service interruption.
**Client:** How short is "short"?
**Engineer:** We estimate ten to fifteen minutes, between 2:00 and 4:00 AM your time.
**Client:** Our night shift uses the system for stock counts.
**Engineer:** Understood. Would 4:00 to 6:00 AM work better, or is there a quieter window?
**Client:** Sunday between 5:00 and 6:00 is our quietest hour.
**Engineer:** Then let's book 5:00 AM. I'll confirm in writing today.
**Client:** And if it takes longer than fifteen minutes?
**Engineer:** If we're not done by 5:30, we roll back and reschedule. You'll have the system back either way.
**Client:** That works. Please send the notice to our operations mailbox.

### Scenario 4 — Thảo luận nội bộ về autoscaling

*Bối cảnh: Hai kỹ sư trao đổi trong standup về việc cluster bị quá tải giờ cao điểm.*

**Engineer A:** We got paged twice last night. Pods were pending because there weren't enough nodes.
**Engineer B:** So the cluster autoscaler didn't react fast enough?
**Engineer A:** It reacted, but node provisioning takes about three minutes. The spike lasted four.
**Engineer B:** Could we keep a warm buffer? Two spare nodes always running?
**Engineer A:** That costs roughly $180 a month. Cheaper than another incident, honestly.
**Engineer B:** Agreed. Let's also lower the scale-out threshold from 70% to 60% CPU.
**Engineer A:** Good. I'll open a Terraform PR for both changes this morning.
**Engineer B:** Tag me as reviewer. And please add a comment explaining why the buffer exists — otherwise someone will delete it in six months.

### Scenario 5 — Thảo luận SLA với khách hàng

*Bối cảnh: Khách hàng muốn cam kết uptime 99.99%. Kỹ sư giải thích chi phí đi kèm.*

**Client:** We'd like the SLA raised to 99.99% uptime.
**Engineer:** That's achievable, but I want to be transparent about what it requires.
**Client:** Please explain.
**Engineer:** 99.9% allows about 43 minutes of downtime per month. 99.99% allows only four minutes.
**Client:** And the difference in setup?
**Engineer:** We'd need a **multi-region** deployment with an active standby and automatic **failover**. That roughly doubles the infrastructure cost.
**Client:** What's the number?
**Engineer:** Around an extra $3,000 per month, plus a one-off setup effort of about three weeks.
**Client:** Let me discuss it internally. Can you send a comparison document?
**Engineer:** Of course. I'll include both options side by side with the cost and the recovery time for each.

### Scenario 6 — Sự cố sau khi deploy, quyết định rollback

*Bối cảnh: Sau khi deploy phiên bản mới, tỉ lệ lỗi tăng. Team quyết định trong 10 phút.*

**On-call:** Error rate is at 6% since the deployment fifteen minutes ago. Normal is under 0.5%.
**Team Lead:** Do we know the cause?
**On-call:** Not yet. Logs show timeouts to the payment service.
**Team Lead:** Our threshold for rollback is 2%. We're well past it.
**On-call:** Confirmed. Starting the rollback now.
**Team Lead:** Post in the incident channel so support knows.
**On-call:** Done. Rollback finished — error rate is back to 0.4%.
**Team Lead:** Good. Now we investigate properly. Let's schedule a **post-mortem** tomorrow, blameless, focused on why the staging tests didn't catch it.

### Scenario 7 — Onboard đồng nghiệp mới vào Terraform

*Bối cảnh: Kỹ sư senior hướng dẫn thành viên mới quy tắc làm việc với IaC.*

**Senior:** Rule number one: never change anything in the Azure portal directly.
**Junior:** Even for a quick fix?
**Senior:** Especially for a quick fix. It causes **drift** — the code and reality stop matching.
**Junior:** How would I notice the drift?
**Senior:** `terraform plan` will show changes you didn't write. That's your warning sign.
**Junior:** What do I do then?
**Senior:** Bring the change into code and re-apply, or revert it manually. Don't ignore it.
**Junior:** And the state file?
**Senior:** It lives in a remote backend with locking, so two people can't apply at once. Never download and edit it by hand.
**Junior:** Understood. So every change goes through a pull request?
**Senior:** Every single one. That's how we keep an audit trail.

---

## 4. Email mẫu (Email Templates)

### 4.1 Incident notification

```text
Subject: [INCIDENT] Degraded performance on [Service Name] — investigating

Dear [Customer / Team],

We are currently investigating degraded performance affecting [service name]
in the [region] region. The issue started at approximately [HH:MM] [timezone].

Impact: [e.g. slower API responses, intermittent 502 errors]
Affected users: [scope, e.g. customers in APAC]
Current status: Our engineering team has identified the likely cause and is
applying a mitigation.

We will send the next update by [HH:MM] [timezone], or sooner if the situation
changes. We apologise for the disruption.

Best regards,
[Your Name]
Cloud Engineering Team | [Company]
```

### 4.2 Maintenance announcement

```text
Subject: Scheduled maintenance — [Service Name] on [Date], [Start]–[End] [timezone]

Dear [Customer / Team],

We will perform scheduled maintenance on [service name] to [purpose,
e.g. upgrade the Kubernetes cluster to version 1.30].

Window:         [Date], [Start time] – [End time] [timezone]
Expected impact: [e.g. up to 15 minutes of downtime during the cutover]
Rollback plan:   If the upgrade is not complete by [time], we will roll back
                 to the current version and reschedule.

No action is required on your side. If this window conflicts with a critical
business activity, please reply by [deadline] and we will reschedule.

Best regards,
[Your Name]
Cloud Engineering Team | [Company]
```

### 4.3 Status report

```text
Subject: Weekly cloud status report — week [NN], [Month Year]

Hi [Manager / Stakeholder],

Here is the cloud infrastructure summary for week [NN].

Availability:    [e.g. 99.97%] against an SLA target of [99.9%]
Incidents:       [number] ([severity breakdown]); all resolved
Cloud spend:     [$amount] month-to-date, [x]% [above/below] forecast
Key changes:     - [e.g. Migrated reporting workload to the Singapore region]
                 - [e.g. Enabled autoscaling on the API cluster]
Next week:       - [planned work item 1]
                 - [planned work item 2]
Risks / asks:    [e.g. Approval needed for reserved instance purchase by Friday]

Happy to walk through any item in more detail.

Best regards,
[Your Name]
```

### 4.4 Access request

```text
Subject: Access request — [Role/Permission] on [Subscription/Project]

Hi [Approver Name],

I would like to request access to [resource / subscription / cluster] for
[purpose, e.g. troubleshooting the production ingress controller].

Requested role:  [e.g. Contributor on subscription "prod-sea"]
Justification:   [why the current role is insufficient]
Duration:        [e.g. 7 days / until ticket TICKET-1234 is closed]
Requested by:    [Your Name], [Team]

I am happy to use just-in-time elevation instead of a permanent assignment if
that is preferred. Please let me know if you need any further information.

Best regards,
[Your Name]
```

### 4.5 Resolution confirmation

```text
Subject: [RESOLVED] [Service Name] performance issue — [Date]

Dear [Customer / Team],

The issue affecting [service name] has been fully resolved as of [HH:MM]
[timezone]. All services are operating normally and monitoring confirms
metrics are back within expected ranges.

Duration:     [start time] – [end time] ([total minutes])
Root cause:   [brief, factual description]
Resolution:   [what was done, e.g. rolled back release 2.14.0 and increased
              the connection pool limit]
Prevention:   [follow-up actions, e.g. added an integration test covering this
              path; alert threshold lowered to catch it earlier]

A full post-incident report will be shared by [date]. Thank you for your
patience.

Best regards,
[Your Name]
Cloud Engineering Team | [Company]
```

---

## 5. Bài tập thực hành (Practice Exercises)

### A. Điền từ vào chỗ trống (10 câu)

Từ gợi ý: *provision, downtime, rollback, drift, autoscaling, egress, cutover, failover, rightsizing, high availability*

1. We need to ____ two additional nodes before the load test starts.
2. Expected ____ for Sunday's maintenance is under fifteen minutes.
3. If the error rate goes above 2%, we trigger an automatic ____.
4. `terraform plan` shows ____ because someone edited the resource in the portal.
5. ____ adds new pods automatically when CPU usage stays above 70%.
6. Most of the bill increase came from ____ traffic, not from compute.
7. The ____ is scheduled for Saturday at 02:00, when traffic is lowest.
8. Database ____ completed in 40 seconds, so users barely noticed.
9. A ____ review removed eight oversized VMs that nobody was using.
10. Our ____ design keeps the service running even if one availability zone fails.

### B. Nối thuật ngữ với định nghĩa (10 cặp)

| # | Term | | Definition |
|---|---|---|---|
| 1 | pod | A | Prepaid capacity bought at a discount for 1–3 years |
| 2 | namespace | B | Moving an app to the cloud with minimal code changes |
| 3 | reserved instance | C | The smallest deployable unit in Kubernetes |
| 4 | lift and shift | D | A contractual uptime and support commitment |
| 5 | SLA | E | A read-only template used to create containers |
| 6 | image | F | A logical partition inside a Kubernetes cluster |
| 7 | load balancer | G | Managing infrastructure through version-controlled files |
| 8 | IaC | H | An isolated data center inside a region |
| 9 | availability zone | I | Running two environments and switching traffic between them |
| 10 | blue-green deployment | J | A service that distributes traffic across instances |

### C. Viết lại câu dùng từ cho trước (5 câu)

1. We will make new servers for the test. *(provision)*
2. The system will not work for about ten minutes. *(downtime)*
3. We will go back to the old version if there is a problem. *(roll back)*
4. The cost is high because a lot of data leaves the cloud. *(egress)*
5. The cluster adds more machines by itself when it is busy. *(autoscaling)*

### D. Role-play

**Tình huống:** Bạn là Cloud Engineer. Khách hàng vừa nhận hoá đơn tháng tăng 35% và đang khó chịu. Nguyên nhân: (1) một môi trường test không ai tắt sau dự án, (2) lưu lượng egress tăng do tính năng xuất báo cáo mới. Bạn có phương án tiết kiệm khoảng 30% nhưng cần khách duyệt việc mua reserved instance 1 năm.

**Nhiệm vụ:** Đóng vai một cuộc gọi 8 lượt trao đổi. Bạn phải: thừa nhận vấn đề mà không đổ lỗi, giải thích nguyên nhân bằng ngôn ngữ phi kỹ thuật, đưa ra hai lựa chọn kèm con số, và chốt bước tiếp theo có thời hạn cụ thể.

---

<details>
<summary>Đáp án</summary>

**A. Điền từ**

1. provision
2. downtime
3. rollback
4. drift
5. Autoscaling
6. egress
7. cutover
8. failover
9. rightsizing
10. high availability

**B. Matching**

1–C, 2–F, 3–A, 4–B, 5–D, 6–E, 7–J, 8–G, 9–H, 10–I

**C. Viết lại câu (gợi ý)**

1. We will **provision** new servers for the test environment.
2. Expected **downtime** is approximately ten minutes.
3. We will **roll back** to the previous stable version if we hit a problem.
4. The cost is high because of **egress** charges for data leaving the cloud.
5. **Autoscaling** adds more nodes automatically when the load increases.

**D. Role-play — khung câu tham khảo**

- Mở đầu: "Thanks for raising this. I've looked at the breakdown and I can explain every line."
- Thừa nhận: "You're right that the increase is significant, and part of it is avoidable."
- Giải thích: "About 20% comes from a test environment that stayed running after the project ended. That's on us, and it's already shut down."
- Giải thích tiếp: "The rest is egress — we pay per gigabyte of data leaving the cloud, and the new report export feature moves a lot of data."
- Lựa chọn 1: "We can compress and cache the reports. That cuts egress by about half, at no extra cost, and takes two weeks."
- Lựa chọn 2: "If you also approve a one-year reserved instance purchase, we save a further 20% on compute — roughly $2,400 over the year."
- Chốt: "So option one alone gets you back near the old bill; option one plus two puts you below it."
- Bước tiếp theo: "I'll send the comparison today. Could you confirm by Friday so the reservation starts next billing cycle?"

</details>
