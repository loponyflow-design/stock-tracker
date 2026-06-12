---
description: สร้างไฟล์ sources/<TICKER>/10-k-fy2025.md อัตโนมัติจาก SEC EDGAR (US stocks) หรือ PDF ใน sources/<TICKER>/
---

You are running the /make-10k command. ถ้าไม่มี TICKER ให้ถามก่อน

## ขั้นตอนที่ 1 — เลือก source

### A: หุ้น US → SEC EDGAR (อัตโนมัติ via PowerShell)

ใช้ PowerShell tool รัน command ต่อไปนี้ตามลำดับ:

**1. หา CIK จาก ticker:**
```powershell
$h = @{ "User-Agent" = "MyProject lopony.flow@gmail.com" }
$map = Invoke-RestMethod -Uri "https://www.sec.gov/files/company_tickers.json" -Headers $h
$entry = $map.PSObject.Properties.Value | Where-Object { $_.ticker -eq "<TICKER>" }
$cik = $entry.cik_str.ToString().PadLeft(10, '0')
Write-Output $cik
```

**2. ดึงรายการ filings ล่าสุด:**
```powershell
$h = @{ "User-Agent" = "MyProject lopony.flow@gmail.com" }
$sub = Invoke-RestMethod -Uri "https://data.sec.gov/submissions/CIK$cik.json" -Headers $h
$idx = ($sub.filings.recent.form | Select-String "^10-K$" -List).LineNumber - 1
$acc = $sub.filings.recent.accessionNumber[$idx] -replace "-", ""
$date = $sub.filings.recent.filingDate[$idx]
Write-Output "Accession: $acc | Date: $date"
```

**3. ดึง filing index เพื่อหาไฟล์ HTML หลัก:**
```powershell
$h = @{ "User-Agent" = "MyProject lopony.flow@gmail.com" }
$cikShort = $cik.TrimStart('0')
$indexUrl = "https://www.sec.gov/Archives/edgar/data/$cikShort/$acc/$($acc -replace '(\d{10})(\d{18})', '$1-$2-index.htm')"
# หรือใช้ JSON index:
$jsonIndex = Invoke-RestMethod -Uri "https://data.sec.gov/submissions/CIK$cik.json" -Headers $h
```

ถ้า index URL ไม่แน่ใจ ให้ใช้ format นี้แทน:
```powershell
$h = @{ "User-Agent" = "MyProject lopony.flow@gmail.com" }
$cikShort = [int64]$cik
$accFmt = $acc -replace '(\d{10})(\d{18})', '$1-$2-'  # format: XXXXXXXXXX-YY-ZZZZZZ
$indexUrl = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=$cikShort&type=10-K&dateb=&owner=include&count=5"
$page = Invoke-WebRequest -Uri $indexUrl -Headers $h
Write-Output $page.Links | Where-Object { $_.href -match "Archives" } | Select-Object -First 5
```

**4. หาไฟล์ HTM หลักใน filing index แล้ว fetch:**
```powershell
$h = @{ "User-Agent" = "MyProject lopony.flow@gmail.com" }
$cikShort = $cik.TrimStart('0')
$accDash = "$($acc.Substring(0,10))-$($acc.Substring(10,2))-$($acc.Substring(12))"
$indexUrl = "https://www.sec.gov/Archives/edgar/data/$cikShort/$acc/${accDash}-index.htm"
$indexPage = Invoke-WebRequest -Uri $indexUrl -Headers $h
# ดู links ที่ชี้ไปไฟล์ .htm ขนาดใหญ่
$indexPage.Links | Where-Object { $_.href -match "\.htm$" } | Select-Object href, innerText
```

**5. Fetch ไฟล์ 10-K HTML หลัก (อ่านทีละ section):**

ใช้ WebFetch บน URL ของไฟล์ HTM ที่ได้จากข้อ 4 โดยแยก prompt ตาม section:
- Prompt 1: "Extract Item 1 Business section — company description, products, segments, distribution, competition, supply chain, seasonality, employees, IP"
- Prompt 2: "Extract Item 1A Risk Factors — macro, regulatory, legal, and business risks"
- Prompt 3: "Extract Item 7 MD&A — revenue by segment and product with YoY%, gross margin, operating expenses, tax rate, liquidity, capital return"
- Prompt 4: "Extract Financial Statements — Income Statement, Balance Sheet, Cash Flow Statement with 3 years of data"

---

### B: หุ้นอื่น → PDF ใน folder

1. ตรวจสอบไฟล์ใน `sources/<TICKER>/`
2. ถ้ามี PDF: อ่านด้วย Read tool ทีละ 20 หน้า เริ่มจากหน้าแรก
3. ถ้าไม่มี: แจ้ง user ให้วาง PDF ที่ `sources/<TICKER>/` แล้วรันใหม่

---

### C: user paste เนื้อหามาในช่อง chat → ใช้เลย

---

## ขั้นตอนที่ 2 — สร้างไฟล์

1. สร้าง `sources/<TICKER>/` ถ้ายังไม่มี
2. อ่าน format จาก `.claude/templates/10k-format.md`
3. สร้าง `sources/<TICKER>/10-k-fy2025.md` ตาม format นั้น

## กฎ

- ห้ามแต่งตัวเลข — ถ้าไม่มีข้อมูลใส่ `N/A — ไม่พบใน source`
- ทุก section ที่มีตัวเลขต้องมี **หมายเหตุ**
- fiscal year ใช้ตามจริงจากเอกสาร
- ตอนท้ายแจ้ง: path ที่สร้าง, source ที่ใช้, section ที่ขาด
