---
description: เพิ่มหุ้นที่มี brief แล้วเข้า showcase/index.html อัตโนมัติ (card + section + CSS color + header count)
---

You are running /add-to-showcase. ถ้าไม่มี TICKER ให้ถามก่อน

## ขั้นตอนที่ 1 — Validate

1. ถ้าไม่มี TICKER ให้ถามก่อน ไม่ทำอะไรจนกว่าจะได้ ticker
2. ตรวจว่า `briefs/<TICKER>.md` มีอยู่ ถ้าไม่มีให้บอก user: "ยังไม่มี brief ของ TICKER — รัน /brief TICKER ก่อนครับ"
3. อ่าน `showcase/index.html` ตรวจว่า `id="<lowercase-ticker>"` **ยังไม่มี** ถ้ามีแล้วให้บอก user และหยุด

## ขั้นตอนที่ 2 — Parse briefs/<TICKER>.md

อ่านไฟล์แล้ว extract ข้อมูลต่อไปนี้:

- **ticker** — uppercase เช่น AAPL
- **lowercase** — lowercase เช่น aapl
- **full_name** — จาก h1 บรรทัดแรก: `# AAPL — Apple Inc.` → "Apple Inc."
- **brief_date** — จาก `_Brief date: YYYY-MM-DD_` หรือ `*Brief date: YYYY-MM-DD*` หรือ `*Brief date: YYYY-MM-DD | ...*`
- **card_preview** — ย่อหน้าแรกของ section Company snapshot ตัดที่ ~120 ตัวอักษร ไม่ตัดกลางคำ

## ขั้นตอนที่ 3 — เลือก accent color

ใช้ palette นี้:
- MSFT → #00a4ef
- GOOGL หรือ GOOG → #4285f4
- META → #0668e1
- AMZN → #ff9900
- NFLX → #e50914

ถ้า ticker ไม่อยู่ใน list: ดูสีที่ถูกใช้ใน showcase แล้ว เลือกสีจาก list ที่ยังไม่ถูกใช้:
`#2563eb`, `#059669`, `#d97706`, `#7c3aed`, `#db2777`, `#0891b2`
ถ้าหมดทั้ง list ใช้ `#555555`

## ขั้นตอนที่ 4 — แปลง brief เป็น HTML

### Gallery card (insert ก่อน `</div>` ปิดของ `<div class="gallery">`)
```html

  <a class="card" href="#LOWERCASE">
    <div class="card-ticker">TICKER</div>
    <div class="card-date">BRIEF_DATE</div>
    <div class="card-preview">CARD_PREVIEW</div>
  </a>
```

### Brief section (insert ก่อน `</body>`)
```html


<!-- ════════════════════════════════════
     TICKER
════════════════════════════════════ -->
<section class="brief" id="LOWERCASE">
  <div class="brief-heading">
    <h2>TICKER &mdash; FULL_NAME</h2>
    <span class="brief-date">BRIEF_DATE</span>
    <a class="back-link" href="#top">&uarr; กลับด้านบน</a>
  </div>

  [แปลงแต่ละ section จาก markdown ตาม mapping ด้านล่าง]

  <p class="disclaimer">ไม่ใช่คำแนะนำการลงทุน &mdash; เป็น research summary เพื่อการศึกษา</p>
</section>
```

### Markdown → HTML mapping

**Section 1 — Company snapshot:**
```html
<h3>1. Company snapshot</h3>
<p>...paragraph text...</p>
```

**Section 2 — Fundamentals signal:**
```html
<h3>2. Fundamentals signal</h3>
<ul>
  <li><strong>Label:</strong> text</li>
</ul>
```

**Section 3 — Latest earnings:**
- ถ้ามีบรรทัดที่ขึ้นต้นด้วย `⚠️` หรือ `ไม่มี earnings` ให้ใส่ `<div class="warn">&#9888; ...text...</div>` ก่อน `<ul>`
- ถ้ามี transcript จริง ใส่ `<p><strong>Qx FYxxxx ...</strong></p>` แทน
```html
<h3>3. Latest earnings</h3>
<div class="warn">&#9888; ...warning text...</div>   <!-- ถ้ามี warning -->
<ul>
  <li>...bullet... <span class="src">(source: ...)</span></li>
</ul>
```

**Section 4 — Bull case / Bear case:**
```html
<h3>4. Bull case / Bear case</h3>
<div class="bb-grid">
  <div class="bull">
    <div class="bb-label">Bull</div>
    <ul>
      <li>...bullet...</li>
    </ul>
  </div>
  <div class="bear">
    <div class="bb-label">Bear</div>
    <ul>
      <li>...bullet...</li>
    </ul>
  </div>
</div>
```

**Section 5 — Kill conditions (1 `<div class="kill">` ต่อ 1 bullet):**
```html
<h3>5. Kill conditions</h3>
<div class="kill"><strong>condition title</strong> &mdash; explanation</div>
<div class="kill"><strong>condition title</strong> &mdash; explanation</div>
```

**Section 6 — What to ask before owning it:**
```html
<h3>6. What to ask before owning it</h3>
<ol>
  <li>...question...</li>
</ol>
```

### Text conversion rules (ใช้ทุก section)
- `**text**` → `<strong>text</strong>`
- `→` → `&rarr;`
- ` — ` (em dash) → ` &mdash; `
- `"text"` (curly quotes) → `&ldquo;text&rdquo;`
- `(source: ...)` inline → `<span class="src">(source: ...)</span>`
- `&` → `&amp;`

## ขั้นตอนที่ 5 — อัปเดต 3 จุดใน showcase/index.html

1. **CSS color rule** — insert หลังบรรทัดสุดท้ายของ `.card[href="..."] .card-ticker { color: ... }` block:
   ```css
   .card[href="#LOWERCASE"] .card-ticker { color: CHOSEN_COLOR; }
   ```

2. **Header ticker count** — หา `N tickers &middot;` ใน `.site-header p` แล้วเปลี่ยน N เป็น N+1

3. **Header date** — หา `อัปเดต YYYY-MM-DD` แล้วเปลี่ยนเป็นวันนี้ (today's date จาก system)

## สรุปสิ่งที่ต้องทำใน showcase/index.html (5 edits)

| # | จุดที่แก้ | action |
|---|---|---|
| 1 | CSS block `.card[href="..."]` | เพิ่ม color rule ใหม่ |
| 2 | `.site-header p` | +1 ticker count |
| 3 | `.site-header p` | อัปเดต date |
| 4 | `<div class="gallery">` | เพิ่ม card ก่อน `</div>` |
| 5 | ก่อน `</body>` | เพิ่ม brief section |

## สิ่งที่ต้องแจ้ง user เมื่อเสร็จ

บอก ticker ที่เพิ่ม, brief date, และสี accent ที่ใช้ เช่น:
"เพิ่ม MSFT เข้า showcase แล้วครับ (date: 2026-06-12, color: #00a4ef)"
