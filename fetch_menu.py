import requests
from bs4 import BeautifulSoup
import json

def get_menu():
    # Použijeme tvou lepší adresu pro iframe
    url = "https://www.menicka.cz/api/iframe/?id=6956"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = []
        
        menu_list = soup.find('ul')
        if menu_list:
            for li in menu_list.find_all('li'):
                text = li.get_text(strip=True)
                if text:
                    items.append(text)
        
        if not items:
            return {"restaurant": "Masný růžek", "items": ["Dnes menu nebylo zadáno nebo je vyprodáno."]}
            
        return {"restaurant": "Masný růžek", "items": items}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    menu_data = get_menu()
    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(menu_data, f, ensure_ascii=False, indent=4)
