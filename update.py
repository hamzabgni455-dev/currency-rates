import json
from bs4 import BeautifulSoup
import cloudscraper


def update_market_rates():
  url = 'https://www.eanlibya.com/exchangerate/'
  scraper = cloudscraper.create_scraper()

  try:
    response = scraper.get(url, timeout=20)
    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # قائمة الكلمات المفتاحية للعملات المستهدفة
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
    ]

    # البحث في جميع العناصر النصية والجداول داخل الصفحة
    for element in soup.find_all(['tr', 'div', 'p', 'li', 'span', 'strong', 'b']):
      text = element.get_text(separator=' ', strip=True)

      # التأكد من أن النص يحتوي على إحدى العملات وأرقام (الأسعار)
      if any(k in text for k in keywords) and any(
          char.isdigit() for char in text
      ):
        clean_text = ' '.join(text.split())
        # قبول النصوص ذات الطول المعقول لتجنب جلب القوائم الطويلة أو الجوانب
        if 5 < len(clean_text) < 80:
          rates.append({'currency': clean_text, 'price': ''})

    # إزالة العناصر المكررة تماماً
    unique_rates = []
    seen = set()
    for r in rates:
      if r['currency'] not in seen:
        seen.add(r['currency'])
        unique_rates.append(r)

    # إذا لم يتم العثور على أي بيانات، نضع تنبيه واضح
    if not unique_rates:
      unique_rates = [{
          'currency': 'جاري تحديث البيانات من الموقع',
          'price': '',
      }]

    # حفظ النتائج في ملف rates.json
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(unique_rates, f, ensure_ascii=False, indent=4)

    print(f'تم تحديث الملف بنجاح، عدد العناصر: {len(unique_rates)}')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
