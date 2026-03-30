import requests
from bs4 import BeautifulSoup
import json

def get_menu_data(res_id, res_name, manual_prices=None):
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
                    # Pokud máme fixní ceny (pro druhou restauraci)
                    if manual_prices and idx < len(manual_prices):
                        prize_text = manual_prices[idx]
                    else:
                        prize_text = prize_td.get_text(strip=True) if prize_td else ""
                    
                    if food_text:
                        items.append(f"{food_text} — {prize_text}")

        return {"name": res_name, "items": items}
    except Exception as e:
        return {"name": res_name, "error": str(e), "items": []}

if __name__ == "__main__":

    restaurants = [
        {"id": "6956", "name": "Masný růžek", "prices": None},
        {"id": "4108", "name": "Veg8 Cafe", "prices": ["40 Kč", "130 Kč", "150 Kč"]}
    ]
    
    final_data = {}
    for res in restaurants:
        final_data[res['id']] = get_menu_data(res['id'], res['name'], res['prices'])

    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
