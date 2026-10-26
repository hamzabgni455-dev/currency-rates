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
    raw_rates = []

    # استخراج الصفوف من الجداول بدقة
    for row in soup.find_all('tr'):
      cols = [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
      if len(cols) >= 2:
        # البحث عن خلية تحتوي على اسم العملة وخلية تحتوي على السعر
        name = ''
        price = ''
        for col in cols:
          if any(
              k in col
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
              ]
          ):
            name = col
          elif re.match(r'^\d+([,.]\d+)?$', col):
            price = col

        if name and price:
          # تنظيف الاسم من أي رموز زائدة
          name = re.sub(r'[-:\|\(\)\/]+', ' ', name).strip()
          raw_rates.append({'currency': name, 'price': price})

    # تصفية وإزالة العناصر المكررة والاحتفاظ بأحدث سعر فريد
    unique_rates = []
    seen_currencies = set()
    for r in raw_rates:
      curr_name = r['currency']
      # توحيد التسمية المختصرة
      if 'دولار' in curr_name:
        clean_name = 'الدولار (موازي)'
      elif 'يورو' in curr_name:
        clean_name = 'اليورو'
      elif 'ليرة' in curr_name:
        clean_name = 'الليرة التركية'
      elif 'تونسي' in curr_name:
        clean_name = 'الدينار التونسي'
      elif 'مصري' in curr_name:
        clean_name = 'الجنيه المصري'
      else:
        clean_name = curr_name

      if clean_name not in seen_currencies:
        seen_currencies.add(clean_name)
        unique_rates.append({'currency': clean_name, 'price': r['price']})

    # إذا استخرجنا نتائج صالحة، نحفظها
    if unique_rates:
      with open('rates.json', 'w', encoding='utf-8') as f:
        json.dump(unique_rates, f, ensure_ascii=False, indent=4)
      print(f'تم تحديث الأسعار الحية بنجاح! عدد العناصر: {len(unique_rates)}')
    else:
      print('لم يتم العثور على مطابقات كافية.')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
