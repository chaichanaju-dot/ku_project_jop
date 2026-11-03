# thai-docx: ทำเอกสารคำสอนภาษาไทยเป็น Word

สกิลสำหรับ Claude Code ที่แปลงไฟล์ Markdown ภาษาไทยเป็นไฟล์ .docx ที่จัดหน้าพร้อมใช้
- จัดชิดขอบแบบกระจายไทย (thaiDistribute) โดยตัดคำด้วย pythainlp
- ฟอนต์ TH Sarabun New, หัวข้อ 24/18/16/14 pt
- คำบรรยายรูป "รูปที่ N.M" เลขรันอัตโนมัติ
- ปิดเส้นใต้สีแดงที่ Word ขีดใต้ภาษาไทย

## สิ่งที่ต้องติดตั้งก่อน

1. Python 3.10 ขึ้นไป แล้วติดตั้งไลบรารี: `pip install pythainlp pillow`
2. pandoc (https://pandoc.org/installing.html)
3. Git Bash (บน Windows) เพื่อรันไฟล์ .sh
4. ฟอนต์ TH Sarabun New ในเครื่อง

## วิธีติดตั้งในโปรเจกต์

คัดลอกทั้งสองโฟลเดอร์ไปไว้ที่โฟลเดอร์โปรเจกต์ของตัวเอง

```
<โปรเจกต์>/.claude/skills/thai-docx/SKILL.md
<โปรเจกต์>/tools/teaching/*
```

เปิด Claude Code ในโฟลเดอร์โปรเจกต์ แล้วพิมพ์ `/thai-docx` หรือบอกว่า "ทำเอกสารคำสอนเป็น Word"

## ใช้เองโดยไม่ผ่าน Claude

```bash
bash tools/teaching/render_chapter_docx.sh  บทที่1.md  บทที่1.docx
bash tools/teaching/apply_house_style.sh    บทที่1.docx
```

เปิดไฟล์ใน Word แล้วกด Ctrl+A ตามด้วย F9 ให้เลขรูปอัปเดต

## หมายเหตุ

- `reference_template.docx` เป็นไฟล์ต้นแบบสไตล์ (ฟอนต์ ขนาด ระยะขอบ) ไม่มีเนื้อหา แก้สไตล์ใน Word แล้วบันทึกทับได้
- รายละเอียดทุกขั้นตอนอยู่ใน `.claude/skills/thai-docx/SKILL.md`
