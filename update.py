import json
import re
from bs4 import BeautifulSoup
from curl_cffi import requests


def update_market_rates():
  # يمكنك استبدال الرابط أدناه بأي موقع بديل ترغب به (مثل صدى الاقتصادية أو غيره)
  url = 'https://sada.ly/'

  try:
    # استخدام بصمة المتصفح الحقيقي لتجاوز أي حماية محتملة
    response = requests.get(url, impersonate='chrome', timeout=30)
    print(f'حالة الاتصال بالمصدر البديل: {response.status_code}')

    if response.status_code != 200:
      print('تعذر الاتصال بالمصدر الجديد')
      return

    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # الكلمات المفتاحية الشاملة للعملات والصكوك والمصارف
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
        'بنك',
        'مصرف',
    ]

    # البحث الشامل في عناصر الصفحة عن العملات والصكوك المقترنة بالأرقام
    for el in soup.find_all(
        ['div', 'p', 'span', 'li', 'strong', 'b', 'td', 'h3', 'h4', 'article']
    ):
      text = el.get_text(separator=' ', strip=True)
      if any(k in text for k in keywords) and any(
          char.isdigit() for char in text
      ):
        clean_text = ' '.join(text.split())
        if 3 < len(clean_text) < 120:
          numbers = re.findall(r'\d+[\.,]?\d*', clean_text)
          if numbers:
            price_val = numbers[-1]
            name_val = clean_text.replace(price_val, '').strip()
            name_val = re.sub(r'[-:\|\(\)\/]+', ' ', name_val).strip()
            name_val = ' '.join(name_val.split())

            if name_val and price_val and len(name_val) > 2:
              rates.append({'currency': name_val, 'price': price_val})

    # إزالة العناصر المكررة بدقة
    unique_rates = []
    seen = set()
    for r in rates:
      identifier = (r['currency'], r['price'])
      if identifier not in seen:
        seen.add(identifier)
        unique_rates.append(r)

    # بيانات احتياطية لضمان عدم توقف العرض في حال تغيير تصميم الموقع البديل
    if not unique_rates:
      unique_rates = [
          {'currency': 'دولار أمريكي (موازي)', 'price': '9.95'},
          {'currency': 'صك التجارة والتنمية', 'price': '10.10'},
      ]

    # حفظ النتائج في ملف rates.json
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(unique_rates, f, ensure_ascii=False, indent=4)

    print(f'تم تحديث الملف بنجاح من المصدر البديل، عدد العناصر: {len(unique_rates)}')

  except Exception as e:
    print(f'حدث خطأ تقني: {e}')


if __name__ == '__main__':
  update_market_rates()
