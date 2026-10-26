import json
import re
from bs4 import BeautifulSoup
from curl_cffi import requests


def update_market_rates():
  # استخدام رابط صفحة الأسعار المباشر مع محاكاة كاملة لمتصفح حقيقي
  url = 'https://www.eanlibya.com/exchangerate/'

  try:
    # استخدام بصمة متصفح كروم المحدثة لتجاوز الحماية
    response = requests.get(
        url,
        impersonate='chrome110',
        headers={
            'Accept-Language': 'ar-LY,ar;q=0.9,en;q=0.8',
            'Referer': 'https://www.eanlibya.com/',
        },
        timeout=30,
    )

    print(f'حالة الاتصال: {response.status_code}')

    if response.status_code != 200:
      print('فشل الاتصال بالمصدر الحي')
      return

    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # البحث الدقيق داخل الجداول والعناصر التي تحتوي على أسعار العملات والصكوك
    for row in soup.find_all(['tr', 'div', 'li']):
      text = row.get_text(separator=' | ', strip=True)

      # البحث عن الكلمات الدالة للعملات والصكوك
      if any(
          k in text
          for k in [
              'دولار',
              'يورو',
              'ليرة',
              'دينار',
              'جنيه',
              'صك',
              'التجارة',
              'الجمهورية',
              'الوحدة',
              'التجاري',
          ]
      ):
        if any(char.isdigit() for char in text):
          parts = text.split('|')
          for i, part in enumerate(parts):
            if any(
                curr in part
                for curr in [
                    'دولار',
                    'يورو',
                    'ليرة',
                    'دينار',
                    'جنيه',
                    'صك',
                    'التجارة',
                    'الجمهورية',
                    'الوحدة',
                ]
            ):
              # محاولة استخراج السعر المجاور للنص
              for j in range(max(0, i - 1), min(len(parts), i + 3)):
                price_candidate = parts[j].strip()
                # التحقق مما إذا كان النص يمثل رقماً عشرياً سليماً للسعر
                if re.match(r'^\d+([,.]\d+)?$', price_candidate):
                  currency_name = (
                      part.replace(price_candidate, '')
                      .replace(':', '')
                      .strip()
                  )
                  if len(currency_name) > 1 and len(currency_name) < 40:
                    rates.append({
                        'currency': currency_name,
                        'price': price_candidate,
                    })

    # طريقة بديلة في حال اختلاف الهيكل: البحث الشامل المنظم
    if not rates:
      for el in soup.find_all(['p', 'span', 'strong', 'td', 'div']):
        t = el.get_text(strip=True)
        if (
            any(
                c in t
                for c in [
                    'دولار',
                    'يورو',
                    'ليرة',
                    'دينار',
                    'جنيه',
                    'صك',
                    'التجارة',
                    'الجمهورية',
                ]
            )
            and len(t) < 50
        ):
          match = re.search(r'(\d+([,.]\d+)?)', t)
          if match:
            price = match.group(1)
            name = t.replace(price, '').strip()
            name = re.sub(r'[-:\|\(\)\/]+', ' ', name).strip()
            if len(name) > 2:
              rates.append({'currency': name, 'price': price})

    # إزالة العناصر المكررة بدقة تامة
    unique_rates = []
    seen = set()
    for r in rates:
      identifier = (r['currency'], r['price'])
      if identifier not in seen:
        seen.add(identifier)
        unique_rates.append(r)

    # إذا استطاع السكريبت جلب بيانات حية، نعتمدها فوراً، وإلا نبقي النظام نشطاً
    if unique_rates and len(unique_rates) >= 3:
      # حفظ النتائج الحية في ملف rates.json
      with open('rates.json', 'w', encoding='utf-8') as f:
        json.dump(unique_rates, f, ensure_ascii=False, indent=4)
      print(
          f'تم بنجاح جلب وتحديث الأسعار الحية! عدد العناصر: {len(unique_rates)}'
      )
    else:
      print('تم الاحتفاظ بالنسخة المستقرة لضمان استمرار عمل الشريط.')

  except Exception as e:
    print(f'حدث خطأ أثناء جلب السعر الحي: {e}')


if __name__ == '__main__':
  update_market_rates()
