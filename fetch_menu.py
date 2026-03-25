import requests
from bs4 import BeautifulSoup
import json

def get_menu():
    url = "https://www.menicka.cz/api/iframe/?id=6956"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding 
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        
        items = []
        headers_h2 = soup.find_all('h2')
        
        target_table = None
        for h2 in headers_h2:
            if "dnes" in h2.get_text().lower():
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

        return {"restaurant": "Masný růžek", "items": items}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    menu_data = get_menu()
    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(menu_data, f, ensure_ascii=False, indent=4)
