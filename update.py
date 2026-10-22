import json
from bs4 import BeautifulSoup
import requests


def update_market_rates():
  url = 'https://www.eanlibya.com/exchangerate/'
  headers = {
      'User-Agent': (
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
          ' like Gecko) Chrome/122.0.0.0 Safari/537.36'
      )
  }

  try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')

    rates = []

    # 1. البحث في الجداول إن وجدت
    tables = soup.find_all('table')
    for table in tables:
      for row in table.find_all('tr'):
        cols = [ele.text.strip() for ele in row.find_all(['th', 'td'])]
        if len(cols) >= 2:
          name, price = cols[0], cols[1]
          if (
              name
              and price
              and 'العملة' not in name
              and 'السوق' not in name
              and len(name) < 40
          ):
            rates.append({'currency': name, 'price': price})

    # 2. إذا لم تجد الجداول، البحث في الصناديق أو العناصر النصية داخل الصفحة
    if not rates:
      # البحث عن العناصر التي قد تحتوي على أسعار العملات
      for el in soup.find_all(['div', 'li', 'p', 'span', 'strong']):
        text = el.text.strip()
        # التحقق من وجود كلمات مفتاحية وأرقام تدل على السعر
        if (
            any(
                c in text
                for c in [
                    'دولار',
                    'يورو',
                    'إسترليني',
                    'دينار',
                    'ليرة',
                    'مصري',
                    'السعودي',
                ]
            )
            and any(char.isdigit() for char in text)
            and len(text) < 60
        ):
          rates.append({'currency': text, 'price': ''})

    # إزالة العناصر المكررة
    unique_rates = []
    seen = set()
    for r in rates:
      identifier = (r['currency'], r['price'])
      if identifier not in seen:
        seen.add(identifier)
        unique_rates.append(r)

    # حفظ البيانات في ملف JSON
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(unique_rates, f, ensure_ascii=False, indent=4)

    print(f'تم تحديث الملف بنجاح، عدد العناصر: {len(unique_rates)}')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
