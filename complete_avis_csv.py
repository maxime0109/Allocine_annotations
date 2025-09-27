import pandas as pd
import requests
from bs4 import BeautifulSoup

# Charger le fichier CSV dans un DataFrame
df = pd.read_csv('./data/avis_film_fr_sample.csv', delimiter=';')

df['film_id'] = df['film-url'].str.extract(r'fichefilm-(\d+)')

# Créer la colonne avec l'URL Allociné
df['allocine_url'] = df['film_id'].apply(
    lambda x: f'https://www.allocine.fr/film/fichefilm_gen_cfilm={x}.html' if pd.notnull(x) else None
)

def get_title_from_allocine(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_div = soup.find('div', class_='titlebar-title titlebar-title-xl')
        if title_div:
            print(f"Titre récupéré depuis Allociné : {title_div.text.strip()}")
            return title_div.text.strip()
        else:
            print("Aucun titre trouvé sur la page Allociné.")
            return None
    except Exception:
        return None

def get_poster_src_from_allocine(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('img', class_='thumbnail-img')
        if img_tag and img_tag.has_attr('src'):
            print(f"Poster récupéré depuis Allociné : {img_tag['src']}")
            return img_tag['src']
        else:
            print("Aucun poster trouvé sur la page Allociné.")
            return None
    except Exception:
        print("Erreur lors de la récupération du poster depuis Allociné.")
        return None

# Ajouter la colonne 'titre' en récupérant le titre via webscraping
df['titre'] = df['allocine_url'].apply(get_title_from_allocine)

# Ajouter la colonne 'poster_url' en récupérant le src de l'image
df['poster_url'] = df['allocine_url'].apply(get_poster_src_from_allocine)

# Afficher les premières lignes du DataFrame
print(df.head())
df.to_csv('./data/avis_film_fr_sample.csv', sep=';', index=False)