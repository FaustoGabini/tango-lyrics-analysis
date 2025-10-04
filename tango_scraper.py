from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# Configurar Chrome en modo headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-infobars")
options.add_argument("--disable-popup-blocking")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--incognito")

# Inicializar el driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Paso 1: Obtener los links de los tangos
base_url = "https://www.todotango.com/musica/obras/letras/-/7/Tango/"
driver.get(base_url)
time.sleep(1)

song_links = []
anchors = driver.find_elements(By.CSS_SELECTOR, "div.itemlista a")
for a in anchors:
    href = a.get_attribute("href")
    if href and href not in song_links:
        song_links.append(href)

print(f"🎵 Total de canciones encontradas: {len(song_links)}")

# Paso 2: Procesar las primeras 10 canciones
song_links = song_links[:5]
canciones = []

for i, link in enumerate(song_links, start=1):
    print(f"{i}. Procesando: {link}")
    driver.get(link)
    time.sleep(1)

    page = BeautifulSoup(driver.page_source, 'html.parser')

    # Extraer la letra
    letra = ""
    span_letra = page.select_one('span#main_Tema1_lbl_Letra')
    if span_letra:
        versos = [t.strip() for t in span_letra.stripped_strings if t.strip()]
        letra = " ".join(versos)

    # Extraer el título
    titulo = ""
    titulo_tag = page.select_one('span#main_Tema1_lbl_Titulo')
    if titulo_tag:
        titulo = titulo_tag.get_text(strip=True)

    # Extraer autores
    autores = []
    autor_tags = page.select('a[id^="main_Tema1_Tema_Autores1_RP_TemasCreadores_AutoresLetra_hl_Creador_"]')
    for a in autor_tags:
        nombre = a.get_text(strip=True)
        if nombre:
            autores.append(nombre)

    autor = ", ".join(autores)
    canciones.append({
        "titulo": titulo,
        "autor": autor,
        "letra": letra
    })

# Cerrar el navegador
driver.quit()

# Mostrar resultados
print("\n🎼 Canciones extraídas:")
for c in canciones:
    print(f"- {c['titulo']} -> {c['autor']}")


# Crear DataFrame y guardar en CSV
df = pd.DataFrame(canciones)
df.to_csv("tangos.csv", index=False, encoding='utf-8-sig')

print("\n📁 Archivo 'tangos.csv' guardado exitosamente.")