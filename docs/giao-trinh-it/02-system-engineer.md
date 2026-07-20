# System Engineer / Quản trị hệ thống — Tiếng Anh giao tiếp nghề nghiệp

Tài liệu này dành cho **System Engineer**, **System Administrator**, **Infrastructure Engineer** người Việt làm việc với đối tác, vendor hoặc đồng nghiệp nước ngoài.
Dùng khi bạn phải thông báo **maintenance window**, báo cáo **downtime**, trình bày **rollback plan**, trao đổi với hỗ trợ kỹ thuật của VMware/Veeam/NAKIVO, hoặc bảo vệ đề xuất nâng cấp hạ tầng trước quản lý nước ngoài.
Trình độ mục tiêu: **B1–B2**. Trọng tâm là nói về **rủi ro, thời gian và trách nhiệm** một cách chính xác — đây là chỗ tiếng Anh sai sẽ gây hậu quả thật.

---

## 1. Từ vựng cốt lõi (Core Vocabulary)

| Term | Definition (EN) | Example Sentence | Tiếng Việt |
|---|---|---|---|
| **hypervisor** | Software that runs and manages virtual machines | "We run **Proxmox** as the hypervisor on the branch cluster and **ESXi** at head office." | nền tảng ảo hoá |
| **host / node** | A physical server running virtual machines | "Node 3 is showing memory pressure — I'll migrate two VMs off it." | máy chủ vật lý / nút |
| **cluster** | A group of hosts working together for capacity and failover | "The three-node **Proxmox** cluster keeps quorum even if one host dies." | cụm máy chủ |
| **VM (virtual machine)** | A virtualised computer running on a host | "The VM has 16 vCPU and 64 GB of RAM allocated." | máy ảo |
| **datastore** | The storage where VM disks live | "The **vSphere** datastore is at 91% — that's our next problem." | kho lưu trữ |
| **snapshot** | A point-in-time image of a VM, used before risky changes | "Take a snapshot before patching, and delete it within 24 hours." | ảnh chụp trạng thái |
| **live migration / vMotion** | Moving a running VM between hosts with no downtime | "I'll **vMotion** the database VM to host 2 before the reboot." | di chuyển máy ảo khi đang chạy |
| **failover** | Automatic switch to a standby system when the primary fails | "Failover to the secondary site took 90 seconds." | chuyển đổi dự phòng |
| **high availability (HA)** | Design that keeps a service running through single failures | "HA is enabled, so a host failure restarts the VMs elsewhere." | tính sẵn sàng cao |
| **backup job** | A scheduled task that copies data for recovery | "The **Veeam** backup job failed twice last night with a VSS error." | tác vụ sao lưu |
| **restore / recovery** | Bringing data or a system back from backup | "We ran a test restore from **NAKIVO** and it completed in 22 minutes." | phục hồi |
| **RPO** (Recovery Point Objective) | How much data loss is acceptable, measured in time | "Our RPO is one hour, so we replicate hourly." | mức mất dữ liệu chấp nhận được |
| **RTO** (Recovery Time Objective) | How fast a service must be back after failure | "The RTO for the ERP is four hours." | thời gian phục hồi mục tiêu |
| **retention** | How long backups are kept before deletion | "We keep 14 daily, 4 weekly and 12 monthly restore points." | thời gian lưu giữ |
| **patching** | Applying security and bug fixes to systems | "**Windows Server** patching runs on the second Tuesday each month." | vá lỗi / cập nhật |
| **maintenance window** | The agreed time slot when disruptive work may happen | "Our maintenance window is Saturday 22:00 to Sunday 02:00." | khung giờ bảo trì |
| **downtime** | The period a service is unavailable | "Total downtime was eleven minutes, within the approved window." | thời gian ngừng dịch vụ |
| **rollback plan** | The documented way to undo a change if it fails | "If the upgrade fails, the rollback plan is to restore last night's snapshot." | phương án quay lui |
| **change request (CR)** | A formal request to approve a planned change | "The change request needs approval 48 hours in advance." | yêu cầu thay đổi |
| **monitoring** | Continuous automated checking of system health | "Monitoring alerted us before any user noticed." | giám sát |
| **alert / threshold** | A notification triggered when a metric crosses a limit | "Set the disk alert threshold at 85%, not 95% — we need reaction time." | cảnh báo / ngưỡng |
| **baseline** | Normal measured behaviour, used for comparison | "CPU is 40% above baseline since the deployment." | mức chuẩn |
| **capacity planning** | Forecasting future resource needs | "Capacity planning says we run out of storage in five months." | hoạch định năng lực |
| **provisioning** | Allocating compute, storage or network resources | "Thin provisioning saves space but you must watch actual usage." | cấp phát tài nguyên |
| **bottleneck** | The component limiting overall performance | "The bottleneck is storage IOPS, not CPU." | điểm nghẽn |
| **IOPS / latency** | Storage operations per second / delay per operation | "Latency spikes to 40 ms during the backup window." | số thao tác I/O / độ trễ |
| **uptime / SLA** | Availability achieved / availability promised | "We delivered 99.95% uptime against a 99.9% SLA." | thời gian hoạt động / cam kết |
| **replication** | Copying data continuously to a second location | "Replication to the DR site runs every 15 minutes." | nhân bản dữ liệu |
| **DR (disaster recovery)** | The plan and site used after a major failure | "We test the DR plan twice a year." | khôi phục thảm hoạ |
| **post-mortem** | A blameless review written after a major incident | "The post-mortem is due within five working days." | báo cáo hậu sự cố |

> **Người Việt hay sai — phát âm & cách dùng:** `hypervisor` /ˈhaɪpərvaɪzər/ — trọng âm ở **hy-**. `ESXi` đọc từng chữ "E-S-X-i". `Veeam` đọc /viːm/ ("vim" dài), không phải "vi-am". `schedule` — Anh /ˈʃedjuːl/, Mỹ /ˈskedʒuːl/, chọn một và dùng nhất quán. **Chú ý ngữ pháp:** *downtime* là danh từ không đếm được → nói **"There was 20 minutes of downtime"**, không nói "a downtime". Tương tự với *"the server is **down**"* (tính từ) chứ không phải "the server is downtime".

---

## 2. Mẫu câu giao tiếp (Common Phrases)

### Báo cáo (Reporting)

1. **Formal** — "Total downtime was [11] minutes, which is within the approved maintenance window." *(Tổng thời gian ngừng là 11 phút, nằm trong khung bảo trì đã duyệt.)*
2. **Formal** — "All post-change validation checks passed and the system has been stable for 24 hours." *(Toàn bộ kiểm tra sau thay đổi đều đạt và hệ thống ổn định 24 giờ.)*
3. **Formal** — "We achieved 99.95% uptime this quarter against a target of 99.9%." *(Quý này đạt 99,95% so với mục tiêu 99,9%.)*
4. **Informal** — "Cluster's back to normal — all VMs migrated, no data loss." *(Cụm đã bình thường — máy ảo chuyển hết, không mất dữ liệu.)*
5. **Informal** — "Heads-up: the Veeam job failed again overnight. Same VSS error." *(Báo trước: job Veeam lại lỗi đêm qua, vẫn lỗi VSS cũ.)*

### Yêu cầu (Requesting)

6. **Formal** — "We would like to request a maintenance window on [DATE] between [START] and [END]." *(Chúng tôi xin đề nghị khung bảo trì ngày… từ… đến…)*
7. **Formal** — "Could you confirm whether this change requires CAB approval or can proceed as a standard change?" *(Anh/chị xác nhận thay đổi này cần duyệt CAB hay thuộc loại tiêu chuẩn?)*
8. **Formal** — "We need an additional 4 TB of storage to cover the next twelve months of growth." *(Chúng tôi cần thêm 4 TB dung lượng cho 12 tháng tới.)*
9. **Informal** — "Can you hold off on the deployment until I finish patching node 3?" *(Hoãn deploy đến khi mình vá xong node 3 nhé?)*
10. **Informal** — "Could you take a snapshot before you touch that VM?" *(Chụp snapshot trước khi động vào VM đó nhé?)*

### Giải thích (Explaining)

11. **Formal** — "The bottleneck is storage latency rather than CPU, so adding vCPU would not improve performance." *(Điểm nghẽn là độ trễ lưu trữ chứ không phải CPU, nên thêm vCPU sẽ không cải thiện.)*
12. **Formal** — "If the upgrade does not complete successfully, we will roll back to the pre-change snapshot; the rollback itself takes approximately 15 minutes." *(Nếu nâng cấp không thành công, chúng tôi quay lui về snapshot trước đó; việc quay lui mất khoảng 15 phút.)*
13. **Formal** — "The risk is low but not zero: the main exposure is that the database service does not restart cleanly after the patch." *(Rủi ro thấp nhưng không bằng không: nguy cơ chính là dịch vụ CSDL không khởi động lại sạch sau khi vá.)*
14. **Informal** — "In short: the disk filled up, backups stopped, nobody noticed for three days." *(Nói ngắn gọn: đĩa đầy, backup dừng, ba ngày không ai để ý.)*
15. **Informal** — "Think of replication as a copy, not a backup — if someone deletes a file, replication deletes it too." *(Hình dung replication là bản sao chứ không phải backup — ai xoá file thì bản sao cũng mất.)*

### Xử lý sự cố (Troubleshooting)

16. **Formal** — "We have isolated the issue to a single host and evacuated all production workloads from it." *(Chúng tôi đã khoanh vùng sự cố ở một host và đã chuyển toàn bộ tải sản xuất khỏi host đó.)*
17. **Formal** — "At this stage we are treating the storage controller firmware as the most likely cause, pending vendor confirmation." *(Hiện chúng tôi coi firmware bộ điều khiển lưu trữ là nguyên nhân khả dĩ nhất, chờ vendor xác nhận.)*
18. **Informal** — "Let's stop guessing and check the logs on the host itself." *(Đừng đoán nữa, xem log ngay trên host đi.)*
19. **Informal** — "It fixed itself after a reboot — that worries me more than if it hadn't." *(Reboot xong tự hết — điều đó còn đáng lo hơn là không hết.)*
20. **Formal** — "We are declaring the incident resolved and will circulate a post-mortem within five working days." *(Chúng tôi tuyên bố sự cố đã xử lý xong và sẽ gửi báo cáo hậu sự cố trong 5 ngày làm việc.)*

> **Lỗi giao tiếp nghiêm trọng nhất trong nghề này:** hứa chắc chắn khi bạn chưa chắc. Tránh **"No problem, it will work"**. Người phương Tây trong vận hành hạ tầng mong bạn nói rõ mức độ tin cậy: **"I'm confident, but I'll have a rollback ready"**, **"I can't guarantee that — here's what I do know"**. Nói *"I don't know yet, I'll confirm in 30 minutes"* là câu trả lời **chuyên nghiệp**, không phải câu trả lời yếu.

---

## 3. Tình huống thực tế (Real-world Scenarios)

### Kịch bản 1 — Xin duyệt maintenance window
*Bối cảnh: Kỹ sư hệ thống trình bày kế hoạch vá Windows Server với IT Manager người nước ngoài.*

- **Engineer:** I'd like approval for a maintenance window on Saturday, 22:00 to 02:00.
- **Manager:** What exactly are you doing?
- **Engineer:** Monthly security patching on twelve Windows Servers, plus a firmware update on the two ESXi hosts.
- **Manager:** What's the user impact?
- **Engineer:** The file server and ERP will be unavailable for roughly 30 minutes each. Everything else stays up because I'll vMotion the VMs between hosts.
- **Manager:** And if the firmware update goes wrong?
- **Engineer:** Rollback plan: I flash the previous firmware version, which takes about 20 minutes per host. I'll also have last night's Veeam restore point verified before I start.
- **Manager:** How confident are you?
- **Engineer:** Confident on the patching — we've done it eleven months in a row. The firmware is new to us, so I've scheduled it last, after everything else is confirmed working.
- **Manager:** Good approach. Approved. Send the announcement to all staff by Thursday.

### Kịch bản 2 — Báo cáo downtime ngoài kế hoạch
*Bối cảnh: Sáng thứ Hai, ERP sập 47 phút. Giám đốc muốn giải thích.*

- **Director:** I got twenty complaints before 9 a.m. What happened?
- **Engineer:** The ERP was down from 08:04 to 08:51 — 47 minutes. I want to give you the facts first, then the cause.
- **Director:** Go ahead.
- **Engineer:** The datastore hit 100% because a snapshot from Friday's testing was never deleted. It grew over the weekend and filled the volume, so the VMs paused.
- **Director:** So this was our own mistake.
- **Engineer:** Yes. It was ours. The snapshot should have been removed within 24 hours and it wasn't.
- **Director:** What did you do?
- **Engineer:** I deleted the snapshot, freed 380 GB, and the VMs resumed. No data was lost — the database recovered cleanly and I verified the last transactions.
- **Director:** And prevention?
- **Engineer:** Three changes: an alert at 85% instead of 95%, a weekly report of snapshots older than 24 hours, and snapshot deletion added to the change checklist. The post-mortem will be with you Wednesday.
- **Director:** Thank you for being straight about it.

### Kịch bản 3 — Backup job liên tục lỗi (thảo luận nội bộ)
*Bối cảnh: Hai kỹ sư trao đổi trong daily standup về job Veeam lỗi.*

- **Engineer A:** The Veeam job for the SQL server has failed four nights running. VSS timeout.
- **Engineer B:** Is it failing on every VM or just that one?
- **Engineer A:** Only the SQL VM. The other nine finish fine.
- **Engineer B:** Then it's probably the application-aware processing, not Veeam itself. How big is the database now?
- **Engineer A:** 1.4 TB, up from 900 GB in March.
- **Engineer B:** That's your problem. VSS is timing out because the freeze takes too long. Two options: extend the timeout, or switch that VM to a native SQL log backup and let Veeam do crash-consistent only.
- **Engineer A:** Which do you prefer?
- **Engineer B:** Native SQL backups. It's more work to set up but it gives us a 15-minute RPO instead of 24 hours. And right now we have four nights with no restore point, which is the real emergency.
- **Engineer A:** Agreed. I'll run a manual backup this morning first, then rebuild the job properly.
- **Engineer B:** Do that. And raise it as a risk in the weekly report — management should know we were exposed.

### Kịch bản 4 — Nói chuyện với vendor support
*Bối cảnh: Gọi hỗ trợ NAKIVO vì restore test thất bại.*

- **Engineer:** Hi, I'm calling about case NKV-77812 — a failed restore test.
- **Support:** Thanks. Can you describe what you attempted and what you saw?
- **Engineer:** I ran a full VM recovery of a 400 GB Windows Server to a Proxmox target. It reached 62% and failed with error "transporter connection lost".
- **Support:** Is the transporter on the same network segment as the target host?
- **Engineer:** No — the transporter is in the main VLAN, the Proxmox host is in the DR VLAN. There's a firewall between them.
- **Support:** That's very likely it. Long transfers can be dropped by an idle or session timeout on the firewall. Could you check the firewall session timeout for those ports?
- **Engineer:** I'll check with the network team. If that's the cause, what do you recommend?
- **Support:** Deploy a second transporter directly in the DR VLAN. That keeps the heavy traffic local and only control traffic crosses the firewall.
- **Engineer:** Understood. Could you send me the sizing guidance for the transporter and the exact ports required?
- **Support:** I'll attach both to the case within the hour.
- **Engineer:** Thank you. I'll test again Thursday night and update the case either way.

### Kịch bản 5 — Trình bày capacity planning để xin ngân sách
*Bối cảnh: Kỹ sư đề xuất mua thêm storage trong cuộc họp quý.*

- **Engineer:** I need to raise a capacity issue before it becomes an incident.
- **CFO:** How urgent?
- **Engineer:** We have five months of storage headroom at current growth. Data has grown 11% per quarter for six quarters — that trend is consistent, not a spike.
- **CFO:** Can you delete something instead?
- **Engineer:** We already reclaimed 2 TB last quarter by shortening retention and removing orphaned disks. That bought us the five months. There's very little left to clean up.
- **CFO:** What happens if we do nothing?
- **Engineer:** When the datastore fills, VMs pause — exactly what happened in the March incident, but across all systems rather than one. Recovery would be hours, not minutes.
- **CFO:** And the cost?
- **Engineer:** 12 TB usable is around [AMOUNT], installed. That covers roughly two years. Lead time from the vendor is six to eight weeks, which is why I'm asking now rather than in month four.
- **CFO:** Send me the quote and a one-page risk summary. I'll take it to the board next week.
- **Engineer:** I'll have both with you tomorrow.

### Kịch bản 6 — Bàn giao ca trực (handover)
*Bối cảnh: Kết thúc ca đêm, bàn giao cho ca ngày.*

- **Night shift:** Three things for you. First, node 2 in the Hyper-V cluster rebooted unexpectedly at 03:12.
- **Day shift:** Did the VMs come back?
- **Night shift:** Yes, HA restarted all six on node 1 within two minutes. No user impact, but node 2 is still out of the cluster pending a hardware check.
- **Day shift:** Okay. Second thing?
- **Night shift:** The monthly patch run finished at 01:40, all green except the print server — it needs a second reboot. Please do that before 07:30.
- **Day shift:** Noted. And third?
- **Night shift:** Replication to the DR site is 40 minutes behind. It's catching up, but keep an eye on it. If it's still behind by noon, escalate.
- **Day shift:** Understood. Anything the users know about?
- **Night shift:** Nothing. No tickets raised overnight. All three are in the handover log with timestamps.
- **Day shift:** Thanks. Go get some sleep.

### Kịch bản 7 — Đề xuất rủi ro với rollback plan
*Bối cảnh: Đề xuất nâng cấp vSphere lên phiên bản mới, quản lý lo ngại.*

- **Manager:** I'm not comfortable upgrading vSphere in the middle of the financial close.
- **Engineer:** That's a fair concern. Can I walk you through the risk and the rollback?
- **Manager:** Please.
- **Engineer:** The upgrade runs one host at a time. Each host is put into maintenance mode first, so every VM moves off it before anything changes. If one host fails to upgrade, the other three keep running production.
- **Manager:** And if the whole thing goes wrong?
- **Engineer:** vCenter is backed up before we start and can be restored in about 40 minutes. The hosts can be reimaged to the current version in roughly an hour each. Worst realistic case is a longer weekend, not a production outage.
- **Manager:** What's the benefit of doing it now instead of after the close?
- **Engineer:** Our current version loses security support in nine weeks. After that, any vulnerability stays unpatched.
- **Manager:** Alright. Do it the weekend after the close — that's three weeks from now and still inside the support window.
- **Engineer:** That works. I'll submit the change request with the full rollback plan on Monday.

---

## 4. Email mẫu (Email Templates)

### 4.1 Incident notification — Thông báo sự cố hạ tầng

```text
Subject: [P1 INCIDENT] [SYSTEM_NAME] unavailable since [START_TIME]

Dear all,

We are currently responding to an unplanned outage on [SYSTEM_NAME].

Start time:       [START_TIME] ([TIMEZONE])
Affected systems: [VM_OR_SERVICE_LIST]
Affected users:   [WHO — e.g. all users of the ERP]
Symptoms:         [WHAT_USERS_SEE]
Current status:   [Investigating / Identified / Recovering]
Working theory:   [SUSPECTED_CAUSE — mark clearly as unconfirmed]
Workaround:       [WORKAROUND_OR "None available"]
Data integrity:   [e.g. No data loss identified at this stage]
Reference:        [INCIDENT_ID]

Next update: [NEXT_UPDATE_TIME], or immediately if the service is
restored. Please do not restart any affected VM or service while the
investigation is in progress.

[YOUR_NAME]
Infrastructure Team — [COMPANY_NAME]
```

### 4.2 Maintenance announcement — Thông báo bảo trì

```text
Subject: [SCHEDULED MAINTENANCE] [SYSTEM_NAME] — [DATE] [START_TIME]-[END_TIME]

Dear colleagues,

The Infrastructure Team will carry out planned maintenance as follows.

Maintenance window: [DATE], [START_TIME] to [END_TIME] ([TIMEZONE])
Change reference:   [CHANGE_ID]
Scope of work:      [e.g. Security patching on 12 Windows Servers and
                    firmware update on 2 ESXi hosts]
Expected impact:    [SYSTEM_1] unavailable approx. [X] minutes
                    [SYSTEM_2] unavailable approx. [Y] minutes
Not affected:       [LIST_OF_UNAFFECTED_SERVICES]
Rollback plan:      [e.g. Restore from verified restore point taken
                    before the change; estimated 30 minutes]

Action required before [START_TIME]:
  - Save all work and sign out of [SYSTEM_NAME]
  - Close any long-running reports or imports

We will confirm completion by email. If the work finishes early, the
systems will be released early. Any issue observed after [END_TIME]
should be reported quoting [CHANGE_ID].

[YOUR_NAME]
Infrastructure Team — [COMPANY_NAME]
```

### 4.3 Status report — Báo cáo tình trạng hạ tầng định kỳ

```text
Subject: Infrastructure Status Report — [PERIOD]

Hi [MANAGER_NAME],

Summary for [PERIOD]:

AVAILABILITY
  Uptime achieved:   [XX.XX]%  (SLA target: [XX.X]%)
  Unplanned outages: [NUMBER] — total [MINUTES] minutes
  Planned downtime:  [MINUTES] minutes across [NUMBER] windows

BACKUP & RECOVERY
  Backup success rate: [XX]% ([FAILED_JOBS] failures, all remediated)
  Last verified restore test: [DATE] — result: [PASS/FAIL]
  Current RPO / RTO status: [ON TARGET / AT RISK — explain]

CAPACITY
  Storage used:   [XX]% ([FREE_TB] TB free)
  Runway at current growth: [MONTHS] months
  Compute headroom: [SUMMARY]

RISKS AND ACTIONS
  1. [RISK_1] — owner [NAME] — target [DATE]
  2. [RISK_2] — owner [NAME] — target [DATE]

Decisions needed from you: [DECISION_OR "None this period"]

Best regards,
[YOUR_NAME]
```

### 4.4 Access request — Yêu cầu cấp quyền quản trị

```text
Subject: [ACCESS REQUEST] Administrative access to [SYSTEM_NAME] for [NAME]

Dear [APPROVER_NAME],

I am requesting elevated access on behalf of [REQUESTER_NAME].

Requester:        [NAME], [JOB_TITLE], [TEAM]
System:           [SYSTEM_NAME — e.g. vCenter / Proxmox cluster / Veeam
                  Backup & Replication console]
Role requested:   [ROLE — e.g. Read-only / Operator / Administrator]
Business reason:  [WHY — e.g. to run and verify restore tests during the
                  on-call rotation]
Duration:         [PERMANENT / UNTIL_DATE]
Change reference: [TICKET_ID]

Controls that will apply:
  - Access granted through the [GROUP_NAME] security group only
  - MFA enforced on the account
  - Actions logged and reviewed at the [QUARTERLY] access review

Please reply "Approved" or "Rejected". No access will be granted without
your written approval.

Kind regards,
[YOUR_NAME]
Infrastructure Team
```

### 4.5 Resolution confirmation — Xác nhận xử lý xong / hoàn tất bảo trì

```text
Subject: [RESOLVED] [INCIDENT_OR_CHANGE_ID] — [SYSTEM_NAME] restored

Dear all,

[SYSTEM_NAME] is fully operational again.

Restored at:      [RESOLUTION_TIME] ([TIMEZONE])
Total downtime:   [MINUTES] minutes ([START_TIME] to [END_TIME])
Root cause:       [ROOT_CAUSE_IN_PLAIN_LANGUAGE]
Action taken:     [WHAT_WAS_DONE]
Data impact:      [e.g. No data loss. All transactions after
                  [TIME] were verified against the application log.]

Validation completed:
  - [CHECK_1 — e.g. All 12 VMs powered on and reachable]
  - [CHECK_2 — e.g. Backup job re-run successfully]
  - [CHECK_3 — e.g. Application login tested by [TEAM]]

Preventive actions:
  1. [ACTION_1] — owner [NAME] — by [DATE]
  2. [ACTION_2] — owner [NAME] — by [DATE]

A full post-mortem will be circulated by [POSTMORTEM_DATE]. If you
notice anything unusual in [SYSTEM_NAME], please report it quoting
[INCIDENT_ID].

Thank you for your patience.

[YOUR_NAME]
Infrastructure Team — [COMPANY_NAME]
```

---

## 5. Bài tập thực hành (Practice Exercises)

### A. Điền từ vào chỗ trống (10 câu)

Từ cho sẵn: *maintenance window, rollback, snapshot, RPO, failover, bottleneck, retention, threshold, replication, post-mortem*

1. Take a ____________ before you patch, and delete it within 24 hours.
2. Our ____________ is one hour, so we replicate hourly.
3. Set the disk alert ____________ at 85% so we have time to react.
4. If the upgrade fails, our ____________ plan is to reimage the host.
5. The ____________ is Saturday 22:00 to Sunday 02:00.
6. ____________ to the secondary site completed in 90 seconds.
7. The ____________ is storage latency, not CPU.
8. We keep 14 daily and 12 monthly restore points — that's our ____________ policy.
9. ____________ is a copy, not a backup: a deleted file is deleted on both sides.
10. The blameless ____________ is due within five working days.

### B. Matching thuật ngữ ↔ định nghĩa (10 cặp)

| # | Term | | Letter | Definition |
|---|---|---|---|---|
| 1 | hypervisor | | A | How fast a service must be back after a failure |
| 2 | cluster | | B | Moving a running VM between hosts with no downtime |
| 3 | vMotion | | C | Software that runs and manages virtual machines |
| 4 | RTO | | D | Normal measured behaviour, used for comparison |
| 5 | datastore | | E | A group of hosts working together for failover |
| 6 | baseline | | F | Forecasting future resource needs |
| 7 | capacity planning | | G | The storage where VM disks live |
| 8 | HA | | H | A formal request to approve a planned change |
| 9 | change request | | I | Design that keeps a service running through single failures |
| 10 | IOPS | | J | Storage operations completed per second |

### C. Viết lại câu dùng từ cho trước (5 câu)

1. "It will definitely work." → *(thận trọng hơn, dùng* **confident / rollback** *)*
2. "The server was broken for a long time." → *(chính xác hơn, dùng* **downtime** *và số liệu)*
3. "We copy data to another site." → *(kỹ thuật hơn, dùng* **replication / DR site** *)*
4. "We don't have space soon." → *(chuyên nghiệp hơn, dùng* **capacity / runway** *)*
5. "It was my mistake." → *(chuyên nghiệp và có hành động, dùng* **preventive action** *)*

### D. Role-play

**Tình huống:** Bạn là System Engineer. Đêm qua **backup job** của toàn bộ cụm **Proxmox** thất bại lần thứ ba liên tiếp, nghĩa là công ty đã 3 ngày **không có restore point**. Sáng nay bạn phải báo cáo với IT Director người nước ngoài — người này không rành kỹ thuật sâu nhưng rất quan tâm rủi ro kinh doanh.

Thực hành trình bày trong **3 phút**, gồm: (a) nêu rủi ro bằng ngôn ngữ kinh doanh, không phải thuật ngữ; (b) nêu nguyên nhân đã xác định và phần chưa chắc chắn; (c) hành động khắc phục ngay trong hôm nay; (d) biện pháp phòng ngừa để không tái diễn. Đổi vai: người kia hỏi thêm *"Why didn't monitoring catch this earlier?"* — hãy trả lời trung thực.

---

<details>
<summary>Đáp án</summary>

**A. Điền từ**
1. snapshot — 2. RPO — 3. threshold — 4. rollback — 5. maintenance window — 6. Failover — 7. bottleneck — 8. retention — 9. Replication — 10. post-mortem

**B. Matching**
1–C, 2–E, 3–B, 4–A, 5–G, 6–D, 7–F, 8–I, 9–H, 10–J

**C. Viết lại câu** *(gợi ý — nhiều cách đúng)*
1. "I'm confident it will work, and I'll have a tested rollback plan ready in case it doesn't."
2. "Total downtime was 47 minutes, from 08:04 to 08:51."
3. "We replicate data to the DR site every 15 minutes, which gives us a 15-minute RPO."
4. "At the current growth rate we have about five months of storage runway before we hit capacity."
5. "That was our mistake. I've already applied the fix, and the preventive action is an alert at 85% plus a weekly snapshot report."

**D. Role-play — khung trình bày tham khảo**
- Rủi ro (business language): "For the last three days, if we had lost a server we could not have recovered yesterday's work. That's the exposure — not a technical failure, a data-loss risk."
- Nguyên nhân: "What I know: the job fails on the SQL VM because the database grew from 900 GB to 1.4 TB and the freeze now times out. What I don't know yet is whether the same limit will affect the file server as it grows."
- Hành động hôm nay: "I'm running a manual backup this morning — that closes the gap within four hours. Then I'll rebuild the job using native SQL log backups tonight."
- Phòng ngừa: "Two changes: an alert on the second consecutive failure instead of the fifth, and a monthly verified restore test with results in your status report."
- Trả lời trung thực: "Monitoring did send emails, but the alert went to a shared mailbox nobody owns. That's the real failure here, and I'm changing it to page the on-call engineer today."

</details>
