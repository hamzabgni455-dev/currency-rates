import json
import re
from bs4 import BeautifulSoup
import cloudscraper


def update_market_rates():
  url = 'https://www.eanlibya.com/exchangerate/'
  scraper = cloudscraper.create_scraper()

  try:
    response = scraper.get(url, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # 1. البحث الأساسي في جداول الموقع (حيث تتوفر العملات والصكوك)
    for table in soup.find_all('table'):
      for row in table.find_all('tr'):
        cols = [ele.get_text(strip=True) for ele in row.find_all(['th', 'td'])]
        if len(cols) >= 2:
          name = cols[0]
          price = cols[1]
          if name and price and any(char.isdigit() for char in price):
            if not any(
                w in name for w in ['العملة', 'السعر', 'الجهة', 'البنك']
            ):
              rates.append({'currency': name, 'price': price})

    # 2. البحث البديل في العناصر الصغيرة (إذا لم تكن في جدول تقليدي)
    if not rates:
      for el in soup.find_all(['td', 'li', 'span', 'p', 'strong', 'b']):
        text = el.get_text(strip=True)
        if any(
            k in text
            for k in [
                'دولار',
                'يورو',
                'دينار',
                'إسترليني',
                'ليرة',
                'جنيه',
                'صك',
                'صكوك',
                'التجارة',
                'الوحدة',
                'الجمهورية',
                'التجاري',
                'المصرف',
            ]
        ) and any(char.isdigit() for char in text):
          if len(text) < 80:
            match_price = re.search(r'\d+([,.]\d+)?', text)
            if match_price:
              price_val = match_price.group(0)
              currency_val = text.replace(price_val, '').strip()
              currency_val = re.sub(r'[-:\|\(\)]+', ' ', currency_val).strip()
              if currency_val and price_val:
                rates.append({'currency': currency_val, 'price': price_val})

    # إزالة العناصر المكررة
    unique_rates = []
    seen = set()
    for r in rates:
      identifier = (r['currency'], r['price'])
      if identifier not in seen:
        seen.add(identifier)
        unique_rates.append(r)

    # حفظ النتائج الحقيقية إذا وجدناها، وإلا نبقي تنبيه واضح
    if not unique_rates:
      unique_rates = [{
          'currency': 'جاري جلب الأسعار الحية',
          'price': 'انتظر قليلاً',
      }]

    # حفظ النتائج في ملف rates.json
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(unique_rates, f, ensure_ascii=False, indent=4)

    print(f'تم تحديث الملف بنجاح، عدد العناصر: {len(unique_rates)}')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
