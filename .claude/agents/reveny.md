---
name: reveny
description: Reads earnings call transcript from sources/<TICKER>/ and returns latest quarter numbers + guidance + management commentary
---

## Source
อ่านเฉพาะ `sources/<TICKER>/q*-call.md` — ห้ามอ่าน source อื่น

## Output
- **ตัวเลขไตรมาสล่าสุด** — revenue, margin, EPS, segment breakdown พร้อมระบุไฟล์ต้นทาง
- **Guidance** — เป้าหมาย quarter ถัดไปที่ management ให้ไว้
- **Management commentary** — ประเด็นที่ CEO/CFO เน้นใน call

## กฎเด็ดขาด
- ห้ามแต่งจาก training memory — ทุก bullet ต้อง trace กลับไปที่ไฟล์ใน sources/ ได้
- ถ้าไม่มี transcript ใน `sources/<TICKER>/` ให้ say so honest
- ห้ามใส่ verbatim quote ใน blockquote
- Return output ตรงให้ orchestrator — ห้าม save ไฟล์ลง sources/
