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

    # 1. الاستخراج الذكي من جداول الموقع (حيث ينفصل اسم العملة عن السعر في أعمدة الجدول)
    for row in soup.find_all('tr'):
      cols = [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
      if len(cols) >= 2:
        name = cols[0]
        price = cols[-1]  # السعر غالباً يكون في العمود الأخير
        if name and price and any(char.isdigit() for char in price):
          # استبعاد رؤوس الجدول العرضية
          if not any(
              w in name for w in ['العملة', 'السعر', 'الجهة', 'البنك', 'التفاصيل']
          ):
            rates.append({'currency': name, 'price': price})

    # 2. البحث الاحتياطي في القوائم أو العناصر الأخرى إذا لم تكتمل الجداول
    if len(rates) < 2:
      for item in soup.find_all(['li', 'div', 'p', 'span']):
        text = item.get_text(separator=' ', strip=True)
        if any(
            k in text
            for k in [
                'دولار',
                'يورو',
                'دينار',
                'صك',
                'التجارة',
                'الوحدة',
                'الجمهورية',
                'التجاري',
            ]
        ) and any(char.isdigit() for char in text):
          if len(text) < 80:
            match = re.search(r'(\d+([,.]\d+)?)', text)
            if match:
              price_val = match.group(0)
              name_val = text.replace(price_val, '').strip()
              name_val = re.sub(r'[-:\|\(\)\/]+', ' ', name_val).strip()
              name_val = ' '.join(name_val.split())
              if name_val and price_val:
                rates.append({'currency': name_val, 'price': price_val})

    # إزالة العناصر المكررة بدقة
    unique_rates = []
    seen = set()
    for r in rates:
      identifier = (r['currency'], r['price'])
      if identifier not in seen:
        seen.add(identifier)
        unique_rates.append(r)

    # إذا وجدنا بيانات حية نعتمدها، وإلا نترك تنبيه واضح
    if not unique_rates:
      unique_rates = [{
          'currency': 'جاري جلب الأسعار الحية',
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
