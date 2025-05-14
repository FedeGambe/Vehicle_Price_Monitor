# autoscout_scraper.py
import os
import re
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup

#def process_location(location_text):
#    location_text = location_text.replace('IT-', '')
#    match = re.match(r'([A-Za-z\s]+)\s-\s([A-Za-z]+),\s*(\d{5})', location_text)
#    if match:
#        locality = match.group(1).strip()
#        province = match.group(2).strip()
#        cap = match.group(3).strip()
#        return f"{locality}, {province}, {cap}"
#    else:
#        return location_text

def autoscout_scraper(url_template, max_pages=20, output_csv=None):
    #Determina il percorso di default se non specificato
    if output_csv is None:
        # Se siamo su Colab, usa /content/, altrimenti usa la directory corrente
        if 'COLAB_GPU' in os.environ:
            output_csv = '/content/classe_A_Autoscout.csv'
        else:
            output_csv = 'classe_A_Autoscout.csv'    
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    all_listings = []

    for page in range(1, max_pages + 1):
        url = url_template.format(page)
        print(f"Scraping page {page}...")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        listings = soup.find_all('article', class_='cldt-summary-full-item')

        if not listings:
            print(f"Nessun annuncio trovato nella pagina {page}. Terminando.")
            break

        for listing in listings:
            title_tag = listing.find('a', class_='ListItem_title__ndA4s')
            title = title_tag.get_text(strip=True) if title_tag else "N/A"
            link = title_tag['href'] if title_tag else "N/A"
            base_url = "https://www.autoscout24.it"
            full_link = base_url + link if link != "N/A" else "N/A"
            price_tag = listing.find('p', {'data-testid': 'regular-price'})
            price = price_tag.get_text(strip=True) if price_tag else "N/A"
            mileage_tag = listing.find('span', {'data-testid': 'VehicleDetails-mileage_road'})
            mileage = mileage_tag.get_text(strip=True) if mileage_tag else "N/A"
            transmission_tag = listing.find('span', {'data-testid': 'VehicleDetails-transmission'})
            transmission = transmission_tag.get_text(strip=True) if transmission_tag else "N/A"
            registration_date_tag = listing.find('span', {'data-testid': 'VehicleDetails-calendar'})
            registration_date = registration_date_tag.get_text(strip=True) if registration_date_tag else "N/A"
            fuel_type_tag = listing.find('span', {'data-testid': 'VehicleDetails-gas_pump'})
            fuel_type = fuel_type_tag.get_text(strip=True) if fuel_type_tag else "N/A"
            power_tag = listing.find('span', {'data-testid': 'VehicleDetails-speedometer'})
            power = power_tag.get_text(strip=True) if power_tag else "N/A"

            location_tag_private = listing.find('span', class_='SellerInfo_private__THzvQ')
            location_tag_address = listing.find('span', class_='SellerInfo_address__leRMu')

            if location_tag_private:
                location_text = location_tag_private.get_text(strip=True)
                venditore = "Privato"
            elif location_tag_address:
                location_text = location_tag_address.get_text(strip=True)
                venditore = "Rivenditore"
            else:
                location_text = "N/A"
                venditore = "N/A"

            #localita = process_location(location_text)
            localita = location_text
            all_listings.append({
                'Annuncio': title,
                'Link': full_link,
                'Prezzo': price,
                'Chilometraggio': mileage,
                'Cambio': transmission,
                'Immatricolazione': registration_date,
                'Carburante': fuel_type,
                'CV': power,
                'Località': localita,
                'Venditore': venditore
            })

        time.sleep(random.uniform(1, 3.5))

    df = pd.DataFrame(all_listings)
    df['Prezzo'] = df['Prezzo'].str.replace('[^0-9]', '', regex=True)
    df['Chilometraggio'] = df['Chilometraggio'].str.replace('[^0-9]', '', regex=True)
    df['Immatricolazione'] = pd.to_numeric(df['Immatricolazione'].str.split('/').str[1], errors='coerce').astype('Int64')
    df['CV'] = df['CV'].str.extract(r'(?:\(?(\d+)\s?CV\)?)', expand=False).astype(float)
    df.replace('', pd.NA, inplace=True)
    df['Prezzo'] = pd.to_numeric(df['Prezzo'], errors='coerce')
    df['Chilometraggio'] = pd.to_numeric(df['Chilometraggio'], errors='coerce')

    df.to_csv(output_csv, index=False)
    print(f"Dati salvati in {output_csv}")