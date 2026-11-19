import json

with open('data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# Pricing updates mapping
price_updates = {
    'p-powergreen': '690 บาท / กระสอบ 50 กก. (13,800 บาท/ตัน) · ส่งฟรีทั่วประเทศ',
    'p-smartn': '1,090 บาท / กระสอบ 50 กก. (21,800 บาท/ตัน) · ส่งฟรีทั่วประเทศ',
    'p-smartyield': '1,090 บาท / กระสอบ 50 กก. (21,800 บาท/ตัน) · ส่งฟรีทั่วประเทศ',
    'p-smartr': '595 บาท / กระสอบ 25 กก. (11,900 บาท/ตัน) · ส่งฟรีทั่วประเทศ',
    'p-unicorn': '530 บาท / กระสอบ 25 กก. (10,600 บาท/ตัน) · ส่งฟรีทั่วประเทศ',
    'p-homemg': '350 บาท / กระสอบ 50 กก. (7,000 บาท/ตัน) · ส่งฟรีทั่วประเทศ',
    'p-takecare': '490 บาท / กระสอบ 50 กก. (9,800 บาท/ตัน) · ส่งฟรีทั่วประเทศ',
    'p-5active': '490 บาท / ซอง 500 กรัม · ส่งฟรี (ซอง 150 กรัม ใช้เป็นของแถมโปรโมชัน)',
    'p-boosterup': '199 บาท / ถุง 1 กก. · ส่งฟรี',
    'p-hydroa': '190 บาท / ถุง 1 กก.',
    'p-hydrob': '235 บาท / ถุง 1 กก.',
    'p-ultrastick': '590 บาท / ขวด 1 ลิตร · ส่งฟรี',
    'p-smartnano': '780 บาท (1 แถม 1) / ขวด 1 ลิตร · 3,900 บาท / ถัง 20 ลิตร · ส่งฟรี',
    'p-smartsilver': '480 บาท / ขวด 1 ลิตร · 4,350 บาท / ถัง 20 ลิตร · ส่งฟรี',
    'p-smartred': '480 บาท / ขวด 1 ลิตร · 4,350 บาท / ถัง 20 ลิตร · ส่งฟรี',
    'p-smartorange': '480 บาท / ขวด 1 ลิตร · 4,350 บาท / ถัง 20 ลิตร · ส่งฟรี',
    'p-smartbio': '580 บาท / ขวด 1 ลิตร · 4,900 บาท / ถัง 20 ลิตร · ส่งฟรี',
    'p-smartnplus': '580 บาท / ขวด 1 ลิตร · 4,990 บาท / ถัง 20 ลิตร · ส่งฟรี',
    'p-smartshield': '580 บาท / ขวด 1 ลิตร · 5,550 บาท / ถัง 20 ลิตร · ส่งฟรี'
}

updated_count = 0
for p in d['products']:
    pid = p['id']
    if pid in price_updates:
        old = p.get('price')
        p['price'] = price_updates[pid]
        updated_count += 1
        print(f"Updated {pid} ({p['name']}):\n  Old: {old}\n  New: {p['price']}\n")

# Update QA script
for q in d.get('qa', []):
    if q.get('id') == 'qa-g1' or 'ราคาปุ๋ยเม็ด' in q.get('q', ''):
        q['a'] = """🟢 พาวเวอร์กรีน (สูตรรองพื้น/บำรุงตอ): 690 บาท/กระสอบ (13,800 บาท/ตัน)
🔴 สมาร์ทเอ็น (สูตรเร่งต้น): 1,090 บาท/กระสอบ (21,800 บาท/ตัน)
🌸 สมาร์ทยิลด์ (สูตรเพิ่มน้ำหนัก): 1,090 บาท/กระสอบ (21,800 บาท/ตัน)
⭐ เทคแคร์: 490 บาท/กระสอบ (9,800 บาท/ตัน)
🌾 สมาร์ท อาร์ (สำหรับข้าว): 595 บาท/กระสอบ 25 กก. (11,900 บาท/ตัน)
🌽 ยูนิคอร์น 18-3-3: 530 บาท/กระสอบ 25 กก. (10,600 บาท/ตัน)
🚚 จัดส่งฟรีทั่วประเทศ พร้อมบริการยกลงจากรถ ไม่มีขั้นต่ำ (ทางเราจะตรวจสอบคิวรถให้ค่ะ)"""
        print("Updated qa-g1 script with new prices")

# Update ads kpi text if needed
for a in d.get('ads', []):
    if '690-1,170' in a.get('kpi', ''):
        a['kpi'] = a['kpi'].replace('690-1,170', '690-1,090')
        print("Updated ad kpi price")

# Add feed update
new_update = {
    'date': '2026-11-19',
    'tab': 'products',
    'what': 'อัปเดตราคาขายล่าสุดตามใบราคา: สมาร์ทเอ็น 1,090 · สมาร์ทยิลด์ 1,090 · สมาร์ทอาร์ 595 · ยูนิคอร์น 530 · เทคแคร์ 490 · โฮมแม็ก 350 · 5 ACTIVE 490 · ฮอร์โมนน้ำ 1L และ 20L ทุกตัว'
}
d['updates'] = [new_update] + [u for u in d.get('updates', []) if u.get('what') != new_update['what']]

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

# Also update backup_data.json for consistency
with open('backup_data.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully updated {updated_count} products in data.json and backup_data.json!")
