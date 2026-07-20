# Security Specialist — Tiếng Anh cho Chuyên gia bảo mật

Tài liệu này dành cho chuyên viên bảo mật, thành viên **SOC**, người làm **incident response**, đánh giá rủi ro, hoặc chuẩn bị cho kỳ **audit** ISO 27001 / SOC 2.
Dùng khi bạn cần báo cáo một **vulnerability** mà không gây hoảng loạn, trả lời auditor nước ngoài, viết **incident report**, hoặc từ chối một yêu cầu cấp quyền không hợp lệ một cách lịch sự nhưng dứt khoát.
Trình độ mục tiêu: B1–B2. Ngôn ngữ thực dụng, dùng được ngay trong ticket và email.

**Phát âm hay sai (người Việt lưu ý):**
- **vulnerability** — /ˌvʌlnərəˈbɪləti/ — 6 âm tiết, trọng âm ở "BIL". Đừng nuốt phần "-nera-": "vun-nơ-rơ-BI-lơ-ti".
- **authentication** — /ɔːˌθentɪˈkeɪʃən/ — trọng âm ở "KEI". Chữ *th* là /θ/ (lưỡi giữa hai răng), không đọc thành "t".
- **breach** — /briːtʃ/ — nguyên âm **dài**, kết thúc bằng /tʃ/. Đừng đọc thành "brít" hay "brết".
- **threat** — /θret/ — âm /θ/ + nguyên âm **ngắn**. Phân biệt với *treat* /triːt/. Nói sai là người nghe hiểu ngược nghĩa.
- **compliance** — /kəmˈplaɪəns/ — trọng âm ở "PLAI", đọc "cơm-PLAI-ơn(s)", không phải "com-pli-en-xơ".

---

## 1. Từ vựng cốt lõi (Core Vocabulary)

| Term | Definition (EN) | Example Sentence | Tiếng Việt |
|---|---|---|---|
| vulnerability | A weakness that an attacker could exploit | The scan found a critical **vulnerability** in the file upload endpoint. | lỗ hổng bảo mật |
| threat | Anything with the potential to cause harm | Ransomware remains the top **threat** for our industry this year. | mối đe doạ |
| risk | The combination of likelihood and impact of a threat | We rated the **risk** as medium because the service is internal only. | rủi ro |
| exploit | Code or a technique that takes advantage of a vulnerability | A public **exploit** for this CVE was released yesterday. | mã khai thác |
| CVE | A public identifier for a known vulnerability | **CVE**-2024-3094 affects the version of the library we ship. | mã định danh lỗ hổng công khai |
| CVSS score | A 0–10 rating of vulnerability severity | With a **CVSS score** of 9.8, this must be patched within 24 hours. | điểm mức độ nghiêm trọng |
| patch management | The process of testing and applying security updates | Our **patch management** policy requires critical fixes within 7 days. | quản lý bản vá |
| zero-day | A vulnerability with no vendor fix available yet | We deployed a virtual patch because it's a **zero-day**. | lỗ hổng chưa có bản vá |
| breach | An incident where data was actually accessed or stolen | We found no evidence that this was a data **breach**. | rò rỉ dữ liệu |
| incident response (IR) | The structured process of handling a security event | Our **incident response** plan defines who declares an incident. | ứng phó sự cố |
| containment | Limiting the spread and impact of an incident | **Containment** was achieved by isolating the host from the network. | khoanh vùng, cô lập |
| eradication | Removing the attacker and their tools from the environment | After **eradication**, we rebuilt the server from a clean image. | loại bỏ tác nhân |
| post-mortem | A blameless review after an incident | The **post-mortem** produced five concrete action items. | rà soát sau sự cố |
| SIEM | A platform that collects and correlates security logs | The **SIEM** raised an alert on 300 failed logins in two minutes. | hệ thống quản lý sự kiện bảo mật |
| SOC | The team that monitors and responds to security events 24/7 | The **SOC** escalated the alert to tier two within four minutes. | trung tâm điều hành an ninh |
| IDS / IPS | Systems that detect (IDS) or block (IPS) malicious traffic | Our **IPS** blocked the SQL injection attempt automatically. | hệ thống phát hiện / ngăn chặn xâm nhập |
| DLP | Controls that stop sensitive data from leaving the organisation | **DLP** flagged an email with 2,000 customer records attached. | chống thất thoát dữ liệu |
| zero trust | A model that never trusts by default and always verifies | Under **zero trust**, being on the office network grants no access by itself. | mô hình không tin cậy mặc định |
| least privilege | Giving users only the access they actually need | **Least privilege** means developers do not get production admin rights. | đặc quyền tối thiểu |
| privilege escalation | Gaining higher permissions than intended | The attacker used a local **privilege escalation** bug to become root. | leo thang đặc quyền |
| authentication | Verifying who a user is | We enforce multi-factor **authentication** on all admin accounts. | xác thực |
| authorization | Deciding what an authenticated user may do | The bug was in **authorization** — any logged-in user could read all invoices. | phân quyền |
| MFA | Requiring two or more proofs of identity | Enabling **MFA** blocked 99% of the password-spraying attempts. | xác thực đa yếu tố |
| penetration test | An authorised simulated attack to find weaknesses | The annual **penetration test** starts on Monday and runs for two weeks. | kiểm thử xâm nhập |
| compliance | Meeting required standards, laws, or contracts | ISO 27001 **compliance** requires evidence, not just good intentions. | tuân thủ |
| audit | A formal review of controls against a standard | The **audit** covers access reviews for the last twelve months. | kiểm toán, đánh giá |
| audit trail | A tamper-evident record of who did what and when | The **audit trail** shows the account was disabled at 14:02 by the SOC. | dấu vết kiểm toán |
| risk assessment | A structured analysis of threats and their impact | The **risk assessment** rated data loss as the highest business risk. | đánh giá rủi ro |
| remediation | The work done to fix a finding | **Remediation** for the top three findings is due by the end of the quarter. | khắc phục |
| phishing | Fraudulent messages that trick users into revealing data | Three staff reported the **phishing** email before anyone clicked. | tấn công lừa đảo qua email |
| encryption at rest / in transit | Protecting stored data / data being transmitted | All backups use **encryption at rest** with customer-managed keys. | mã hoá khi lưu trữ / khi truyền |

> **Lưu ý người Việt hay nhầm:** **vulnerability** (lỗ hổng — cái đang tồn tại) ≠ **threat** (mối đe doạ — cái có thể xảy đến) ≠ **risk** (rủi ro — khả năng × hậu quả). Trong báo cáo, dùng sai ba từ này khiến người đọc đánh giá sai mức độ nghiêm trọng.
> Cũng đừng gọi mọi sự cố là **"breach"**. *Breach* nghĩa là dữ liệu **đã bị** truy cập hoặc lấy đi — từ này có hệ quả pháp lý. Khi chưa chắc, dùng **"security incident"** hoặc **"suspicious activity"**.

---

## 2. Mẫu câu giao tiếp (Common Phrases)

### Báo cáo (Reporting)

1. **Formal** — "We have identified a high-severity vulnerability affecting [system]. There is currently no evidence of exploitation." → *Chúng tôi phát hiện một lỗ hổng mức cao ở [hệ thống]. Hiện chưa có dấu hiệu bị khai thác.*
2. **Formal** — "The incident has been contained. Investigation into the root cause is ongoing." → *Sự cố đã được khoanh vùng. Việc điều tra nguyên nhân gốc đang tiếp tục.*
3. **Formal** — "Based on the evidence available, we do not classify this as a data breach at this stage." → *Dựa trên bằng chứng hiện có, ở giai đoạn này chúng tôi chưa xếp đây là rò rỉ dữ liệu.*
4. **Informal** — "Quick update: host is isolated, no lateral movement so far." → *Cập nhật nhanh: máy đã cô lập, chưa thấy di chuyển ngang.*
5. **Informal** — "Scanner flagged it, but it's a false positive — that port isn't exposed externally." → *Máy quét báo, nhưng đây là báo động giả, cổng đó không mở ra ngoài.*

### Yêu cầu (Requesting)

6. **Formal** — "Could you please provide the access logs for [system] covering [date range]?" → *Anh/chị gửi giúp log truy cập của [hệ thống] trong khoảng [thời gian].*
7. **Formal** — "We would ask that this patch be applied within the 72-hour window defined in our policy." → *Đề nghị áp bản vá trong 72 giờ theo chính sách.*
8. **Formal** — "Please confirm in writing that the affected account has been disabled." → *Vui lòng xác nhận bằng văn bản rằng tài khoản liên quan đã bị vô hiệu hoá.*
9. **Informal** — "Can you pull the SIEM events for that IP over the last 24 hours?" → *Lấy giúp sự kiện SIEM của IP đó trong 24 giờ qua nhé?*
10. **Informal** — "Could you send me a screenshot of the email header, not just the body?" → *Gửi mình ảnh phần header email, không chỉ nội dung nhé?*

### Giải thích (Explaining)

11. **Formal** — "To be clear about the scope: the vulnerability is exploitable only from inside the corporate network." → *Nói rõ phạm vi: lỗ hổng chỉ khai thác được từ trong mạng nội bộ.*
12. **Formal** — "Least privilege is not a lack of trust in you personally; it is a control that limits damage if any account is compromised." → *Đặc quyền tối thiểu không phải là không tin cá nhân anh/chị, mà là biện pháp giới hạn thiệt hại nếu bất kỳ tài khoản nào bị chiếm.*
13. **Formal** — "The residual risk after remediation is assessed as low and is documented in the risk register." → *Rủi ro còn lại sau khắc phục được đánh giá là thấp và đã ghi vào sổ rủi ro.*
14. **Informal** — "In plain terms: someone guessed the password, but MFA stopped them." → *Nói đơn giản: có người đoán được mật khẩu, nhưng MFA đã chặn lại.*
15. **Informal** — "Think of zero trust as checking the badge at every door, not just the front gate." → *Coi zero trust như kiểm tra thẻ ở mọi cánh cửa, không chỉ cổng chính.*

### Xử lý sự cố & từ chối yêu cầu (Handling incidents & saying no)

16. **Formal** — "We are treating this as a P1 incident and have activated the incident response process." → *Chúng tôi xử lý việc này ở mức P1 và đã kích hoạt quy trình ứng phó sự cố.*
17. **Formal** — "I understand the urgency, however I'm not able to grant permanent production access. I can offer time-limited elevation with approval instead." → *Tôi hiểu tính cấp bách, nhưng tôi không thể cấp quyền production vĩnh viễn. Tôi có thể cấp quyền tạm thời có phê duyệt.*
18. **Formal** — "That request falls outside our access policy. Let me suggest an approach that meets your need and stays compliant." → *Yêu cầu đó nằm ngoài chính sách. Để tôi đề xuất cách vừa đáp ứng nhu cầu vừa tuân thủ.*
19. **Informal** — "I can't approve that one, sorry — but tell me what you're trying to do and we'll find another way." → *Cái đó mình không duyệt được, nhưng cho mình biết bạn cần làm gì để tìm cách khác.*
20. **Informal** — "Let's contain first, investigate after. Please disconnect the laptop from the network now." → *Cô lập trước, điều tra sau. Ngắt mạng laptop ngay giúp mình.*

> **Mẹo từ chối lịch sự nhưng dứt khoát:** dùng công thức **acknowledge → decline → alternative**. Ví dụ: *"I understand this is blocking your release (acknowledge). I can't grant standing admin rights (decline). I can enable just-in-time access for four hours with your manager's approval (alternative)."* Tránh nói "maybe" hay "I will try" — trong bảo mật, câu mơ hồ tạo ra kỳ vọng sai.

---

## 3. Tình huống thực tế (Real-world Scenarios)

### Scenario 1 — Báo cáo lỗ hổng nghiêm trọng mà không gây hoảng loạn

*Bối cảnh: Phát hiện CVE nghiêm trọng trong thư viện đang dùng ở production. Kỹ sư báo với giám đốc kỹ thuật.*

**Security:** I need ten minutes. We've found a critical CVE in a library used by the customer portal.
**CTO:** How bad is it?
**Security:** CVSS 9.8, remote code execution. But let me give you the full picture before we react.
**CTO:** Go on.
**Security:** The vulnerable function is only reachable through an endpoint that sits behind authentication and our WAF already blocks the known payload.
**CTO:** So we're not currently exposed?
**Security:** Not to the public exploit, no. I'd call it high risk, not an emergency. There's no evidence of exploitation in our logs.
**CTO:** What do you need?
**Security:** A patch window in the next 48 hours, and one backend engineer for half a day. I've already prepared the upgrade branch.
**CTO:** Approved. Keep the tone in your email calm — I don't want the board reading "critical" and panicking.
**Security:** Understood. I'll lead with the mitigation we already have in place, then the fix timeline.

### Scenario 2 — Nói chuyện với auditor

*Bối cảnh: Auditor bên ngoài kiểm tra quy trình rà soát quyền truy cập cho chứng nhận ISO 27001.*

**Auditor:** Can you walk me through your access review process?
**Security:** Certainly. We perform a full user access review quarterly, and an immediate review whenever someone changes role or leaves.
**Auditor:** Who performs the review?
**Security:** The system owner reviews and signs off. Security facilitates and keeps the evidence.
**Auditor:** May I see the evidence for the most recent quarter?
**Security:** Yes. Here is the exported report, the sign-off email from each owner, and the tickets for the twelve accounts we removed.
**Auditor:** What happens if an owner does not respond?
**Security:** After two reminders it escalates to their director, and the review is marked overdue in our compliance dashboard.
**Auditor:** Has that happened?
**Security:** Once, in Q2. The record is in the dashboard, it was closed eleven days late, and we documented it as a minor non-conformity with a corrective action.
**Auditor:** I appreciate the transparency. That's the right way to handle it.

> **Ghi chú:** Với auditor, **đừng giấu lỗi nhỏ**. Câu "we documented it as a minor non-conformity with a corrective action" cho thấy hệ thống hoạt động. Giấu rồi bị phát hiện sẽ nghiêm trọng hơn nhiều.

### Scenario 3 — Từ chối yêu cầu cấp quyền không hợp lệ

*Bối cảnh: Một developer xin quyền admin production vĩnh viễn để "xử lý bug nhanh hơn".*

**Developer:** I need permanent admin on the production database. Waiting for approval every time slows me down.
**Security:** I hear you — that delay is real, and I don't want it blocking releases.
**Developer:** So you'll grant it?
**Security:** Not as a standing permission, no. Production admin is restricted under our least-privilege policy, and the audit next month checks exactly this.
**Developer:** But I'm the one who wrote the schema.
**Security:** I know, and this isn't about trust in you. If your account is ever phished, the attacker inherits whatever you hold permanently.
**Developer:** Then what are my options?
**Security:** Just-in-time elevation. You request it in the tool, your lead approves, and you get four hours of full access. Approval usually takes under ten minutes.
**Developer:** And at 2 AM during an incident?
**Security:** During a declared incident, the on-call lead can approve, and there's a break-glass account with automatic logging. You'll never be stuck.
**Developer:** That's fair. Can you help me set up the request template?
**Security:** Happy to. I'll send it today so it's ready before your next release.

### Scenario 4 — Xử lý báo cáo phishing từ nhân viên

*Bối cảnh: Một nhân viên kế toán gọi cho team bảo mật vì đã bấm vào link trong email lạ.*

**Employee:** I think I clicked something I shouldn't have. There was an invoice email and I entered my password.
**Security:** Thank you for telling us straight away — that's exactly the right thing to do. You're not in trouble.
**Employee:** It looked like it came from our supplier.
**Security:** They're designed to look real. First, please don't shut the laptop down. Just disconnect it from Wi-Fi.
**Employee:** Done.
**Security:** I'm resetting your password now and revoking your active sessions. Did you approve any MFA prompt after entering the password?
**Employee:** There was a notification and I tapped approve. I thought it was the normal login.
**Security:** Good to know — that's important. I'll check whether any sign-in succeeded from an unusual location.
**Employee:** I'm sorry.
**Security:** Honestly, you did the hardest part by reporting it fast. That's what limits the damage. I'll call you back within thirty minutes with next steps.

### Scenario 5 — Thảo luận nội bộ về kết quả penetration test

*Bối cảnh: Team bảo mật họp nội bộ để phân loại các phát hiện sau đợt pentest.*

**Lead:** The pentest report has eighteen findings. Three critical, five high, ten informational.
**Analyst A:** The critical ones are all the same root cause — the API doesn't check object ownership.
**Lead:** So one authorization bug, exploitable in three places?
**Analyst A:** Correct. Fixing the middleware closes all three.
**Analyst B:** What about the outdated TLS on the marketing site? They rated it high.
**Lead:** I'd push back on that rating. Static site, no user data, no session. It's a finding, but the impact is low.
**Analyst B:** Should we dispute it in the report?
**Lead:** We don't dispute — we add our risk context and accept it formally in the risk register. Auditors want to see the reasoning, not silence.
**Analyst A:** Timeline for the critical fix?
**Lead:** Ten working days. I'll book the retest for the week after so we have written confirmation before the board meeting.

### Scenario 6 — Thông báo sự cố cho khách hàng

*Bối cảnh: Hệ thống bị tấn công dò mật khẩu. Không có dữ liệu bị lấy. Khách hàng yêu cầu giải thích.*

**Client:** We received your incident notification. Was our data stolen?
**Security:** No. Let me be precise about what happened and what did not.
**Client:** Please do.
**Security:** An attacker ran a password-spraying attack against our login page over about forty minutes. Two accounts had correct passwords, but multi-factor authentication blocked both sign-ins.
**Client:** So nobody got in?
**Security:** Correct. Our logs show no successful authentication and no data access. This was an attempted intrusion, not a breach.
**Client:** How do you know the logs are complete?
**Security:** Authentication logs are written to a separate append-only store that the application cannot modify. We reviewed the full window.
**Client:** What are you changing?
**Security:** We've enabled rate limiting per source IP, forced a password reset for the two accounts, and added an alert that fires after twenty failed logins per minute.
**Client:** Thank you. Will you send this in writing?
**Security:** Yes, a full incident report by end of day tomorrow, including the timeline and the follow-up actions with owners and dates.

### Scenario 7 — Giải thích zero trust cho quản lý phi kỹ thuật

*Bối cảnh: Trưởng phòng nhân sự hỏi tại sao vẫn phải xác thực dù đang ngồi ở văn phòng.*

**HR Manager:** Why do I have to authenticate again when I'm already in the office?
**Security:** Because we've moved to a **zero trust** model. Being on the office network no longer counts as proof of identity.
**HR Manager:** It used to be enough.
**Security:** It did, and that was the weakness. If anyone plugs into a meeting-room port or steals a laptop, the old model trusted them automatically.
**HR Manager:** But it adds steps to my day.
**Security:** It does, and I want to keep that cost low. With the phone app, most sign-ins are one tap, and we remember trusted devices for thirty days.
**HR Manager:** What about the HR system specifically? That's the sensitive one.
**Security:** That one stays at every-session verification, because it holds personal data of every employee. Regulators expect stronger controls there.
**HR Manager:** That's reasonable. Can you explain this to my team? They keep asking me.
**Security:** Of course. I'll run a fifteen-minute session, no jargon, with a couple of real examples of what it prevents.

---

## 4. Email mẫu (Email Templates)

### 4.1 Incident notification

```text
Subject: [SECURITY INCIDENT] [Severity] — [short description] — initial notification

Dear [Recipient / Team],

We are writing to inform you of a security incident detected at approximately
[HH:MM] [timezone] on [date].

What we know:      [factual description, e.g. repeated failed login attempts
                   against the customer portal from a single IP range]
What we do NOT
know yet:          [e.g. the origin of the attempt and whether other systems
                   were targeted]
Current impact:    [e.g. no confirmed unauthorised access; no evidence of data
                   exposure at this time]
Actions taken:     - [e.g. affected accounts disabled at HH:MM]
                   - [e.g. source IP range blocked at the firewall]
                   - [e.g. incident response process activated]

We will provide the next update by [HH:MM] [timezone]. Please direct any
questions to [contact] rather than forwarding this message externally.

Regards,
[Your Name]
Information Security | [Company]
```

### 4.2 Maintenance announcement (security patching)

```text
Subject: Scheduled security patching — [System Name] on [Date]

Dear [Team / Customer],

We will apply security updates to [system name] to remediate [reference,
e.g. CVE-2025-XXXX, CVSS 9.1].

Window:           [Date], [Start] – [End] [timezone]
Expected impact:  [e.g. two restarts, up to 10 minutes unavailability each]
Reason:           [brief, non-alarming justification]
If we cannot
complete in time: We will roll back to the current version and reschedule.

No action is required from you. If this window conflicts with a critical
activity, please reply by [deadline].

Regards,
[Your Name]
Information Security | [Company]
```

### 4.3 Status report

```text
Subject: Monthly security status report — [Month Year]

Hi [Manager / Stakeholder],

Summary of the security posture for [month].

Incidents:            [number] total — [breakdown by severity]; [number] open
Mean time to contain: [e.g. 38 minutes] (target: [60 minutes])
Vulnerabilities:      [number] critical/high open; [number] remediated this month
Patch compliance:     [percentage]% of endpoints within policy
Phishing simulation:  [percentage]% click rate ([up/down] from [previous])
Audit / compliance:   [e.g. ISO 27001 surveillance audit passed, one minor
                      non-conformity, corrective action due DD/MM]
Top risks:            1. [risk] — [owner] — [due date]
                      2. [risk] — [owner] — [due date]
Decisions needed:     [e.g. approval for DLP rollout to the finance team]

Details and evidence are available on request.

Regards,
[Your Name]
```

### 4.4 Access request

```text
Subject: Access request — [Role] on [System] for [Purpose]

Hi [Approver Name],

I would like to request the following access, in line with our least-privilege
policy.

Requester:      [Name], [Team]
System:         [system / environment]
Role requested: [specific role, not "admin" unless truly required]
Business
justification:  [what task requires it and why the current role is insufficient]
Duration:       [e.g. 8 hours / until DD/MM / for ticket TICKET-1234]
Data accessed:  [e.g. no personal data / customer records, read-only]
Compensating
controls:       [e.g. session recording enabled, actions logged to SIEM]

If a time-limited (just-in-time) elevation is preferred over a standing
assignment, that works for my use case.

Regards,
[Your Name]
```

### 4.5 Resolution confirmation

```text
Subject: [RESOLVED] Security incident [ID] — [short description]

Dear [Recipient / Team],

The security incident reported on [date] is now closed.

Timeline:      Detected   [HH:MM] [date]
               Contained  [HH:MM] [date]
               Eradicated [HH:MM] [date]
               Closed     [HH:MM] [date]
Root cause:    [factual, non-blaming description]
Data impact:   [e.g. no evidence of unauthorised access to customer data;
               authentication logs reviewed for the full window]
Remediation:   - [action completed]
               - [action completed]
Preventive
actions:       - [action] — owner [name] — due [date]
               - [action] — owner [name] — due [date]

A blameless post-mortem was held on [date]; the full report is available at
[location / on request].

Thank you to everyone who reported and responded quickly.

Regards,
[Your Name]
Information Security | [Company]
```

---

## 5. Bài tập thực hành (Practice Exercises)

### A. Điền từ vào chỗ trống (10 câu)

Từ gợi ý: *vulnerability, containment, least privilege, breach, patch, phishing, audit trail, escalated, remediation, compliance*

1. The scanner found a critical ____ in the file upload endpoint.
2. ____ was achieved by isolating the host from the network within eight minutes.
3. Under ____, developers do not receive standing production admin rights.
4. We found no evidence of unauthorised access, so this is not a data ____.
5. Please apply the security ____ within the 72-hour window defined in our policy.
6. Three employees reported the ____ email before anyone entered credentials.
7. The ____ shows the account was disabled at 14:02 by the SOC analyst.
8. The SOC ____ the alert to tier two within four minutes of detection.
9. ____ for the three critical findings is due within ten working days.
10. ISO 27001 ____ requires documented evidence, not just good intentions.

### B. Nối thuật ngữ với định nghĩa (10 cặp)

| # | Term | | Definition |
|---|---|---|---|
| 1 | SIEM | A | An authorised simulated attack to find weaknesses |
| 2 | zero trust | B | Verifying who a user is |
| 3 | DLP | C | A platform that collects and correlates security logs |
| 4 | penetration test | D | A vulnerability with no vendor fix available yet |
| 5 | authentication | E | A model that never trusts by default and always verifies |
| 6 | authorization | F | Controls that stop sensitive data from leaving the organisation |
| 7 | zero-day | G | Gaining higher permissions than intended |
| 8 | privilege escalation | H | Deciding what an authenticated user may do |
| 9 | CVSS score | I | The team that monitors security events around the clock |
| 10 | SOC | J | A 0–10 rating of vulnerability severity |

### C. Viết lại câu dùng từ cho trước (5 câu)

1. Someone got into the system and took customer data. *(breach)*
2. We stopped the problem from spreading to other machines. *(containment)*
3. Users should only get the access they really need for their job. *(least privilege)*
4. The bad email tried to make staff type their passwords. *(phishing)*
5. We must fix the problems the report found, and prove we did it. *(remediation, evidence)*

### D. Role-play

**Tình huống:** Bạn là Security Specialist. Trưởng phòng kinh doanh yêu cầu bạn xuất toàn bộ danh sách khách hàng (bao gồm email và số điện thoại) ra file Excel để gửi cho một đối tác marketing bên ngoài. Việc này vi phạm chính sách bảo vệ dữ liệu, và **DLP** sẽ chặn email. Người này đang gấp và không hài lòng.

**Nhiệm vụ:** Đóng vai một cuộc trao đổi 8 lượt. Bạn phải: giữ thái độ hợp tác, nêu rõ lý do từ chối bằng ngôn ngữ nghiệp vụ (không phải "chính sách nói vậy"), đề xuất ít nhất một phương án thay thế hợp lệ, và chốt bước tiếp theo cụ thể.

---

<details>
<summary>Đáp án</summary>

**A. Điền từ**

1. vulnerability
2. Containment
3. least privilege
4. breach
5. patch
6. phishing
7. audit trail
8. escalated
9. Remediation
10. compliance

**B. Matching**

1–C, 2–E, 3–F, 4–A, 5–B, 6–H, 7–D, 8–G, 9–J, 10–I

**C. Viết lại câu (gợi ý)**

1. An attacker gained unauthorised access and exfiltrated customer data — this qualifies as a data **breach**.
2. **Containment** prevented the incident from spreading to other hosts.
3. Under the principle of **least privilege**, users receive only the access required for their role.
4. The **phishing** email attempted to trick staff into entering their credentials.
5. **Remediation** of the reported findings is required, together with **evidence** that each fix has been verified.

**D. Role-play — khung câu tham khảo**

- Hợp tác trước: "I want to help you hit that deadline, so let me understand what the partner actually needs."
- Nêu rủi ro nghiệp vụ, không nêu chính sách suông: "Sending customer emails and phone numbers to an external party without a data processing agreement exposes us to a regulatory fine and to a reportable incident if they leak it."
- Nêu thực tế kỹ thuật: "Our DLP will block that attachment automatically, so even if we agreed, the email wouldn't arrive."
- Từ chối rõ ràng: "So I can't approve the full export in its current form."
- Phương án 1: "We can share a pseudonymised list — segment and region, no direct identifiers. That covers most campaign targeting."
- Phương án 2: "Or the partner works inside our platform under a signed data processing agreement, and we log every access."
- Xác nhận nhu cầu thật: "Which of those actually gets the campaign live? If it's targeting, option one is enough."
- Chốt: "I'll draft the pseudonymised extract today and send legal the DPA template. Can we review both tomorrow at 10?"

</details>
