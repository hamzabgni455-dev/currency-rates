import json
import re
from bs4 import BeautifulSoup
from curl_cffi import requests


def update_market_rates():
  url = 'https://www.eanlibya.com/exchangerate/'

  try:
    response = requests.get(url, impersonate='chrome110', timeout=30)
    if response.status_code != 200:
      print('فشل الاتصال بالمصدر')
      return

    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # فحص صفوف الجدول بدقة منعاً لتداخل الأعمدة
    for row in soup.find_all('tr'):
      cols = [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
      if len(cols) >= 2:
        row_text = ' '.join(cols)

        # تحديد اسم العملة الصحيح بناءً على محتوى الصف
        curr_name = ''
        if 'دولار' in row_text:
          curr_name = 'الدولار (موازي)'
        elif 'يورو' in row_text:
          curr_name = 'اليورو'
        elif 'ليرة' in row_text:
          curr_name = 'الليرة التركية'
        elif 'تونسي' in row_text:
          curr_name = 'الدينار التونسي'
        elif 'مصري' in row_text:
          curr_name = 'الجنيه المصري'

        if curr_name:
          # استخراج الأرقام العشرية من الصف وتجنب التداخل
          prices = []
          for col in cols:
            match = re.findall(r'\b\d+[\.,]\d+\b', col)
            if match:
              prices.extend(match)

          if prices:
            # نأخذ أول رقم عشري دقيق يمثل سعر العملة في الجدول
            price_val = prices[0]
            rates.append({'currency': curr_name, 'price': price_val})

    # تصفية النتائج والاحتفاظ بنسخة فريدة وصحيحة لكل عملة
    unique_rates = []
    seen = set()
    for r in rates:
      if r['currency'] not in seen:
        seen.add(r['currency'])
        unique_rates.append(r)

    # حفظ النتائج المنظمة في ملف rates.json
    if unique_rates:
      with open('rates.json', 'w', encoding='utf-8') as f:
        json.dump(unique_rates, f, ensure_ascii=False, indent=4)
      print(
          'تم تحديث الأسعار الحية بدقة تامة وبدون تداخل! عدد العناصر:'
          f' {len(unique_rates)}'
      )
    else:
      print('لم يتم العثور على مطابقات كافية.')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
