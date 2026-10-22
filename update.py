import json
import cloudscraper
from bs4 import BeautifulSoup


def update_market_rates():
  url = 'https://www.eanlibya.com/exchangerate/'

  # استخدام cloudscraper لتجاوز حماية الموقع (مثل Cloudflare)
  scraper = cloudscraper.create_scraper()

  try:
    response = scraper.get(url, timeout=20)
    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # 1. البحث في جداول الموقع
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

    # 2. البحث البديل في عناصر الصفحة إذا لم تكن في جدول تقليدي
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
          if len(text) < 50:
            rates.append({'currency': text, 'price': ''})

    # إزالة العناصر المكررة
    unique_rates = []
    seen = set()
    for r in rates:
      identifier = (r['currency'], r['price'])
      if identifier not in seen:
        seen.add(identifier)
        unique_rates.append(r)

    # إذا لم يتم العثور على بيانات نهائياً
    if not unique_rates:
      unique_rates = [{
          'currency': 'تعذر الجلب',
          'price': 'يرجى التحقق من الهيكل',
      }]

    # حفظ النتائج في ملف rates.json
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(unique_rates, f, ensure_ascii=False, indent=4)

    print(f'تم تحديث الملف بنجاح، عدد العناصر: {len(unique_rates)}')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
