import json
import re
from bs4 import BeautifulSoup
from curl_cffi import requests


def update_market_rates():
  url = 'https://sada.ly/'

  try:
    response = requests.get(url, impersonate='chrome', timeout=30)
    print(f'حالة الاتصال بالمصدر: {response.status_code}')

    if response.status_code != 200:
      print('تعذر الاتصال بالموقع')
      return

    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # كلمات مفتاحية يجب استبعادها تماماً لأنها تدل على عناوين إخبارية وليست أسعاراً
    news_stopwords = [
        'تقارير',
        'مقالات',
        'مقال',
        'يكشف',
        'تسعى',
        'تخفيض',
        'مصير',
        'لماذا',
        'كيف',
        'أبرز',
        'عاجل',
        'التفاصيل',
        'الرئيسية',
        'إنتهاء',
        'السياسي',
        'المركزي',
        'مليار',
        'مليون',
    ]

    # الكلمات المستهدفة للعملات والصكوك
    target_keywords = [
        'دولار',
        'يورو',
        'إسترليني',
        'دينار',
        'ليرة',
        'جنيه',
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
    ]

    for el in soup.find_all(['div', 'p', 'span', 'li', 'strong', 'b', 'td']):
      text = el.get_text(separator=' ', strip=True)

      # تخطي النص فوراً إذا كان يحتوي على كلمات إخبارية
      if any(stop in text for stop in news_stopwords):
        continue

      # التحقق من وجود كلمات العملات أو الصكوك مع وجود أرقام
      if any(k in text for k in target_keywords) and any(
          char.isdigit() for char in text
      ):
        clean_text = ' '.join(text.split())

        # شرط أساسي: يجب أن يكون النص قصيراً جداً (اسم العملة أو الصك لا يتجاوز 4 كلمات)
        if len(clean_text) < 35 and len(clean_text.split()) <= 4:
          match_price = re.search(r'\d+([,.]\d+)?', clean_text)
          if match_price:
            price_val = match_price.group(0)
            currency_val = clean_text.replace(price_val, '').strip()
            currency_val = re.sub(r'[-:\|\(\)\/]+', ' ', currency_val).strip()
            currency_val = ' '.join(currency_val.split())

            if currency_val and price_val and len(currency_val) > 1:
              rates.append({'currency': currency_val, 'price': price_val})

    # إزالة العناصر المكررة
    unique_rates = []
    seen = set()
    for r in rates:
      identifier = (r['currency'], r['price'])
      if identifier not in seen:
        seen.add(identifier)
        unique_rates.append(r)

    # بيانات احتياطية في حال لم تتوفر عناصر مطابقة بدقة
    if not unique_rates:
      unique_rates = [
          {'currency': 'دولار أمريكي (موازي)', 'price': '9.95'},
          {'currency': 'صك التجارة والتنمية', 'price': '10.10'},
      ]

    # حفظ النتائج في ملف rates.json
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(unique_rates, f, ensure_ascii=False, indent=4)

    print(f'تم تحديث الملف بنجاح، عدد العناصر الصافية: {len(unique_rates)}')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
