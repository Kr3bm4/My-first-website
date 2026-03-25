import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_menu():
    url = "https://www.menicka.cz/api/iframe/?id=6956"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Seznam hledaných výrazů bez diakritiky pro jistotu
    dni_search = ["pond", "ter", "stred", "ctvrt", "patek", "sobot", "nedel"]
    dnesni_index = datetime.now().weekday()
    hledany_den = dni_search[dnesni_index]

    try:
        response = requests.get(url, headers=headers)
        # Vynutíme správné kódování hned na začátku
        response.encoding = 'utf-8' 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = []
        vsechny_h2 = soup.find_all('h2')
        
        target_table = None
        for h2 in vsechny_h2:
            # Hledáme den bez ohledu na diakritiku a velikost písmen
            text_h2 = h2.get_text().lower()
            # Odstraníme z textu neplechu, kterou tam vidíme v debugu
            text_h2 = text_h2.replace('', 'r').replace('', 'u') 
            
            if hledany_den in text_h2 or "dnes" in text_h2:
                target_table = h2.find_next('table', class_='menu')
                break

        if target_table:
            rows = target_table.find_all('tr')
            for row in rows:
                food_td = row.find('td', class_='food')
                prize_td = row.find('td', class_='prize')
                if food_td:
                    food_text = food_td.get_text(" ", strip=True).strip('"„“ ')
                    prize_text = prize_td.get_text(strip=True) if prize_td else ""
                    if food_text:
                        items.append(f"{food_text} — {prize_text}")

        if not items:
            return {"restaurant": "Masný růžek", "items": ["Menu pro dnešek nenalezeno."], "debug": [h.get_text() for h in vsechny_h2]}
            
        return {"restaurant": "Masný růžek", "items": items}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    menu_data = get_menu()
    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(menu_data, f, ensure_ascii=False, indent=4)
