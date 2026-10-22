import json
import re
from bs4 import BeautifulSoup
import cloudscraper


def update_market_rates():
  url = 'https://www.eanlibya.com/exchangerate/'
  scraper = cloudscraper.create_scraper()

  try:
    response = scraper.get(url, timeout=20)
    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # الكلمات المفتاحية للعملات والصكوك المصرفية
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
        'التجارة والتنمية',
        'الوحدة',
        'الجمهورية',
        'التجاري الوطني',
        'شمال إفريقيا',
    ]

    for element in soup.find_all(
        ['tr', 'div', 'p', 'li', 'span', 'strong', 'b']
    ):
      text = element.get_text(separator=' ', strip=True)
      if any(k in text for k in keywords) and any(
          char.isdigit() for char in text
      ):
        clean_text = ' '.join(text.split())
        if 5 < len(clean_text) < 90:
          match_price = re.search(r'\d+([,.]\d+)?', clean_text)
          if match_price:
            price_val = match_price.group(0)
            currency_val = clean_text.replace(price_val, '').strip()
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

    if not unique_rates:
      unique_rates = [{'currency': 'جاري التحديث', 'price': ''}]

    # حفظ النتائج في ملف rates.json
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(unique_rates, f, ensure_ascii=False, indent=4)

    print(f'تم تحديث الملف بنجاح، عدد العناصر: {len(unique_rates)}')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
