import json
from bs4 import BeautifulSoup
import requests


def update_market_rates():
  url = 'https://www.eanlibya.com/exchangerate/'
  headers = {
      'User-Agent': (
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      )
  }

  try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    rates = []
    tables = soup.find_all('table')

    for table in tables:
      for row in table.find_all('tr'):
        cols = [ele.text.strip() for ele in row.find_all(['th', 'td'])]
        if len(cols) >= 2:
          name, price = cols[0], cols[1]
          if (
              name
              and price
              and 'العملة' not in name
              and 'السوق' not in name
          ):
            rates.append({'currency': name, 'price': price})

    # حفظ البيانات في ملف JSON
    with open('rates.json', 'w', encoding='utf-8') as f:
      json.dump(rates, f, ensure_ascii=False, indent=4)

    print('تم تحديث ملف الأسعار بنجاح!')

  except Exception as e:
    print(f'حدث خطأ: {e}')


if __name__ == '__main__':
  update_market_rates()
  
