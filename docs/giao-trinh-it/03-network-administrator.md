# Network Administrator — Tiếng Anh cho Quản trị mạng

Tài liệu này dành cho **network administrator**, **NOC engineer** và **IT helpdesk** người Việt đang làm việc với đồng nghiệp hoặc khách hàng nước ngoài.
Dùng khi bạn phải báo cáo sự cố mạng, xin **change window**, giải thích cho người dùng vì sao mạng chậm, hoặc trao đổi với vendor (FortiGate, Cisco, Ubiquiti, pfSense) qua email và call.
Trình độ: **B1–B2**. Học xong bạn có thể mô tả một sự cố mạng qua điện thoại mà không cần nhìn sơ đồ.

---

## 1. Từ vựng cốt lõi (Core Vocabulary)

| Term | Definition (EN) | Example Sentence | Tiếng Việt |
| --- | --- | --- | --- |
| VLAN | A logical network that separates traffic on the same physical switch | We put the CCTV cameras on **VLAN 40** so they cannot reach the finance servers. | Mạng LAN ảo |
| Subnet | A smaller address range carved out of a larger network | The Hanoi office uses the **subnet** 10.20.30.0/24. | Mạng con |
| Subnet mask | The value that defines how many hosts fit in a subnet | Your laptop has the wrong **subnet mask**, that is why the gateway is unreachable. | Mặt nạ mạng |
| Gateway | The device that sends traffic out of the local network | The default **gateway** stopped responding to ping at 09:12. | Cổng ra mạng |
| Router | A device that forwards packets between networks | We replaced the branch **router** with a Cisco ISR 1111. | Bộ định tuyến |
| Switch | A device that connects devices inside one LAN | Port 14 on the access **switch** keeps flapping. | Bộ chuyển mạch |
| Trunk port | A switch port that carries several VLANs | Please configure the uplink as a **trunk port** for VLAN 10, 20 and 40. | Cổng trunk |
| Access port | A switch port assigned to a single VLAN | The printer is on an **access port**, so tagging is not required. | Cổng access |
| Firewall rule | A policy that allows or blocks specific traffic | I need a **firewall rule** to allow TCP 1433 from the app server only. | Luật tường lửa |
| ACL | Access Control List, an ordered list of permit or deny statements | The **ACL** is blocking the request before it reaches the server. | Danh sách kiểm soát truy cập |
| NAT | Network Address Translation, mapping private to public addresses | Outbound traffic uses **NAT** on the FortiGate WAN interface. | Chuyển đổi địa chỉ mạng |
| Port forwarding | Sending traffic from a public port to an internal host | We set up **port forwarding** so the vendor can reach the camera NVR. | Chuyển tiếp cổng |
| VPN | An encrypted tunnel between sites or for remote users | The **VPN** tunnel to the Singapore office dropped twice last night. | Mạng riêng ảo |
| Site-to-site VPN | A permanent tunnel joining two office networks | The **site-to-site VPN** uses IKEv2 with AES-256. | VPN nối hai chi nhánh |
| Routing table | The list of paths a router uses to forward traffic | The static route is missing from the **routing table**. | Bảng định tuyến |
| Static route | A manually configured path | I added a **static route** for 192.168.50.0/24 via the core switch. | Định tuyến tĩnh |
| BGP | A protocol that exchanges routes between networks or ISPs | Our **BGP** session with the ISP went down for six minutes. | Giao thức định tuyến BGP |
| Bandwidth | The maximum data capacity of a link | The leased line has 200 Mbps of **bandwidth** in each direction. | Băng thông |
| Throughput | The data actually transferred per second | Real **throughput** is only 40 Mbps although we pay for 200. | Thông lượng thực tế |
| Latency | The delay before data reaches its destination | **Latency** to the Tokyo region jumped from 60 ms to 310 ms. | Độ trễ |
| Jitter | Variation in latency, harmful to voice and video | High **jitter** is why the Teams calls sound choppy. | Độ biến động trễ |
| Packet loss | The percentage of packets that never arrive | We are seeing 8% **packet loss** on the WAN interface. | Mất gói tin |
| DHCP | The service that hands out IP addresses automatically | The **DHCP** scope is exhausted, no free addresses are left. | Cấp phát IP tự động |
| DNS | The service that translates names into IP addresses | The site is up, but **DNS** resolution is failing for internal clients. | Phân giải tên miền |
| Uptime | How long a device or link has run without failure | The firewall shows an **uptime** of 214 days. | Thời gian hoạt động liên tục |
| Failover | Automatic switch to a backup link or device | **Failover** to the secondary ISP worked, but it took 40 seconds. | Chuyển dự phòng |
| Change window | An approved time slot for making risky changes | Can we book a **change window** on Saturday from 22:00 to 00:00? | Khung giờ được phép thay đổi |
| Rollback plan | The steps to undo a change if it fails | The **rollback plan** is to restore the config backup from 21:55. | Kế hoạch hoàn tác |
| SLA | Service Level Agreement, the promised service quality | Our **SLA** commits to 99.9% availability per month. | Cam kết chất lượng dịch vụ |
| Traceroute | A tool showing every hop along a path | The **traceroute** stops at hop 7, inside the ISP network. | Lệnh dò đường đi gói tin |

> **Phát âm — người Việt hay sai**
> - **router**: /ˈruː.tər/ (Anh) hoặc /ˈraʊ.tər/ (Mỹ). Chọn một kiểu và giữ nguyên, đừng nói "rao-tơ" nửa vời.
> - **latency**: /ˈleɪ.tən.si/ — "LAY-ten-si", KHÔNG phải "la-ten-xi".
> - **subnet**: /ˈsʌb.net/ — nhấn âm đầu, "SUB-net".
> - **VLAN**: đọc là "VEE-lan" (một từ), không đánh vần từng chữ.
> - **gateway**: /ˈɡeɪt.weɪ/ — "GATE-way", không phải "ga-tơ-quây".
> - **throughput**: /ˈθruː.pʊt/ — "THROO-put". Âm **th** phải đưa lưỡi ra, đừng đọc thành "tru-put".

---

## 2. Mẫu câu giao tiếp (Common Phrases)

### Báo cáo (Reporting)

1. **Formal** — "We are currently experiencing a network outage affecting the [Hanoi] office." → Chúng tôi đang gặp sự cố mất mạng ảnh hưởng tới văn phòng [Hà Nội].
2. **Formal** — "The issue started at 09:12 ICT and is still ongoing. I will send an update every 30 minutes." → Sự cố bắt đầu lúc 09:12 và vẫn đang diễn ra. Tôi sẽ cập nhật mỗi 30 phút.
3. **Formal** — "Root cause has been identified as a misconfigured firewall rule. Service was restored at 10:05." → Nguyên nhân gốc là một luật firewall cấu hình sai. Dịch vụ khôi phục lúc 10:05.
4. **Informal** — "Heads up: link to the DC is flapping. Looking into it now." → Báo nhanh: đường lên trung tâm dữ liệu đang chập chờn, tôi đang xem.
5. **Informal** — "We're back up. Packet loss is down to zero." → Đã lên lại rồi, mất gói về 0.

### Yêu cầu (Requesting)

6. **Formal** — "I would like to request a change window on [Saturday] from [22:00] to [00:00]." → Tôi xin đăng ký khung giờ thay đổi vào [thứ Bảy] từ [22:00] đến [00:00].
7. **Formal** — "Could you please approve the firewall rule change described in ticket [NET-1042]?" → Anh/chị duyệt giúp thay đổi firewall trong ticket [NET-1042] được không ạ?
8. **Formal** — "We need the source IP, destination IP, port and protocol before we can open the rule." → Chúng tôi cần IP nguồn, IP đích, cổng và giao thức trước khi mở luật.
9. **Informal** — "Can you run a traceroute and paste the output here?" → Chạy traceroute rồi dán kết quả vào đây giúp mình nhé.
10. **Informal** — "Mind if I bounce the switch port? It'll drop you for about ten seconds." → Mình reset cổng switch nhé, bạn sẽ mất mạng khoảng mười giây.

### Giải thích (Explaining)

11. **Formal** — "The slowdown is caused by congestion on the WAN link, not by your laptop." → Việc chậm là do nghẽn đường WAN, không phải do máy của anh/chị.
12. **Formal** — "To put it simply, the data has to travel further, so each request takes longer." → Nói đơn giản, dữ liệu phải đi xa hơn nên mỗi yêu cầu mất nhiều thời gian hơn.
13. **Formal** — "This is a temporary workaround. The permanent fix is scheduled for [date]." → Đây là giải pháp tạm. Cách khắc phục lâu dài dự kiến vào [ngày].
14. **Informal** — "Basically, the VLAN wasn't allowed on the trunk, so traffic never left the switch." → Về cơ bản, VLAN chưa được cho phép trên trunk nên traffic không ra khỏi switch.
15. **Informal** — "Think of the VLAN as a separate hallway in the same building." → Cứ hình dung VLAN như một hành lang riêng trong cùng toà nhà.

### Xử lý sự cố (Troubleshooting)

16. **Formal** — "Could you confirm whether the issue affects all users or only your device?" → Anh/chị xác nhận giúp sự cố ảnh hưởng tất cả mọi người hay chỉ máy của anh/chị?
17. **Formal** — "We have escalated the case to the ISP and are waiting for their response." → Chúng tôi đã chuyển vụ việc lên nhà mạng và đang chờ phản hồi.
18. **Informal** — "Let's rule out DNS first. Can you ping 8.8.8.8 and tell me what you get?" → Loại trừ DNS trước đã. Bạn ping 8.8.8.8 rồi báo kết quả nhé.
19. **Informal** — "I've rolled the config back, can you try again?" → Mình đã hoàn tác cấu hình, bạn thử lại xem.
20. **Informal** — "It's working on my end. Let's check whether it's a local cache issue." → Bên mình chạy ổn. Kiểm tra xem có phải lỗi cache máy bạn không.

> **Lỗi lịch sự thường gặp:** người Việt hay dịch thẳng "Bạn làm sai rồi" thành *"You did it wrong"*. Với khách nước ngoài, câu này rất nặng. Hãy nói **"It looks like the setting may not have been applied yet"** — cùng nội dung, nhưng không đổ lỗi. Tương tự, thay *"That's not my problem"* bằng **"That's outside my area, but I'll connect you with the right team."**

---

## 3. Tình huống thực tế (Real-world Scenarios)

### Kịch bản 1 — Người dùng gọi báo mạng chậm

*Bối cảnh: Một nhân viên kế toán ở Singapore gọi vào helpdesk, phàn nàn mạng chậm. Bạn không nhìn thấy máy của họ.*

**User:** Hi, the network is really slow today. I can't even open the ERP system.
**Admin:** Sorry about that. Let me help you narrow it down. Is it slow for everything, or only the ERP?
**User:** Mainly the ERP. Email seems fine.
**Admin:** Good, that tells me the internet link is probably healthy. Are you on Wi-Fi or a cable?
**User:** Wi-Fi, in meeting room 3.
**Admin:** Could you plug into the wall port for one minute and try again? That will rule out wireless interference.
**User:** Okay… it's much faster on cable.
**Admin:** Thanks for testing. So the ERP is fine, the problem is wireless coverage in that room. I'll raise a ticket to add an access point there.
**User:** How long will that take?
**Admin:** The survey is this week and installation next Tuesday. Until then, the cable will give you full speed.

### Kịch bản 2 — Mô tả sự cố qua điện thoại, không có sơ đồ

*Bối cảnh: Bạn gọi cho kỹ sư trực đêm ở nước ngoài. Cả hai không mở được sơ đồ mạng, nên phải mô tả bằng lời.*

**Admin (VN):** Thanks for picking up. I'll describe the topology because I can't share my screen right now.
**Engineer:** Go ahead, I'll take notes.
**Admin (VN):** We have one FortiGate 100F at the edge, two WAN links, primary fiber and a 4G backup. Behind it, a Cisco core switch, then four access switches.
**Engineer:** Understood. Where is the failure?
**Admin (VN):** The primary fiber is up physically, the interface shows green, but we have 30% packet loss beyond the ISP gateway.
**Engineer:** So it fails at the first hop outside your network?
**Admin (VN):** Exactly. Traceroute stops at hop two, which is the ISP side.
**Engineer:** Then it's not your firewall. Did failover to 4G trigger?
**Admin (VN):** No, because the link never went fully down. That is the second issue I want to fix.
**Engineer:** Right. Open a ticket with the ISP now, and let's tune the SLA probe so partial loss also triggers failover.

### Kịch bản 3 — Xin change window để sửa firewall rule

*Bối cảnh: Họp ngắn với IT Manager để xin phê duyệt sửa luật firewall trên FortiGate.*

**Admin:** I'd like to request a change window this Saturday, 22:00 to 00:00.
**Manager:** What exactly are you changing?
**Admin:** Three firewall rules on the FortiGate. Two are obsolete and will be removed, one will be tightened from any-to-any down to a single port.
**Manager:** What's the risk if it goes wrong?
**Admin:** Worst case, the payroll server loses access to the database for a few minutes. The rollback plan is to restore the configuration backup taken at 21:55.
**Manager:** How long does a rollback take?
**Admin:** Under five minutes, and I'll verify with a test connection immediately after each rule.
**Manager:** Who is on standby?
**Admin:** Myself and one colleague on call. I'll send the completion report by 00:30.
**Manager:** Approved. Please notify the finance team on Friday so nobody is surprised.

### Kịch bản 4 — Thảo luận nội bộ về VLAN cho văn phòng mới

*Bối cảnh: Team network họp thiết kế VLAN cho chi nhánh mới trước khi đặt thiết bị Ubiquiti.*

**Lead:** Let's finalise the VLAN plan for the new branch before we order the Ubiquiti gear.
**Admin A:** I propose four VLANs: staff, guest, voice and CCTV.
**Admin B:** Do we need a separate VLAN for the printers?
**Admin A:** I'd keep printers on the staff VLAN. Fewer subnets, less routing to maintain.
**Lead:** Agreed. What subnet size?
**Admin A:** A /24 each. That's 254 hosts, more than enough for 60 people.
**Admin B:** And the guest VLAN must not reach anything internal.
**Lead:** Correct, guest traffic goes straight out through NAT, with a bandwidth limit of 20 Mbps.
**Admin A:** I'll write the switch configuration and put the uplinks in trunk mode.
**Lead:** Please document the plan today so the installation team can follow it on site.

### Kịch bản 5 — Escalation khi VPN sập nhiều lần

*Bối cảnh: VPN site-to-site giữa hai chi nhánh rớt lặp lại. Bạn phải escalate lên vendor support.*

**Admin:** We're opening a P2 case. The site-to-site VPN between Hanoi and Bangkok has dropped five times in 24 hours.
**Vendor:** Can you confirm the firmware version on both firewalls?
**Admin:** Both are pfSense 2.7.2, identical configuration.
**Vendor:** Does the tunnel rebuild automatically?
**Admin:** Yes, but it takes about 90 seconds, and users lose their sessions each time.
**Vendor:** Have you checked the logs around the drop?
**Admin:** We see a phase 2 rekey failure each time, always at the same interval.
**Vendor:** That points to a lifetime mismatch. Please send both configs and the logs from the last two events.
**Admin:** Sending now. What response time should we expect on a P2?
**Vendor:** Four business hours. If it drops again before then, reply to the same case and we'll raise it to P1.

### Kịch bản 6 — Báo cáo trạng thái trong daily standup

*Bối cảnh: Standup buổi sáng, mỗi người báo cáo ngắn gọn dưới hai phút.*

**Lead:** Network team, what's your status?
**Admin:** Yesterday I finished the switch firmware upgrade on floors two and three. No incidents overnight.
**Lead:** Any impact on users?
**Admin:** Two minutes of downtime per switch, done after 21:00, so nobody noticed.
**Lead:** What's next?
**Admin:** Today I'm reviewing the firewall rule base. We have around 40 rules that haven't matched any traffic in six months.
**Lead:** Are you removing them straight away?
**Admin:** No, I'll disable them first and wait a week. Safer than deleting.
**Lead:** Good. Any blockers?
**Admin:** One. I still need the ISP contact for the Bangkok line. Could you share it after the call?

### Kịch bản 7 — Giải thích cho khách hàng vì sao mạng chậm mà không đổ lỗi

*Bối cảnh: Khách hàng nước ngoài khó chịu vì hệ thống chậm và nghĩ lỗi thuộc về đội IT.*

**Client:** Your network has been terrible all week. What are you doing about it?
**Admin:** I understand how frustrating that is. Let me share what we've measured so far.
**Client:** Please do.
**Admin:** Latency inside the office is normal, around 2 ms. The delay appears once traffic reaches the application, which is hosted in Europe.
**Client:** So it's not the office network?
**Admin:** The office link is part of the path, but it isn't the bottleneck. Distance and the application response time account for most of the delay.
**Client:** Then what can we actually do?
**Admin:** Two options. Short term, we prioritise that application on the WAN so it isn't competing with backups. Long term, we look at a regional instance closer to you.
**Client:** How much improvement will the short-term fix give?
**Admin:** Based on our test, roughly 20 to 30 percent. I'd rather be honest than promise more.
**Client:** Fair enough. Send me the plan in writing.
**Admin:** I'll have it in your inbox before the end of the day.

> **Ghi chú:** Trong kịch bản 7, người nói KHÔNG nói *"It's not our fault"*. Thay vào đó dùng dữ liệu ("latency is 2 ms inside the office") rồi đưa lựa chọn. Đây là cách giữ uy tín mà không làm khách mất mặt.

---

## 4. Email mẫu (Email Templates)

### 4.1 Incident notification

```text
Subject: [INCIDENT] [P1] Network outage affecting [SITE_NAME]

Dear all,

We are currently experiencing a network outage affecting [SITE_NAME].

Start time:        [START_TIME] [TIMEZONE]
Impacted services: [SERVICE_LIST]
Impacted users:    [USER_COUNT] users at [LOCATION]
Current status:    Under investigation

What we know so far:
[SHORT_TECHNICAL_SUMMARY]

What we are doing:
[ACTION_1]
[ACTION_2]

Workaround: [WORKAROUND_OR_"None available at this time"]

The next update will be sent at [NEXT_UPDATE_TIME] or earlier if the
situation changes.

Best regards,
[YOUR_NAME]
Network Operations, [COMPANY]
```

### 4.2 Maintenance announcement

```text
Subject: [SCHEDULED MAINTENANCE] [SYSTEM_NAME] on [DATE], [START_TIME]-[END_TIME]

Dear colleagues,

We will perform scheduled maintenance on [SYSTEM_NAME].

Date:            [DATE]
Change window:   [START_TIME] - [END_TIME] [TIMEZONE]
Expected impact: [DOWNTIME_MINUTES] minutes of interruption
Affected sites:  [SITE_LIST]

Purpose of the change:
[REASON, e.g. firmware upgrade to fix a known VPN stability issue]

During the window you may experience:
- Loss of VPN connectivity
- Brief interruption of internet access

Rollback plan: the configuration backup taken at [BACKUP_TIME] will be
restored if any verification step fails.

If you have a critical activity in this window, please reply before
[DEADLINE] so we can reschedule.

Best regards,
[YOUR_NAME]
```

### 4.3 Status report

```text
Subject: [WEEKLY NETWORK REPORT] Week [WEEK_NUMBER], [DATE_RANGE]

Hi [MANAGER_NAME],

Here is the network status report for [DATE_RANGE].

Availability
- WAN primary link: [PERCENT]% (SLA target [SLA_TARGET]%)
- VPN tunnels:      [PERCENT]%

Incidents
- [INCIDENT_ID] [SHORT_TITLE] - [DURATION], resolved, root cause: [CAUSE]
- [INCIDENT_ID] [SHORT_TITLE] - [DURATION], resolved, root cause: [CAUSE]

Performance
- Average latency to [REGION]: [VALUE] ms
- Peak bandwidth usage:        [VALUE] Mbps of [CAPACITY] Mbps
- Packet loss (worst day):     [VALUE]%

Completed this week
- [TASK_1]
- [TASK_2]

Planned for next week
- [TASK_3]
- [TASK_4]

Risks and requests
- [RISK_OR_REQUEST]

Best regards,
[YOUR_NAME]
```

### 4.4 Access request

```text
Subject: [ACCESS REQUEST] Firewall rule for [APPLICATION_NAME]

Hi [APPROVER_NAME],

I would like to request a new firewall rule for [APPLICATION_NAME].

Requested by:  [REQUESTER_NAME], [DEPARTMENT]
Business need: [BUSINESS_JUSTIFICATION]

Rule details
- Source:      [SOURCE_IP_OR_GROUP]
- Destination: [DESTINATION_IP]
- Port:        [PORT_NUMBER]
- Protocol:    [TCP/UDP]
- Direction:   [INBOUND/OUTBOUND]
- Duration:    [PERMANENT / UNTIL_DATE]

Security note: access is restricted to a single host and port. No
any-to-any rule is required.

Could you please approve or comment by [DEADLINE]? I will implement the
change in the next change window on [WINDOW_DATE].

Best regards,
[YOUR_NAME]
```

### 4.5 Resolution confirmation

```text
Subject: [RESOLVED] [INCIDENT_ID] - [SHORT_TITLE]

Dear all,

The incident affecting [SERVICE_NAME] has been resolved.

Incident ID:   [INCIDENT_ID]
Start time:    [START_TIME]
Restored at:   [END_TIME]
Total duration:[DURATION]

Root cause:
[ROOT_CAUSE_EXPLANATION]

Resolution:
[WHAT_WAS_DONE_TO_FIX_IT]

Preventive actions:
- [ACTION_1] - owner [NAME], due [DATE]
- [ACTION_2] - owner [NAME], due [DATE]

Please let us know if you still see any issue with [SERVICE_NAME].
Thank you for your patience during the incident.

Best regards,
[YOUR_NAME]
Network Operations, [COMPANY]
```

---

## 5. Bài tập thực hành (Practice Exercises)

### 5.1 Điền từ vào chỗ trống (10 câu)

Từ gợi ý: *latency, packet loss, change window, subnet, trunk, gateway, failover, rollback, throughput, escalate*

1. We are seeing 8% ________ on the WAN interface, so voice calls are breaking up.
2. Please configure the uplink as a ________ port so it can carry VLAN 10 and 20.
3. The default ________ stopped responding, so no traffic can leave the office.
4. I would like to book a ________ on Saturday night to upgrade the firmware.
5. If the verification fails, we will follow the ________ plan and restore the backup.
6. ________ to Tokyo increased from 60 ms to 310 ms after the ISP changed the route.
7. The link is rated at 200 Mbps, but real ________ is only 40 Mbps.
8. Each branch office uses its own ________, for example 10.20.30.0/24.
9. The secondary ISP took over automatically, so ________ worked as designed.
10. If the vendor does not reply within four hours, we will ________ the case to P1.

### 5.2 Matching thuật ngữ ↔ định nghĩa (10 cặp)

| # | Term | | Letter | Definition |
| --- | --- | --- | --- | --- |
| 1 | VLAN | | A | An ordered list of permit or deny statements |
| 2 | NAT | | B | The delay before data reaches its destination |
| 3 | ACL | | C | A logical network separating traffic on one physical switch |
| 4 | DHCP | | D | An encrypted tunnel between two sites |
| 5 | Jitter | | E | Translating private addresses into public ones |
| 6 | Latency | | F | A tool that shows every hop along a path |
| 7 | Site-to-site VPN | | G | The service that assigns IP addresses automatically |
| 8 | Traceroute | | H | The agreed level of service quality |
| 9 | SLA | | I | Variation in delay that harms voice and video |
| 10 | Uptime | | J | How long a device has run without failure |

### 5.3 Viết lại câu dùng từ cho trước (5 câu)

1. "The internet is broken." → viết lại lịch sự, dùng **experiencing**.
2. "You configured it wrong." → viết lại không đổ lỗi, dùng **may not have been applied**.
3. "I want to change the firewall on Saturday." → viết lại trang trọng, dùng **request a change window**.
4. "It's not our fault, it's the ISP." → viết lại trung lập, dùng **the issue appears to originate**.
5. "We fixed it." → viết lại cho email chính thức, dùng **service was restored at**.

### 5.4 Role-play

*Bạn là network administrator. Đồng nghiệp đóng vai giám đốc chi nhánh nước ngoài đang bực bội vì Wi-Fi phòng họp rớt liên tục trong buổi họp với khách hàng.*

Nhiệm vụ của bạn trong 8 lượt trao đổi:
1. Xin lỗi ngắn gọn và ghi nhận ảnh hưởng.
2. Hỏi hai câu để khoanh vùng (chỉ phòng họp đó hay cả tầng? có dây mạng dự phòng không?).
3. Đưa một giải pháp tạm thời dùng được ngay.
4. Giải thích nguyên nhân bằng ngôn ngữ phi kỹ thuật, KHÔNG đổ lỗi cho người dùng.
5. Cam kết mốc thời gian cụ thể và cách bạn sẽ cập nhật.

<details>
<summary>Đáp án</summary>

**5.1 Điền từ**
1. packet loss — 2. trunk — 3. gateway — 4. change window — 5. rollback — 6. Latency — 7. throughput — 8. subnet — 9. failover — 10. escalate

**5.2 Matching**
1-C, 2-E, 3-A, 4-G, 5-I, 6-B, 7-D, 8-F, 9-H, 10-J

**5.3 Viết lại câu** (gợi ý, các cách diễn đạt tương đương đều chấp nhận được)
1. "We are currently experiencing an internet connectivity issue."
2. "It looks like the setting may not have been applied yet."
3. "I would like to request a change window on Saturday from 22:00 to 00:00."
4. "Based on our tests, the issue appears to originate outside our network, at the ISP level."
5. "Service was restored at 10:05 ICT."

**5.4 Role-play — mẫu mở đầu**
- "I'm sorry the Wi-Fi disrupted your meeting. Let me get this sorted quickly."
- "Two quick questions: is it only meeting room 3, or the whole floor? And is there a wall port in the room?"
- "For the rest of today, please use the cable in the room. It bypasses the wireless issue completely."
- "The room sits at the edge of the coverage area, so the signal weakens when several laptops connect at once. Nothing you did caused it."
- "I'll run a wireless survey tomorrow morning and send you the result by 16:00, with a date for the new access point."

</details>
