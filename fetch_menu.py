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
    url = "https://www.indicka-restaurace-annapurna.cz/MC/HANDLERS/getDocument.php?name=WEEKLY&location=brno&language=cz"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    res_name = "Annapurna"
    
    days_map = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri"}
    current_day_idx = datetime.now().weekday()
    
    if current_day_idx > 4:
        return {"name": res_name, "items": ["Weekend - Closed — "]}

    day_key = days_map[current_day_idx]

    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.content, 'html.parser')
        
        day_container = soup.find('div', {'mc-data': day_key})
        
        if not day_container:
            return {"name": res_name, "items": ["Menu pro tento den nebylo nalezeno — "]}

        items = []

        soup_items = day_container.find_all('div', {'mc-template': 'soup'})
        for s in soup_items:
            en_name_el = s.find('span', {'mc-text': lambda x: x and 'meal_name' in x})
            cs_desc_el = s.find('span', {'mc-text': lambda x: x and 'meal_description' in x})
            price_el = s.find('span', class_='weekly-menu-text20')
            
            en_name = en_name_el.get_text(strip=True) if en_name_el else "Soup"
            cs_desc = cs_desc_el.get_text(strip=True) if cs_desc_el else ""
            price = price_el.get_text(strip=True) if price_el else "20"
            
            items.append(f"{en_name} ≅ {cs_desc} — {price} Kč")

        main_items = day_container.find_all('div', {'mc-template': 'main'})
        for m in main_items:
            en_name_el = m.find('span', {'mc-text': lambda x: x and 'MEALNAME' in x})
            cs_desc_el = m.find('span', {'mc-text': lambda x: x and 'MEALDESCRIPTION' in x})
            price_el = m.find('span', class_='weekly-menu-text30')
            
            en_name = en_name_el.get_text(strip=True) if en_name_el else "Main Dish"
            cs_desc = cs_desc_el.get_text(strip=True) if cs_desc_el else ""
            price = price_el.get_text(strip=True) if price_el else "144"
            
            items.append(f"{en_name} ≅ {cs_desc} — {price} Kč")

        return {"name": res_name, "items": items}
        
    except Exception as e:
        return {"name": res_name, "error": str(e), "items": []}

def get_sargam_data():
    url = "https://sargamrestaurace.cz/Sargam2/DMenuItems"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res_name = "Sargam 2"
    
    days_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday"}
    current_day_idx = datetime.now().weekday()
    
    if current_day_idx > 4:
        return {"name": res_name, "items": ["Closed — "]}

    target_day_id = days_map[current_day_idx]

    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        day_header = soup.find('div', id=target_day_id)
        if not day_header:
            return {"name": res_name, "items": ["Menu not found — "]}

        parent_row = day_header.find_parent('div', class_='row')
        items = []

        soup_name_el = parent_row.find('div', class_='dish-name')
        soup_price_el = parent_row.find('div', class_='dish-number flex-grow-1')
        
        if soup_name_el:
            s_name = soup_name_el.get_text(strip=True)
            s_price = soup_price_el.get_text(strip=True) if soup_price_el else ""
            items.append(f"{s_name} — {s_price}")

        main_dishes = parent_row.find_all('div', class_='dish-container')
        
        for dish in main_dishes:
            name_el = dish.find('div', class_='dish-name')
            if name_el:
                m_name = name_el.get_text(strip=True)
                
                if "all you can eat" in m_name.lower():
                    continue
                
                price_el = dish.find('div', class_='dish-number flex-grow-1')
                m_price = price_el.get_text(strip=True) if price_el else ""
                items.append(f"{m_name} — {m_price}")

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
    final_data['sargam'] = get_sargam_data()

    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
