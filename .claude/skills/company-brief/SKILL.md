---
name: company-brief
description: Use when the user asks for a research brief on a public stock (e.g. "/brief AAPL", "ทำ brief NVDA ให้หน่อย", "research TSLA"). Outputs a 6-section markdown brief saved to briefs/<TICKER>.md.
---

# company-brief SOP

## When to use this

ผู้ใช้ขอ research brief ของหุ้น 1 ตัว Trigger ทั่วไป:
- `/brief <TICKER>` slash command
- "ทำ brief หุ้น X ให้หน่อย"
- "ขอข้อมูลย่อๆ ของ <ticker>"

## Inputs you need

- 1 stock ticker (เช่น AAPL, NVDA, GOOGL)
- ถ้าไม่มี ticker ให้ ask before doing anything else

## Steps

1. Confirm the ticker. ถ้า ambiguous ให้ ask user to confirm
2. Read `CLAUDE.md` ที่ root ของ project ใน CLAUDE.md จะมีย่อหน้า investing voice ของ user, output ต้องสะท้อนสไตล์นั้น
3. Dispatch agent ทั้ง 3 ตัวใน **message เดียว (tool call block เดียว)** เพื่อให้รันขนาน (parallel) — ห้าม dispatch ทีละตัวรอผลก่อนแล้วค่อยส่งตัวถัดไป เพราะ source แยกกัน ไม่ต้องรอผลของกัน:
   - **Fundy** — อ่าน `sources/<TICKER>/10-k-*.md` → return Company snapshot + Fundamentals signal
   - **Reveny** — อ่าน `sources/<TICKER>/q*-call.md` → return Latest earnings + Guidance + Management commentary
   - **Weby** — WebSearch → return News 7 วันล่าสุด + Analyst moves + Catalysts
   - ใช้ Agent tool dispatch named subagent โดยระบุ `subagent_type` ตรงกับชื่อ agent และส่ง prompt ที่บอก ticker ให้แต่ละตัว
4. รอผล agent ทั้ง 3 กลับมาครบ แล้ว integrate เป็น brief 6 sections ตาม Output format ด้านล่าง
5. ถ้า folder `briefs/` ยังไม่มี ให้สร้าง
6. Save brief ที่ `briefs/<TICKER>.md` (uppercase ticker)
7. แสดง brief เต็มกลับใน chat ด้วย

## Output format (6 sections, required, no skipping)

### 1. Company snapshot (3-4 ประโยคไทย)
บริษัททำอะไร, ขายให้ใคร, รายได้หลักมาจากไหน ภาษาคนปกติ ไม่เอาคำตลาด

### 2. Fundamentals signal (3-5 bullets)
Revenue trend, margin trend, balance sheet feel, capital allocation pattern เน้น direction มากกว่าตัวเลข

### 3. Latest earnings
3-5 bullets **Source:** อ่านทุกไฟล์ใน sources/<TICKER>/ ก่อนเขียน ถ้า folder ว่างหรือไม่มี เขียนตรงๆ ว่า "ไม่มี earnings transcript ใน sources/<TICKER>/" ห้ามแต่งตัวเลขจากความจำ ทุก bullet ในนี้ต้อง trace กลับไปที่ไฟล์ใน sources/ ได้ และระบุไฟล์ต้นทางใน parens ท้าย bullet เช่น (source: sources/AAPL/q1-2026-call.md)

### 4. Bull case / Bear case
2-3 bullets แต่ละข้าง Bear case ต้อง specific to บริษัทนี้

### 5. Kill conditions (สำคัญ อย่าข้าม)
2-3 bullets "ถ้าเห็นอะไรเกิดขึ้น ควรเลิกถือ"

### 6. What to ask before owning it (3-5 questions)
คำถามที่ beginner ควรตอบให้ได้ก่อนกดซื้อ

## Voice rules

- Tone reflect investing voice ใน `CLAUDE.md` ของ project
- ห้าม ออก buy/sell recommendation
- ห้าม แต่ง verbatim quote ของ executive ใส่ blockquote
- ห้าม ใช้คำว่า "moat" ตรงๆ ใช้ Helmer's 7 Powers ที่ specific แทน
- ห้าม บอกว่า "ตลาดยังไม่ price in"

## When unsure

Honest > confident ถ้าข้อมูลไม่พอ พูดว่า "ผมไม่แน่ใจ ลองดูใน [source]" ดีกว่าแต่ง
