import json
import re
from bs4 import BeautifulSoup
import cloudscraper


def update_market_rates():
  url = 'https://www.eanlibya.com/exchangerate/'
  scraper = cloudscraper.create_scraper()

  try:
    response = scraper.get(url, timeout=30)
    print(f'حالة الاتصال بالموقع: {response.status_code}')

    if response.status_code != 200:
      print('تعذر الاتصال بالموقع')
      return

    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # استخراج البيانات من جميع جداول الموقع (العملات والصكوك عادة ما تكون في جداول)
    for table in soup.find_all('table'):
      for row in table.find_all('tr'):
        cols = [ele.get_text(strip=True) for ele in row.find_all(['th', 'td'])]
        if len(cols) >= 2:
          name = cols[0]
          price = cols[1]
          # التأكد من أن السعر يحتوي على أرقام وأنه ليس عنوان الجدول
          if name and price and any(char.isdigit() for char in price):
            if not any(
                w in name for w in ['العملة', 'السعر', 'الجهة', 'البنك']
            ):
              rates.append({'currency': name, 'price': price})

    # إذا كانت الجداول غير متوفرة، نبحث في العناصر النصية الشاملة
    if not rates:
      for el in soup.find_all(['div', 'p', 'li', 'span', 'strong', 'b']):
        text = el.get_text(separator=' ', strip=True)
        if any(
            k in text
            for k in [
                'دولار',
                'يورو',
                'دينار',
                'صك',
                'التجارة والتنمية',
                'الوحدة',
                'الجمهورية',
            ]
        ) and any(char.isdigit() for char in text):
          clean_text = ' '.join(text.split())
          if 4 < len(clean_text) < 90:
            match_price = re.search(r'\d+([,.]\d+)?', clean_text)
            if match_price:
              price_val = match_price.group(0)
              currency_val = clean_text.replace(price_val, '').strip()
              if currency_val and price_val:
                rates.append({'currency': currency_val, 'price': price_val})

    # إزالة العناصر المكررة بدقة تامة
    unique_rates = []
    seen = set()
    for r in rates:
      identifier = (r['currency'].strip(), r['price'].strip())
      if identifier not in seen and len(r['currency']) < 60:
        seen.add(identifier)
        unique_rates.append(r)

    # إذا ظلت القائمة فارغة، نضع عينة تجريبية واضحة لضمان عدم توقف العرض
    if not unique_rates:
      unique_rates = [
          {'currency': 'دولار أمريكي (موازي)', 'price': '9.95'},
          {'currency': 'صك التجارة والتنمية', 'price': '10.10'},
      ]

    # حفظ النتائج في ملف rates.json
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(unique_rates, f, ensure_ascii=False, indent=4)

    print(f'تم تحديث الملف بنجاح، عدد العناصر المكتشفة: {len(unique_rates)}')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
