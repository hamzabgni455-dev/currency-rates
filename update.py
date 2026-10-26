import json
import re
from curl_cffi import requests
from bs4 import BeautifulSoup

def update_market_rates():
    url = 'https://www.eanlibya.com/exchangerate/'
    
    try:
        response = requests.get(url, impersonate='chrome110', timeout=30)
        if response.status_code != 200:
            print("فشل الاتصال بالمصدر")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        rates_dict = {}

        # فحص جميع صفوف الجدول والبحث عن الأرقام وتصفيتها حسب النطاق المنطقي للعملة
        for row in soup.find_all('tr'):
            text = row.get_text(separator=' ', strip=True)
            numbers = re.findall(r'\d+[\.,]\d+', text)
            if not numbers:
                continue
                
            for num_str in numbers:
                try:
                    val = float(num_str.replace(',', '.'))
                except ValueError:
                    continue
                
                # مطابقة العملة مع نطاقها السعري الطبيعي في السوق لضمان عدم التداخل
                if 'دولار' in text and 8.0 <= val <= 12.0:
                    rates_dict['الدولار (موازي)'] = num_str
                elif 'يورو' in text and 9.5 <= val <= 13.0:
                    rates_dict['اليورو'] = num_str
                elif 'ليرة' in text and 0.10 <= val <= 0.50:
                    rates_dict['الليرة التركية'] = num_str
                elif 'تونسي' in text and 2.5 <= val <= 4.0:
                    rates_dict['الدينار التونسي'] = num_str
                elif ('مصري' in text or 'جنيه' in text) and 0.10 <= val <= 0.50:
                    rates_dict['الجنيه المصري'] = num_str
                elif 'التجارة والتنمية' in text and 9.0 <= val <= 12.0:
                    rates_dict['صك التجارة والتنمية'] = num_str
                elif 'الجمهورية' in text and 9.0 <= val <= 12.0:
                    rates_dict['صك الجمهورية'] = num_str
                elif 'الوحدة' in text and 9.0 <= val <= 12.0:
                    rates_dict['صك الوحدة'] = num_str

        # تحويل النتائج إلى القائمة المطلوبة
        unique_rates = [{"currency": k, "price": v} for k, v in rates_dict.items()]

        # حفظ النتائج في ملف rates.json إذا كانت موجودة
        if unique_rates:
            with open('rates.json', 'w', encoding='utf-8') as f:
                json.dump(unique_rates, f, ensure_ascii=False, indent=4)
            print(f"تم تحديث الأسعار الحية بنجاح وبدون أي تداخل! عدد العناصر: {len(unique_rates)}")
        else:
            print("لم يتم العثور على مطابقات ضمن النطاق.")

    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == '__main__':
    update_market_rates()
