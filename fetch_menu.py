import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_menu():
    url = "https://www.menicka.cz/api/iframe/?id=6956"
    headers = {'User-Agent': 'Mozilla/5.0'}
    dni = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
    dnesni_den = dni[datetime.now().weekday()]

    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = []
        den_blocks = soup.find_all('div', class_='menicka')
        
        for block in den_blocks:
            datum_div = block.find('div', class_='datum')
            if datum_div and dnesni_den in datum_div.get_text():
                li_items = block.find_all('li')
                for li in li_items:
                    text = li.get_text(strip=True)
                    if text:
                        items.append(text)
                break 

        if not items:
            return {"restaurant": "Masný růžek", "items": [f"Pro den {dnesni_den} nebylo menu nalezeno."]}
            
        return {"restaurant": "Masný růžek", "items": items}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    menu_data = get_menu()
    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(menu_data, f, ensure_ascii=False, indent=4)
