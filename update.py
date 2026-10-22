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

    # الكلمات المفتاحية الشاملة للعملات والصكوك والمصارف الليبية
    keywords = [
        'دولار',
        'يورو',
        'إسترليني',
        'دينار',
        'ليرة',
        'جنيه',
        'مصري',
        'سعودي',
        'درهم',
        'صك',
        'صكوك',
        'التجارة',
        'التنمية',
        'الوحدة',
        'الجمهورية',
        'التجاري',
        'أمان',
        'صحارى',
        'السرايا',
        'الوفاء',
        'المتوسط',
        'البنك',
        'مصرف',
    ]

    # مسح شامل لجميع العناصر النصية والجداول في الصفحة
    for el in soup.find_all(
        ['tr', 'div', 'p', 'li', 'span', 'strong', 'b', 'td', 'th']
    ):
      text = el.get_text(separator=' ', strip=True)
      if any(k in text for k in keywords) and any(
          char.isdigit() for char in text
      ):
        clean_text = ' '.join(text.split())
        if 3 < len(clean_text) < 100:
          match_price = re.search(r'\d+([,.]\d+)?', clean_text)
          if match_price:
            price_val = match_price.group(0)
            currency_val = clean_text.replace(price_val, '').strip()
            currency_val = re.sub(r'[-:\|\(\)\/]+', ' ', currency_val).strip()
            currency_val = ' '.join(currency_val.split())

            if currency_val and price_val and len(currency_val) > 1:
              rates.append({'currency': currency_val, 'price': price_val})

    # إزالة العناصر المكررة بدقة
    unique_rates = []
    seen = set()
    for r in rates:
      identifier = (r['currency'], r['price'])
      if identifier not in seen:
        seen.add(identifier)
        unique_rates.append(r)

    # إذا لم يتم العثور على بيانات حية، نضع تنبيه واضح
    if not unique_rates:
      unique_rates = [{
          'currency': 'جاري تحديث الأسعار الحية',
          'price': 'يرجى الانتظار',
      }]

    # حفظ النتائج في ملف rates.json
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(unique_rates, f, ensure_ascii=False, indent=4)

    print(f'تم تحديث الملف بنجاح، عدد العناصر: {len(unique_rates)}')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
