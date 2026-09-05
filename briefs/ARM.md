# ARM — Arm Holdings plc
_Brief date: 2026-06-21_

---

## 1. Company snapshot

Arm ออกแบบสถาปัตยกรรมและ design ของ CPU/GPU แล้ว **ขายสิทธิ์ (license) ให้บริษัทชิปทั่วโลก** อย่าง Apple, Qualcomm, Nvidia และ cloud providers เอาไปสร้างชิปเอง — Arm ไม่ผลิตชิปเอง รายได้มาจาก 2 ทาง: ค่า license ล่วงหน้า + **royalty ต่อชิปทุกตัวที่ลูกค้าขายออกไป** ทำให้ gross margin สูงถึง 98% Arm ครองตลาด mobile processor เกือบเบ็ดเสร็จ (สะสมชิปที่ใช้ Arm กว่า 350 พันล้านตัว) และกำลังขยายสู่ data center/AI — SoftBank ถือหุ้น ~90% (free float ต่ำมาก)

---

## 2. Fundamentals signal

- **Revenue โต 3 ปีติด >20%:** $3.2B → $4.0B → $4.9B (FY2026 +23%) — เป็นการเติบโตที่สม่ำเสมอ ไม่ใช่ครั้งเดียว
- **Royalty $2.6B (53% ของรายได้, +21%):** หนุนโดย Armv9 + CSS ที่ royalty rate ต่อชิปสูงขึ้น — รายได้ recurring คุณภาพดีที่โตโดยไม่ต้องหาลูกค้าใหม่
- **Gross margin 98%** — โมเดล IP บริสุทธิ์ ต้นทุนผลิตแทบเป็นศูนย์
- **แต่ R&D = 56% ของรายได้และเร่งตัว** → operating margin แค่ 18% (ลดจาก 21%) — กำไรโตช้ากว่ารายได้เพราะลงทุนหนัก
- **งบแข็งมาก:** cash + ST investments ~$3.6B แทบไม่มีหนี้ (asset-light, capex ต่ำ)
- **ยังไม่คืนเงินผู้ถือหุ้น** — ไม่มี dividend/buyback ที่มีนัย เก็บเงินลงทุน growth

---

## 3. Latest earnings

**หมายเหตุ:** ตัวเลขทั้งปี FY2026 มาจาก 20-F ใน `sources/ARM/` ส่วนรายไตรมาส Q4 มาจาก web (ไม่มี transcript ใน sources/)

- FY2026 (สิ้น มี.ค. 2026): revenue $4.92B +23%, royalty $2.61B +21%, license $2.31B +25% (source: sources/ARM/10-k-fy2026.md)
- Q4 FY2026 (ราย 6 พ.ค. 2026): revenue $1,490M +20% — record quarter, license record $819M +29%, royalty $671M +11% (source: web)
- **Data center royalties โตเกิน 2 เท่า YoY** — Graviton/Cobalt/Axion เป็น engine ใหม่จริง (source: web)
- Non-GAAP EPS Q4 $0.60 beat consensus $0.58 — แต่**หุ้นร่วง ~7%** หลังประกาศ (ตลาดกังวล guidance/supply) (source: web)
- เป็นปีที่ 3 ติดต่อกันที่โต >20% นับจาก IPO (ก.ย. 2023) (source: web)

---

## 4. Bull case / Bear case

**Bull**
- **Switching Cost + Scale Economies มหาศาล** — ecosystem, toolchain, developer ที่สะสมหลายสิบปี ย้ายออก = สร้างใหม่ทั้งหมด; Armv9 upgrade cycle ทำให้ royalty/ชิป โตขึ้นโดยไม่ต้องหาลูกค้าใหม่
- **Data center/AI เป็น optionality ที่เริ่มเป็นจริง** — royalty data center โตเกิน 2 เท่า addressable market ใหม่ที่เพิ่งเริ่ม monetize
- รายได้ recurring คุณภาพดี (royalty ต่อชิป) + gross margin 98% + งบไร้หนี้ — ความสามารถทำกำไรระยะยาวสูงถ้าคุม R&D ได้

**Bear**
- **RISC-V (open-source ฟรี ไม่มี royalty)** — ภัยคุกคามเชิงโครงสร้างต่อโมเดล licensing โดยตรง เริ่มจาก IoT/embedded
- **Customer concentration:** top 5 = 57% ของรายได้, Arm China รายเดียว 16% + SoftBank ถือ ~90% — ผูกกับลูกค้า/ผู้ถือหุ้นน้อยราย มี governance overhang
- **Channel conflict:** การทำชิปเอง (Arm AGI ประกาศ มี.ค. 2026) แข่งกับลูกค้าตัวเอง เสี่ยงผลักลูกค้าใหญ่ไป x86/RISC-V
- **ผูกกับ macro:** semiconductor เป็น cyclical + valuation สูงสะท้อน perfect execution; R&D 56% ถ้า growth ชะลอแม้ชั่วคราว margin บีบและราคามักถูกลงโทษแรง (เห็นแล้วจากหุ้นร่วง 7%)

---

## 5. Kill conditions

- **ถ้า RISC-V เริ่มได้ลูกค้า tier-1 จริง** (มือถือหรือ data center รายใหญ่เปลี่ยนไปใช้) — premise switching cost ที่เป็นหัวใจของ bull case พังทันที
- **ถ้า royalty growth ชะลอต่ำกว่า ~10% ต่อเนื่อง ขณะ R&D ยังโต** — operating margin จะถูกบีบจนกำไรไม่โต ทั้งที่ valuation ตั้งบนสมมติฐานโตเร็ว
- **ถ้า production silicon ทำให้ลูกค้ารายใหญ่ (Qualcomm/Nvidia/CSP) ลดการพึ่ง Arm อย่างมีนัย** — customer concentration ที่สูงอยู่แล้วจะกลายเป็นจุดตาย

---

## 6. What to ask before owning it

1. ARM เก็บเงินต่อชิปทุกตัวที่คนอื่นขาย — ถ้าตลาดมือถือ flat ARM จะโตจากอะไร (v9 royalty rate + data center) และโตได้อีกกี่ปีก่อน v9 migration จะอิ่มตัว?
2. RISC-V โตถึงไหนแล้ว — มีลูกค้า tier-1 รายไหนเริ่มเปลี่ยนจริง? นี่คือ kill condition หลักที่ต้องเฝ้า
3. การทำชิปเอง (Arm AGI) จะทำให้ลูกค้าอย่าง Qualcomm/Nvidia/CSP มอง ARM เป็นคู่แข่งไหม — channel conflict กระทบ licensing แค่ไหน?
4. หุ้นนี้ผูก macro (semiconductor cyclical) และเทรดที่ valuation สูง — ถ้า chip downturn มา ผมยังถือ 3 ปีได้สบายใจไหม หรือจะ panic ตอนราคาร่วง?
5. SoftBank ถือ ~90% — ถ้าขายออกหรือเพิ่ม float กระทบราคา/governance ยังไง? และ "เงื่อนไขที่จะทำให้ผมขาย ARM ทิ้ง" คืออะไรกันแน่ — ถ้าตอบไม่ได้ ยังไม่พร้อมซื้อ

---

_ไม่ใช่คำแนะนำการลงทุน — เป็น research summary เพื่อการศึกษา_
