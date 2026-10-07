import json
import re
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import random

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

def autoscout_scraper(url_template, max_pages=20):
    """Legge i dati degli annunci dal JSON __NEXT_DATA__ della pagina (più stabile delle classi CSS)."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    colonne = ['Annuncio', 'Link', 'Marca', 'Modello', 'Modello_plus_info', 'Prezzo', 'Chilometraggio',
               'Cambio', 'Immatricolazione', 'Carburante', 'CV', 'Località', 'Venditore']
    all_listings = []

    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        try:
            response = requests.get(url_template.format(page), headers=headers)
            response.raise_for_status()
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.S)
            props = json.loads(m.group(1))['props']['pageProps']
        except (requests.exceptions.RequestException, AttributeError, KeyError, ValueError) as e:
            print(f"Error fetching page {page}: {e}")
            break

        listings = props.get('listings') or []
        if not listings:
            print(f"Nessun annuncio trovato nella pagina {page}. Terminando.")
            break

        for l in listings:
            v, loc, seller = l.get('vehicle', {}), l.get('location', {}), l.get('seller', {})
            det = {d.get('iconName'): d.get('data') for d in l.get('vehicleDetails', [])}
            info = v.get('modelVersionInput') or "N/A"
            privato = seller.get('type') != 'Dealer'
            indirizzo = f"IT-{loc.get('zip', '')} {loc.get('city', '')}".strip()
            all_listings.append({
                'Annuncio': f"{v.get('make')} {v.get('model')} {info}".strip(),
                'Link': "https://www.autoscout24.it" + l.get('url', ''),
                'Marca': v.get('make'),
                'Modello': v.get('model'),
                'Modello_plus_info': info,
                'Prezzo': l.get('price', {}).get('priceRaw'),
                'Chilometraggio': pd.to_numeric(re.sub(r'[^0-9]', '', v.get('mileageInKm') or ''), errors='coerce'),
                'Cambio': v.get('transmission'),
                'Immatricolazione': (l.get('tracking', {}).get('firstRegistration') or '').replace('-', '/') or None,
                'Carburante': v.get('fuel'),
                'CV': det.get('speedometer'),
                'Località': f"Privato,{indirizzo}" if privato else f"{seller.get('companyName', '')} • {indirizzo}",
                'Venditore': "Privato" if privato else "Rivenditore",
            })

        if page >= props.get('numberOfPages', 1):
            break
        time.sleep(random.uniform(2, 4))

    return pd.DataFrame(all_listings, columns=colonne)  # vuoto ma con colonne se nessun annuncio


def autosupermarket_scraper(url_base, max_pages=None):
    """Serve Chrome: i dettagli (km, cambio, ...) vengono resi lato client, il server manda solo schede 'semplici'."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)
    sep = "&" if "?" in url_base else "?"
    dati, visti = [], set()
    page_num = 1

    while True:
        url = f"{url_base}{sep}page={page_num}"
        print(f"Caricamento pagina {page_num}: {url}")
        driver.get(url)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.listing-card div.data-row")))
        except Exception:
            print("Timeout o nessun annuncio trovato")
            break

        schede = BeautifulSoup(driver.page_source, 'html.parser').select("div.listing-card")
        nuove = 0
        for c in schede:
            testo = lambda q: (c.select_one(q).get_text(" ", strip=True) if c.select_one(q) else None)
            link = c.select_one("a.listing-card-overlay")
            link = link["href"] if link else None
            if not link or link in visti:
                continue
            visti.add(link)
            nuove += 1
            if not c.select_one("div.data-row"):  # schede "semplici" senza dettagli: inutilizzabili
                continue
            # valori "etichetta -> valore" della griglia dettagli (Chilometri, Cambio, Alimentazione, ...)
            det = {}
            for p in c.select("div.data-row p.fw-medium"):
                lab = p.find_previous_sibling("div")
                if lab:
                    det[lab.get_text(strip=True)] = p.get_text(strip=True)
            prezzo = c.select_one("div.fs-2")
            prezzo = prezzo.find(string=True, recursive=False) if prezzo else None
            dati.append({
                "Annuncio": testo(".listing-card-title"),
                "Modello": testo(".listing-card-title span"),
                "Link": link,
                "Prezzo": f"{prezzo.strip()} €" if prezzo else None,
                "Chilometraggio": det.get("Chilometri"),
                "Cambio": det.get("Cambio"),
                "Immatricolazione": det.get("Immatricolazione"),
                "Carburante": det.get("Alimentazione"),
                "Tipologia": det.get("Condizione"),
                "CV": det.get("Motore"),
                "Località": testo("p.text-ellipsis + span"),
            })

        print(f"Annunci nuovi: {nuove}")
        if not nuove:  # oltre l'ultima pagina il sito ripropone l'ultima
            break
        if max_pages and page_num >= max_pages:
            print(f"Raggiunto limite massimo di pagine: {max_pages}")
            break
        page_num += 1
        time.sleep(random.uniform(1, 2))

    driver.quit()
    return pd.DataFrame(dati)

def automobile_it_scraper(url_base, max_pages=None):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.page_load_strategy = 'eager'  # carica più velocemente (non aspetta tutte le risorse)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 30)

    dati = []
    page_num = 1
    cookie_gestiti = False
    localita_gestita = False

    while True:
        # Costruzione URL
        if page_num == 1:
            url = url_base
        else:
            if "?" in url_base:
                parts = url_base.split("?")
                url = f"{parts[0]}/page-{page_num}?{parts[1]}"
            else:
                url = f"{url_base}/page-{page_num}"

        print(f"Caricamento pagina {page_num}: {url}")
        
        try:
            driver.set_page_load_timeout(180)
            driver.get(url)
        except Exception as e:
            print(f"⚠ Timeout nel caricamento di {url}: {e}")
            page_num += 1
            continue

        # Gestione popup cookie (solo la prima volta)
        if not cookie_gestiti:
            try:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#didomi-notice-agree-button"))).click()
                print("✅ Cookie accettati")
                cookie_gestiti = True
                time.sleep(2)
            except:
                print("⚠ Nessun banner cookie trovato")

        # Gestione popup località (solo la prima volta)
        if not localita_gestita:
            try:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ModalClose"))).click()
                print("✅ Popup località chiuso")
                localita_gestita = True
                time.sleep(1)
            except:
                print("⚠ Nessun popup località trovato")

        # Attendi caricamento annunci
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.CardAd")))
        except:
            print("❌ Timeout o nessun annuncio trovato")
            break

        annunci = driver.find_elements(By.CSS_SELECTOR, "a.CardAd")
        print(f"📌 Annunci trovati: {len(annunci)}")

        if not annunci:
            print("Fine annunci.")
            break

        for annuncio in annunci:
            try:
                titolo = annuncio.find_element(By.CSS_SELECTOR, "h2.Card__Title").text.strip()
                prezzo = annuncio.find_element(By.CSS_SELECTOR, "div.Card__InfoPrice span").text.strip()
                link = annuncio.get_attribute("href")
                if not link.startswith("http"):
                    link = "https://www.automobile.it" + link

                dettagli = [li.text.strip() for li in annuncio.find_elements(By.CSS_SELECTOR, "ul li.Card__InfoTag")]

                def get_detail(idx):
                    return dettagli[idx] if len(dettagli) > idx else None

                tipologia = get_detail(0)
                immatricolazione = get_detail(1)
                chilometri = get_detail(2)
                carburante = get_detail(3)
                cambio = get_detail(4)
                unico_proprietario = get_detail(5)

                try:
                    localita = annuncio.find_element(By.CSS_SELECTOR, "div.Card__InfoLocation span").text.strip()
                except:
                    localita = ""

                dati.append({
                    "Annuncio": titolo,
                    "Link": link,
                    "Prezzo": prezzo,
                    "Tipologia": tipologia,
                    "Immatricolazione": immatricolazione,
                    "Chilometraggio": chilometri,
                    "Carburante": carburante,
                    "Cambio": cambio,
                    "Unico_Proprietario": unico_proprietario,
                    "Località": localita
                })

            except Exception as e:
                print(f"Errore su annuncio: {e}")

        # Controllo se fermarsi
        if max_pages and page_num >= max_pages:
            print(f"Raggiunto limite massimo di pagine: {max_pages}")
            break

        # Verifica se esiste pagina successiva
        try:
            driver.find_element(By.CSS_SELECTOR, "li.disabled a[aria-label='Pagina successiva']")
            print("Ultima pagina raggiunta.")
            break
        except:
            page_num += 1
            time.sleep(random.uniform(2, 5))

    driver.quit()
    return pd.DataFrame(dati)

def subito_scraper(url_base, max_pages=None):
    """Legge gli annunci dal JSON __NEXT_DATA__ (le classi CSS di Subito cambiano spesso; serve Chrome non headless: il sito blocca requests)."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    results, visti = [], set()
    page_num, cookie_gestiti, tot_pagine = 1, False, 1

    while page_num <= tot_pagine:
        if page_num == 1:
            url = url_base
        elif "?" in url_base:
            base, query = url_base.split("?", 1)
            url = f"{base}?o={page_num}&{query}"
        else:
            url = f"{url_base}?o={page_num}"
        print(f"Caricamento pagina {page_num}: {url}")
        try:
            driver.set_page_load_timeout(120)
            driver.get(url)
        except Exception as e:
            print(f"⚠ Timeout caricando {url}: {e}")
            break

        if not cookie_gestiti:
            try:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#didomi-notice-agree-button"))).click()
                cookie_gestiti = True
                time.sleep(2)
            except Exception:
                print("⚠ Nessun banner cookie trovato")

        try:
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', driver.page_source, re.S)
            items = json.loads(m.group(1))['props']['pageProps']['initialState']['items']
        except (AttributeError, KeyError, ValueError):
            print("❌ Dati annunci non trovati (pagina bloccata o finita).")
            break
        tot_pagine = min(items.get('totalPages', 1), max_pages or 10**9)

        nuovi = 0
        for ad in items.get('originalList', []):
            link = ad.get('urls', {}).get('default')
            if not link or link in visti:
                continue
            visti.add(link)
            nuovi += 1
            f = lambda uri: next((v['value'] for v in ad.get('features', {}).get(uri, {}).get('values', [])), None)
            geo = ad.get('geo', {})
            results.append({
                'Annuncio': ad.get('subject'),
                'Prezzo': pd.to_numeric(next((v['key'] for v in ad.get('features', {}).get('/price', {}).get('values', [])), None), errors='coerce'),  # numerico: il formato '8999 €' non passa da pulisci_prezzo
                'Tipologia': f('/vehicle_status'),
                'Immatricolazione': f('/register_date') or f('/year'),
                'Chilometraggio': f('/mileage_scalar'),
                'Carburante': f('/fuel'),
                'Cambio': f('/gearbox'),
                'Classe Euro': f('/pollution'),
                'Località': geo.get('town', {}).get('value'),
                'Provincia': geo.get('city', {}).get('shortName'),
                'Venditore': "Rivenditore" if ad.get('advertiser', {}).get('company') else "Privato",
                'Link': link,
            })
        print(f"✅ Trovati {nuovi} annunci nuovi nella pagina {page_num}/{tot_pagine}")
        if not nuovi:
            break
        page_num += 1
        time.sleep(random.uniform(2, 4))

    driver.quit()
    print("✅ Scraping completato!")
    return pd.DataFrame(results)
