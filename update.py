import json
import re
from bs4 import BeautifulSoup
import requests


def update_market_rates():
  url = 'https://www.eanlibya.com/exchangerate/'
  headers = {
      'User-Agent': (
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
          ' (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
      )
  }

  try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # 1. البحث في صفوف الجداول التقليدية
    for tr in soup.find_all('tr'):
      cols = [td.text.strip() for td in tr.find_all(['th', 'td'])]
      if len(cols) >= 2:
        name, price = cols[0], cols[1]
        if (
            any(
                c in name
                for c in [
                    'دولار',
                    'يورو',
                    'إسترليني',
                    'دينار',
                    'ليرة',
                    'مصري',
                    'السعودي',
                    'درهم',
                ]
            )
            and any(char.isdigit() for char in price)
        ):
          rates.append({'currency': name, 'price': price})

    # 2. البحث الشامل في عناصر الصفحة إذا لم تكن في جدول
    if not rates:
      for el in soup.find_all(['div', 'li', 'p', 'span', 'strong', 'td', 'b']):
        text = el.text.strip()
        if any(
            c in text
            for c in [
                'دولار',
                'يورو',
                'إسترليني',
                'ليرة',
                'مصري',
                'السعودي',
                'دينار',
            ]
        ) and any(char.isdigit() for char in text):
          parts = re.split(r'[\s\:\-\|]+', text)
          if len(parts) >= 2:
            price_candidate = next(
                (p for p in parts if any(d.isdigit() for d in p)), ''
            )
            name_candidate = ' '.join(
                [p for p in parts if p != price_candidate]
            )
            if price_candidate and len(name_candidate) < 30:
              rates.append({
                  'currency': name_candidate.strip(),
                  'price': price_candidate.strip(),
              })

    # إزالة العناصر المكررة
    unique_rates = []
    seen = set()
    for r in rates:
      identifier = (r['currency'], r['price'])
      if identifier not in seen and 'جاري' not in r['price']:
        seen.add(identifier)
        unique_rates.append(r)

    # إذا لم يتم العثور على أي بيانات، ضع رسالة توضيحية
    if not unique_rates:
      unique_rates = [{
          'currency': 'تحديث قادم',
          'price': 'يرجى التحقق لاحقاً',
      }]

    # حفظ النتائج في ملف rates.json
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(unique_rates, f, ensure_ascii=False, indent=4)

    print(f'تم تحديث الملف بنجاح، عدد العناصر: {len(unique_rates)}')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
