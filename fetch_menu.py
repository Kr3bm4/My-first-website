import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_menicka_data(res_id, res_name, manual_prices=None):
    url = f"https://www.menicka.cz/api/iframe/?id={res_id}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding 
        soup = BeautifulSoup(response.content, 'html.parser')
        
        items = []
        headers_h2 = soup.find_all('h2')
        target_table = None
        
        for h2 in headers_h2:
            if "dnes" in h2.get_text().lower():
                target_table = h2.find_next('table', class_='menu')
                break

        if target_table:
            rows = target_table.find_all('tr')
            for idx, row in enumerate(rows):
                food_td = row.find('td', class_='food')
                prize_td = row.find('td', class_='prize')
                
                if food_td:
                    food_text = food_td.get_text(" ", strip=True).strip('"„“ ')
                    if manual_prices and idx < len(manual_prices):
                        prize_text = manual_prices[idx]
                    else:
                        prize_text = prize_td.get_text(strip=True) if prize_td else ""
                    
                    if food_text:
                        items.append(f"{food_text} — {prize_text}")

        return {"name": res_name, "items": items}
    except Exception as e:
        return {"name": res_name, "error": str(e), "items": []}

def get_annapurna_data():
    url = "https://www.indicka-restaurace-annapurna.cz/brno/cz/weekly.html"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    res_name = "Annapurna"
    
    days_map = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri"}
    current_day_idx = datetime.now().weekday()
    
    if current_day_idx > 4: 
        return {"name": res_name, "items": ["Weekend - Closed — "]}

    day_key = days_map[current_day_idx]

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        day_container = soup.find('div', {'mc-data': day_key, 'mc-target': 'weeklyMenuTab'})
        
        if not day_container:
            return {"name": res_name, "items": ["Menu not found — "]}

        items = []
        

        soup_items = day_container.find_all('div', {'mc-template': 'soup'})
        for s in soup_items:
            en_name = s.find('span', class_='weekly-menu-text18').get_text(strip=True)
            cs_desc = s.find('span', class_='weekly-menu-text22').get_text(strip=True)
            price = s.find('span', class_='weekly-menu-text20').get_text(strip=True)
            items.append(f"{en_name} ≅ {cs_desc} — {price} Kč")


        main_items = day_container.find_all('div', {'mc-template': 'main'})
        for m in main_items:
            en_name = m.find('span', class_='weekly-menu-text28').get_text(strip=True)
            cs_desc = m.find('span', class_='weekly-menu-text32').get_text(strip=True)
            price = m.find('span', class_='weekly-menu-text30').get_text(strip=True)
            items.append(f"{en_name} ≅ {cs_desc} — {price} Kč")

        return {"name": res_name, "items": items}
    except Exception as e:
        return {"name": res_name, "error": str(e), "items": []}

if __name__ == "__main__":

    menicka_res = [
        {"id": "6956", "name": "Masný růžek", "prices": None},
        {"id": "4108", "name": "Veg8 Cafe", "prices": ["40 Kč", "130 Kč", "150 Kč"]},
        {"id": "8722", "name": "Deli-Tree", "prices": None},
    ]
    
    final_data = {}

    for res in menicka_res:
        final_data[res['id']] = get_menicka_data(res['id'], res['name'], res['prices'])

    final_data['annapurna'] = get_annapurna_data()

    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
