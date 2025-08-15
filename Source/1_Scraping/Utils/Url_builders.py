# ===============================
# Funzioni per generare URL dinamici
# ===============================

# ---------- Autosupermarket ----------
def build_autosupermarket_url(marca, modello, prezzo_minimo=0, prezzo_massimo=0,
                              km_minimi=0, km_massimi=0,
                              anno_min=0, anno_max=0):
    """Genera URL per Autosupermarket con parametri dinamici."""
    url = f"https://autosupermarket.it/ricerca/{marca}/{modello}"
    params = []

    if prezzo_minimo > 0:
        params.append(f"prezzo-da-{prezzo_minimo}")
    if prezzo_massimo > 0:
        params.append(f"prezzo-a={prezzo_massimo}")
    if km_minimi > 0:
        params.append(f"km-da={km_minimi}")
    if km_massimi > 0:
        params.append(f"km-a={km_massimi}")
    if anno_min > 0:
        params.append(f"anno-da={anno_min}")
    if anno_max > 0:
        params.append(f"anno-a={anno_max}")

    if params:
        url += "?" + "&".join(params)

    return url


# ---------- Automobile.it ----------
def build_automobile_url(marca, modello, prezzo_minimo=0, prezzo_massimo=0,
                         km_minimi=0, km_massimi=0,
                         anno_min=0, anno_max=0):
    """Genera URL per Automobile.it con parametri dinamici."""
    url = f"https://www.automobile.it/{marca}-{modello}"

    if prezzo_massimo > 0:
        url += f"-{prezzo_massimo}"

    params = []
    if anno_max > 0:
        params.append(f"anno_fino_a={anno_max}")
    if anno_min > 0:
        params.append(f"immatricolazione={anno_min}")
    if km_massimi > 0:
        params.append(f"km_max={km_massimi}_km")
    if km_minimi > 0:
        params.append(f"km_min={km_minimi}_km")
    if prezzo_minimo > 0:
        params.append(f"prezzo_da={prezzo_minimo}")

    if params:
        url += "?" + "&".join(params)

    return url

# ---------- Subito.it ----------
dict_km_subito_ms = {
    0: 0, 1: 0, 2: 5000, 3: 10000, 4: 15000, 5: 20000, 6: 25000, 7: 30000,
    8: 35000, 9: 40000, 10: 45000, 11: 50000, 12: 55000, 13: 60000,
    14: 65000, 15: 70000, 16: 75000, 17: 80000, 18: 85000, 19: 90000,
    20: 95000, 21: 100000, 22: 110000, 23: 120000, 24: 130000,
    25: 140000, 26: 150000
}
dict_km_subito_me = {
    0: 0, 1: 5000, 2: 10000, 3: 15000, 4: 20000, 5: 25000, 6: 30000,
    7: 35000, 8: 40000, 9: 45000, 10: 50000, 11: 55000, 12: 60000,
    13: 65000, 14: 70000, 15: 75000, 16: 80000, 17: 85000, 18: 90000,
    19: 95000, 20: 100000, 21: 110000, 22: 120000, 23: 130000,
    24: 140000, 25: 150000, 26: 160000
}
def build_subito_url(marca, modello, prezzo_minimo=0, prezzo_massimo=0,
                     km_minimi=0, km_massimi=0,
                     anno_min=0, anno_max=0):
    """Genera URL per Subito.it con mapping dei range km."""
    def get_km_code(value, mapping, min_side=True):
        if value <= 0:
            return 0
        items = sorted(mapping.items(), key=lambda x: x[1])
        if min_side:  # ms
            for k, v in items:
                if v >= value:
                    return k
            return max(mapping.keys())
        else:  # me
            for k, v in reversed(items):
                if v <= value:
                    return k
            return min(mapping.keys())

    ms_code = get_km_code(km_minimi, dict_km_subito_ms, min_side=True)
    me_code = get_km_code(km_massimi, dict_km_subito_me, min_side=False)

    url = f"https://www.subito.it/annunci-italia/vendita/auto/{marca}/{modello}/?"
    params = []

    if prezzo_minimo > 0:
        params.append(f"ps={prezzo_minimo}")
    if prezzo_massimo > 0:
        params.append(f"pe={prezzo_massimo}")
    if ms_code > 0:
        params.append(f"ms={ms_code}")
    if me_code > 0:
        params.append(f"me={me_code}")
    if anno_min > 0:
        params.append(f"ys={anno_min}")
    if anno_max > 0:
        params.append(f"ye={anno_max}")

    if params:
        url += "&".join(params)

    return url

# ---------- Autotorino ----------
def build_autotorino_url(marca_sito, modello_sito,
                         prezzo_minimo=0, prezzo_massimo=0,
                         km_minimi=0, km_massimi=0,
                         anno_min=0, anno_max=0):
    """
    Genera URL per Autotorino.it con i parametri specifici.
    marca_sito e modello_sito devono essere i codici interni del sito.
    """

    url = "https://www.autotorino.it/veicoli/auto?"
    params = []

    # Immatricolazione (anno)
    if anno_min > 0 or anno_max > 0:
        anno_min = anno_min if anno_min > 0 else ""
        anno_max = anno_max if anno_max > 0 else ""
        params.append(f"immatricolazione_anno={anno_min}-{anno_max}")

    # Chilometri
    if km_minimi > 0 or km_massimi > 0:
        km_min = km_minimi if km_minimi > 0 else 0
        km_max = km_massimi if km_massimi > 0 else 999999
        params.append(f"km={km_min}-{km_max}")

    # Marca e modello (codici forniti)
    if marca_sito:
        params.append(f"marca_sito={marca_sito}")
    if modello_sito:
        params.append(f"modello_sito={modello_sito}")

    # Prezzo
    if prezzo_minimo > 0 or prezzo_massimo > 0:
        p_min = prezzo_minimo if prezzo_minimo > 0 else 0
        p_max = prezzo_massimo if prezzo_massimo > 0 else 999999
        params.append(f"price={p_min}-{p_max}")

    if params:
        url += "&".join(params)

    return url

# ---------- Autoscout ----------
def bild_autoscout_url(marca_sito, modello_sito,
                         prezzo_minimo=0, prezzo_massimo=0,
                         km_minimi=0, km_massimi=0,
                         anno_min=0, anno_max=0):
    url = f"https://www.autoscout24.it/lst/{marca_sito}/{modello_sito}?atype=C&cy=I&damaged_listing=exclude&desc=1&?"

    if prezzo_massimo > 0:
        url += f"-{prezzo_massimo}"

    params = []
    if anno_max > 0:
        params.append(f"fregfrom={anno_min}")
    if anno_min > 0:
        params.append(f"fregto={anno_max}")
    if km_massimi > 0:
        params.append(f"kmfrom={km_massimi}_km")
    if km_minimi > 0:
        params.append(f"kmto={km_minimi}_km")
    params.append("powertype=kw")
    if prezzo_minimo > 0:
        params.append(f"pricefrom={prezzo_minimo}")
    if prezzo_massimo > 0:
        params.append(f"priceto={prezzo_minimo}")
    params.append("search_id=2bu1025n5if&sort=standard&source=homepage_search-mask&ustate=N%2CU")

    if params:
        url += "?" + "&".join(params)

    return url

def bild_autoscout_urls(marca_sito, modello_sito,
                        prezzo_minimo=0, prezzo_massimo=0,
                        km_minimi=0, km_massimi=0,
                        anno_min=0, anno_max=0):
    if prezzo_minimo <= 0:
        prezzo_minimo = 0

    urls = []

    # Se prezzo_massimo è 0 o minore di minimo, consideriamo solo una url
    if prezzo_massimo == 0 or prezzo_massimo <= prezzo_minimo:
        prezzo_massimo = prezzo_minimo + 1000

    # Creiamo gli intervalli di 1000
    for start in range(prezzo_minimo, prezzo_massimo, 1000):
        end = min(start + 1000, prezzo_massimo)

        url = f"https://www.autoscout24.it/lst/{marca_sito}/{modello_sito}?atype=C&cy=I&damaged_listing=exclude&desc=1"

        params = []
        if anno_min > 0:
            params.append(f"fregfrom={anno_min}")
        if anno_max > 0:
            params.append(f"fregto={anno_max}")
        if km_minimi > 0:
            params.append(f"kmfrom={km_minimi}_km")
        if km_massimi > 0:
            params.append(f"kmto={km_massimi}_km")

        params.append("powertype=kw")
        params.append(f"pricefrom={start}")
        params.append(f"priceto={end}")
        params.append("search_id=2bu1025n5if&sort=standard&source=homepage_search-mask&ustate=N%2CU")

        url += "&" + "&".join(params)
        urls.append(url)

    return urls