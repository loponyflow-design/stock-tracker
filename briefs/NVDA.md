# NVDA — NVIDIA Corporation
*Brief date: 2026-06-12 | Source: 10-K FY2026 + Web search*

---

## 1. Company Snapshot

NVIDIA ออกแบบ GPU, CPU, DPU และ software สำหรับ AI และ accelerated computing แล้วจ้าง TSMC/Samsung ผลิตให้ (fabless) ลูกค้าหลักคือ cloud providers ขนาดใหญ่ เช่น Microsoft, Amazon, Google ที่นำ GPU ไปสร้าง AI infrastructure ให้ลูกค้าของตัวเอง รายได้ 90% มาจาก Data Center — ใครก็ตามที่ต้องการรัน AI model ขนาดใหญ่ ณ วันนี้แทบหนีไม่พ้นต้องผ่าน NVIDIA ปัจจุบัน platform CUDA มีนักพัฒนาใช้อยู่กว่า 7.5 ล้านคนทั่วโลก ซึ่งเป็น switching cost ที่สร้างมานานกว่า 20 ปี

---

## 2. Fundamentals Signal

- **Revenue เติบโตต่อเนื่อง 3 ปีซ้อน**: $60.9B → $130.5B → $215.9B — absolute dollar growth สูงมาก (+$85B ในปีเดียว) แต่อัตราเร่งเริ่มชะลอตามฐานที่ใหญ่ขึ้น
- **Q1 FY2027 ล่าสุด (เม.ย. 2026)**: revenue $81.6B +85% YoY +20% QoQ — ยังไม่มีสัญญาณชะลอในระยะสั้น
- **Gross margin หดจาก 75% → 71%** ใน FY2026 เพราะ 2 สาเหตุชั่วคราว: H20 China ban ($4.5B charge) + transition cost จาก Hopper → Blackwell — operating margin ยังอยู่ที่ 60%+ ซึ่งสูงมาก
- **FCF แข็งมาก**: $27B → $61B → $97B สามปีต่อเนื่อง — แปลงรายได้เป็นเงินสดได้ดีมาก
- **Balance sheet ซับซ้อนขึ้น**: net cash $54B แต่ goodwill พุ่ง $14.4B (Groq deal) + non-marketable equity $22.3B (ลงทุน private companies) + purchase obligations $95.2B — assets หลายก้อนประเมินมูลค่าจริงได้ยาก

---

## 3. Latest Earnings

ไม่มี earnings call transcript ใน `sources/NVDA/` — ข้อมูลด้านล่างมาจาก web search เท่านั้น ควรตรวจสอบกับ transcript จริงก่อนตัดสินใจ

- Q1 FY2027 (ended Apr 26, 2026): revenue $81.6B — record quarter +85% YoY, +20% QoQ (source: web/SEC 8-K)
- ประกาศ buyback เพิ่มอีก $80B และเพิ่ม dividend จาก $0.01 → $0.25/หุ้น/ไตรมาส (+25x) (source: web)
- S&P Global ปรับ credit rating ขึ้น อ้างถึง "insatiable demand" สำหรับระบบ AI (source: web)
- SharonAI ประกาศ deal 6 ปีกับ NVIDIA — deploy GB300 GPUs 40,000 ตัวในออสเตรเลีย (source: web)

---

## 4. Bull Case / Bear Case

**Bull Case**
- CUDA ecosystem ที่สะสมมา 20 ปีสร้าง switching cost แท้จริง — 7.5M+ developers เขียน code สำหรับ CUDA โดยตรง การ migrate ออกต้องใช้เวลาและเงินมหาศาล
- ทุก AI model ขนาดใหญ่ที่ train อยู่วันนี้ใช้ NVIDIA — ยิ่งโลกลงทุน AI มากขึ้น demand GPU ก็เพิ่มตาม
- Platform cadence ปีละรุ่น (Blackwell → Rubin H2 FY2027) + full-stack ตั้งแต่ chip ถึง software ทำให้ยาก disrupt

**Bear Case**
- **รายได้ผูกกับ AI capex ของ CSP โดยตรง** — ถ้า Microsoft, Amazon, Google ลด spending แม้แค่ไตรมาสเดียว NVIDIA กระทบหนัก นี่คือจุดที่บริษัทนี้ผูกกับ macro มากกว่าที่เห็นจากภายนอก
- **China market ปิดตัวอย่างมีนัยสำคัญ** — ยิ่งนาน Huawei และ local chip makers ยิ่งสร้าง ecosystem แทนได้ โอกาสกลับตลาดที่ใหญ่ที่สุดในโลกยากขึ้นทุกวัน
- **Customer concentration สูงผิดปกติ** — 2 ลูกค้า = 36% revenue ถ้าใครสักคนพัฒนา chip เองสำเร็จ (Amazon Trainium, Google TPU, Microsoft Maia) impact ทันที

---

## 5. Kill Conditions

ถ้าเห็นสิ่งเหล่านี้เกิดขึ้น ควรทบทวนจุดยืนทันที:

- **CSP หลัก 1-2 ราย ลด AI capex guidance อย่างมีนัยสำคัญ** — รายได้ NVIDIA กระจุกที่ลูกค้ากลุ่มนี้ ถ้าพวกเขาชะลอ NVIDIA โดนก่อนใคร
- **Gross margin หลุดต่ำกว่า 65% ติดต่อกัน 2 ไตรมาสโดยไม่มี one-time ชัดเจน** — สัญญาณ pricing power ลดลงจากการแข่งขัน (AMD, custom ASIC จาก CSP)
- **CUDA ecosystem เริ่ม fragment** เช่น framework หลักอย่าง PyTorch หรือ JAX ย้าย default support hardware อื่น — switching cost ที่แท้จริงของ NVIDIA อยู่ที่ CUDA ไม่ใช่ hardware เพียงอย่างเดียว

---

## 6. What to Ask Before Owning It

1. **ถ้า AI capex cycle ชะลอลงในปีหน้า คุณจะถือ NVDA ต่อหรือเปล่า?** — NVIDIA ขึ้นกับ spending ของ hyperscaler โดยตรง ถ้าตอบยังไม่ชัด แสดงว่า sell condition ยังไม่ถูก define
2. **revenue $215B มาจากลูกค้ากี่ราย?** — 2 ราย = 36% ถ้าคนใดคนหนึ่งพัฒนา chip เองสำเร็จ กระทบแค่ไหน
3. **Groq deal $13B cash + goodwill $14.4B — ถ้า integrate ไม่สำเร็จและต้อง write-off คุณยังถือต่อไหม?** — ใหญ่พอกระทบ EPS หลายปีได้
4. **China market ถูก ban — จะกลับมาได้ไหมภายในกรอบที่คุณถือหุ้น?** — ถ้าตลาดจีนปิดถาวร Huawei ecosystem จะใหญ่แค่ไหนใน 3 ปีข้างหน้า
5. **หุ้นนี้ผูกกับ macro หรือเปล่า?** — NVDA ไม่ใช่บริษัทที่รายได้สม่ำเสมอไม่ขึ้นกับสภาพแวดล้อม ถ้าเศรษฐกิจชะลอและ hyperscaler freeze capex คุณยังสบายใจถือ 3 ปีได้จริงไหม

---

*ไม่ใช่คำแนะนำซื้อขาย — เป็น research summary เท่านั้น*
