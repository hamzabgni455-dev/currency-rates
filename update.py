import json
from bs4 import BeautifulSoup
import requests


def update_market_rates():
  url = 'https://www.eanlibya.com/exchangerate/'
  headers = {
      'User-Agent': (
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
          ' like Gecko) Chrome/122.0.0.0 Safari/537.36'
      )
  }

  try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    rates = []

    # البحث عن الجداول داخل الصفحة
    tables = soup.find_all('table')
    for table in tables:
      rows = table.find_all('tr')
      for row in rows:
        cols = [ele.text.strip() for ele in row.find_all(['th', 'td'])]
        if len(cols) >= 2:
          name = cols[0]
          price = cols[1]
          if (
              name
              and price
              and 'العملة' not in name
              and 'السوق' not in name
          ):
            rates.append({'currency': name, 'price': price})

    # إذا لم يتم العثور على جداول، وضع بيانات تجريبية مؤقتة لضمان عمل الملف
    if not rates:
      rates = [
          {'currency': 'دولار أمريكي (موازي)', 'price': 'جاري التحديث...'},
          {'currency': 'يورو (موازي)', 'price': 'جاري التحديث...'},
      ]

    # حفظ البيانات في ملف rates.json
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(rates, f, ensure_ascii=False, indent=4)
    print(f'تم تحديث الملف بنجاح، عدد العناصر: {len(rates)}')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
