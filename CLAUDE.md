# Project: My First Project

โปรเจคทดลองใช้ Claude Code — สร้าง slash command, skill, sub-agent ระหว่างเรียน LTD AI 101

## กฎ

- ขออนุญาตก่อนแก้ไฟล์เยอะหรือลบของ
- ห้ามรัน rm -rf หรือลบ folder โดยไม่ถาม
- ห้ามแก้ไฟล์นอก folder นี้
- ตอบตรง กระชับ

## โครงสร้าง

- `sources/<TICKER>/` — 10-K และ earnings transcript
- `briefs/` — stock brief output
- `.claude/commands/` — slash commands
- `.claude/templates/` — output templates

## Investment voice (ใช้กับ /brief และ company-brief skill)

ลงทุนระยะยาว 3 ปีขึ้นไป สนใจบริษัทที่พื้นฐานมั่นคง รายได้สม่ำเสมอ กำไรโต และเข้าใจว่าลูกค้าคือใคร
หลีกเลี่ยงหุ้นที่ผูกกับ macro — ถ้าเศรษฐกิจแย่แล้วพังทันทีไม่เอา
ก่อนซื้อต้องตอบได้ว่า "เงื่อนไขอะไรที่จะทำให้ขายทิ้ง" — ถ้าตอบไม่ได้ยังไม่ซื้อ
Skill `company-brief` ต้องสะท้อนเสียงนี้ใน Bull/Bear, Kill conditions, และ "What to ask"
