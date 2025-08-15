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

def autoscout_scraper(url_template, max_pages=20, #output_csv=None
                      ):
    """
    #Determina il percorso di default se non specificato
    if output_csv is None:
        # Se siamo su Colab, usa /content/, altrimenti usa la directory corrente
        if 'COLAB_GPU' in os.environ:
            output_csv = '/content/data_scaper_Autoscout.csv'
        else:
            output_csv = 'data_scaper_Autoscout.csv'    
    """
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
            # Estrazione Marca, Modello e Modello_plus_info
            h2_tag = listing.find('h2')
            if h2_tag:
                spans = h2_tag.find_all('span')
                marca = spans[0].get_text(strip=True) if len(spans) > 0 else "N/A"
                modello = spans[1].get_text(strip=True) if len(spans) > 1 else "N/A"
                modello_plus_info_tag = h2_tag.find('span', class_='ListItem_version__5EWfi')
                modello_plus_info = modello_plus_info_tag.get_text(strip=True) if modello_plus_info_tag else "N/A"
                annuncio = f"{marca} {modello} {modello_plus_info}" if modello_plus_info != "N/A" else f"{marca} {modello}"
            else:
                marca, modello, modello_plus_info, annuncio = "N/A", "N/A", "N/A", "N/A"
            title_tag = listing.find('a', class_='ListItem_title__ndA4s')
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
                'Annuncio': annuncio,
                'Link': full_link,
                'Marca': marca,
                'Modello': modello,
                'Modello_plus_info': modello_plus_info,
                'Prezzo': price,
                'Chilometraggio': mileage,
                'Cambio': transmission,
                'Immatricolazione': registration_date,
                'Carburante': fuel_type,
                'CV': power,
                'Località': localita,
                'Venditore': venditore
            })

        time.sleep(random.uniform(5, 10))

    df = pd.DataFrame(all_listings)
    df['Prezzo'] = df['Prezzo'].str.replace('[^0-9]', '', regex=True)
    df['Chilometraggio'] = df['Chilometraggio'].str.replace('[^0-9]', '', regex=True)
    #df['Immatricolazione'] = pd.to_numeric(df['Immatricolazione'].str.split('/').str[1], errors='coerce').astype('Int64')
    #df['CV'] = df['CV'].str.extract(r'(?:\(?(\d+)\s?CV\)?)', expand=False).astype(float)
    df.replace('', pd.NA, inplace=True)
    df['Prezzo'] = pd.to_numeric(df['Prezzo'], errors='coerce')
    df['Chilometraggio'] = pd.to_numeric(df['Chilometraggio'], errors='coerce')

    #df.to_csv(output_csv, index=False)
    #print(f"Dati salvati in {output_csv}")
    return df

def autosupermarket_scraper(url_base, max_pages=None):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    dati = []
    page_num = 1

    while True:
        url = f"{url_base}&page={page_num}"
        print(f"Caricamento pagina {page_num}: {url}")
        driver.get(url)

        # Aspetta che tutti gli annunci siano presenti
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.listing-card-link")))
        except:
            print("Timeout o nessun annuncio trovato")
            break

        annunci = driver.find_elements(By.CSS_SELECTOR, "a.listing-card-link")
        print(f"Annunci trovati: {len(annunci)}")

        if not annunci:
            print("Nessun annuncio trovato, probabilmente pagina finale.")
            break

        for annuncio in annunci:
            try:
                titolo = annuncio.find_element(By.CSS_SELECTOR, "h3.listing-card-title").text.replace('\n', ' ').strip()
                modello = annuncio.find_element(By.CSS_SELECTOR, "h3.listing-card-title span.text-muted").text.strip()
                link = annuncio.get_attribute("href")
                prezzo = annuncio.find_element(By.CSS_SELECTOR, "span.price").text.strip()

                dettagli_divs = annuncio.find_elements(By.CSS_SELECTOR, "div.row.data-row div.col-6 p.fw-medium")
                dettagli = [d.text.strip() for d in dettagli_divs]
                def get_detail(dettagli, index):
                    return dettagli[index] if len(dettagli) > index else None

                chilometri = get_detail(dettagli, 0)
                cambio = get_detail(dettagli, 1)
                immatricolazione = get_detail(dettagli, 2)
                alimentazione = get_detail(dettagli, 3)
                tipologia = get_detail(dettagli, 4)
                motore = get_detail(dettagli, 5)

                try:
                    localita = annuncio.find_element(By.CSS_SELECTOR, "div.fs-sm.flex-grow-1 span.text-muted").text.strip()
                except:
                    localita = ""

                dati.append({
                    "Annuncio": titolo,
                    "Modello": modello,
                    "Link": link,
                    "Prezzo": prezzo,
                    "Chilometraggio": chilometri,
                    "Cambio": cambio,
                    "Immatricolazione": immatricolazione,
                    "Carburante": alimentazione,
                    "Tipologia": tipologia,
                    "CV": motore,
                    "Località": localita
                })
            except Exception as e:
                print(f"Errore su annuncio: {e}")

        if max_pages and page_num >= max_pages:
            print(f"Raggiunto limite massimo di pagine: {max_pages}")
            break

        try:
            driver.find_element(By.CSS_SELECTOR, "li.page-item.next a.disabled")
            print("Ultima pagina raggiunta.")
            break
        except:
            page_num += 1

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
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.page_load_strategy = 'eager'  # carica più veloce

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    results = []
    page_num = 1
    cookie_gestiti = False

    while True:
        # Costruzione URL con paginazione
        if page_num == 1:
            url = url_base
        else:
            if "?" in url_base:
                parts = url_base.split("?")
                url = f"{parts[0]}?o={page_num}&{parts[1]}"
            else:
                url = f"{url_base}?o={page_num}"

        print(f"\nCaricamento pagina {page_num}: {url}")

        try:
            driver.set_page_load_timeout(120)
            driver.get(url)
        except Exception as e:
            print(f"⚠ Timeout caricando {url}: {e}")
            page_num += 1
            continue

        # Gestione cookie solo la prima volta
        if not cookie_gestiti:
            try:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#didomi-notice-agree-button"))).click()
                print("✅ Cookie accettati")
                cookie_gestiti = True
                time.sleep(2)
            except:
                print("⚠ Nessun banner cookie trovato")

        # Attendi caricamento annunci
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.BigCard-module_link__kVqPE")))
        except:
            print("❌ Nessun annuncio trovato o pagina finita.")
            break

        ads = driver.find_elements(By.CSS_SELECTOR, "a.BigCard-module_link__kVqPE")
        print(f"✅ Trovati {len(ads)} annunci nella pagina {page_num}")

        if not ads:
            print("Fine annunci.")
            break

        # Parsing annunci
        for ad in ads:
            try:
                link = ad.get_attribute("href")
                titolo = ""
                try:
                    titolo = ad.find_element(By.CSS_SELECTOR, "h2.BigCard-module_card-title__Cgcnt").text.strip()
                except:
                    pass

                # Se titolo vuoto, ricostruiscilo dall'URL
                if not titolo:
                    raw_text = link.split("/auto/")[1].split("-")[0:-2]
                    words = raw_text
                    new_words = []
                    i = 0
                    while i < len(words):
                        if words[i].isdigit() and i+1 < len(words) and len(words[i+1]) == 1:
                            new_words.append(words[i] + "." + words[i+1])
                            i += 2
                        else:
                            new_words.append(words[i])
                            i += 1
                    titolo = " ".join(new_words).title().replace("Cv", "CV")

                prezzo = ad.find_element(By.CSS_SELECTOR, ".index-module_price__N7M2x").text.strip()

                localita_el = ad.find_element(By.CSS_SELECTOR, ".PostingTimeAndPlace-module_date-location__1Owcv")
                localita = localita_el.find_element(By.CSS_SELECTOR, ".index-module_town__2H3jy").text.strip()
                provincia = localita_el.find_element(By.CSS_SELECTOR, ".city").text.strip("()")

                rivenditore = "Rivenditore" if "Rivenditore" in ad.text else "Privato"

                info_elements = ad.find_elements(By.CSS_SELECTOR, ".index-module_info__GDGgZ")
                info_texts = [e.text.strip() for e in info_elements]

                tipologia = info_texts[0] if len(info_texts) > 0 else None
                immatricolazione = info_texts[1] if len(info_texts) > 1 else None
                km = carburante = cambio = euro = None

                if tipologia in ["Km0", "Nuovo"]:
                    if len(info_texts) > 2: carburante = info_texts[2]
                    if len(info_texts) > 3: cambio = info_texts[3]
                    if len(info_texts) > 4: euro = info_texts[4]
                else:
                    if len(info_texts) > 2: km = info_texts[2]
                    if len(info_texts) > 3: carburante = info_texts[3]
                    if len(info_texts) > 4: cambio = info_texts[4]
                    if len(info_texts) > 5: euro = info_texts[5]

                results.append({
                    "Annuncio": titolo,
                    "Prezzo": prezzo,
                    "Tipologia": tipologia,
                    "Immatricolazione": immatricolazione,
                    "Chilometraggio": km,
                    "Carburante": carburante,
                    "Cambio": cambio,
                    "Classe Euro": euro,
                    "Località": localita,
                    "Provincia": provincia,
                    "Venditore": rivenditore,
                    "Link": link
                })

            except Exception as e:
                print(f"Errore in annuncio: {e}")
                continue

        # Controllo limite pagine
        if max_pages and page_num >= max_pages:
            print(f"Raggiunto limite massimo di pagine: {max_pages}")
            break

        # Verifica se ci sono altre pagine
        try:
            driver.find_element(By.CSS_SELECTOR, "li.disabled a[aria-label='Pagina successiva']")
            print("Ultima pagina raggiunta.")
            break
        except:
            page_num += 1
            time.sleep(random.uniform(2, 5))

    driver.quit()
    print("\n✅ Scraping completato!")
    return pd.DataFrame(results)