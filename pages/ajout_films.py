import dash
from dash import html, dcc, Output, Input, State
from app_instance import app
import requests
from bs4 import BeautifulSoup
import csv
import os
import urllib.parse
import re

# --- Fonctions de récupération ---
def get_film_title(url):
    url = url.rstrip("/")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_div = soup.find('div', class_='titlebar-title titlebar-title-xl')
        if title_div:
            return title_div.text.strip()
        return None
    except Exception:
        return None

def get_poster_url(url):
    url = url.rstrip("/")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('img', class_='thumbnail-img')
        if img_tag and img_tag.has_attr('src'):
            return img_tag['src']
        return None
    except Exception:
        return None

def extract_allocine_id(url):
    match = re.search(r'cfilm=(\d+)', url)
    return match.group(1) if match else ""

# --- Layout Dash ---
layout = html.Div([
    dcc.Location(id='url-ajout-films', refresh=False),
    
    html.Div([
        # En-tête
        html.Div([
            html.H2("🎬 Ajouter un film", style={
                'fontSize': '2.5em',
                'fontWeight': '300',
                'marginBottom': '10px',
                'textShadow': '0 2px 4px rgba(0, 0, 0, 0.3)',
                'color': 'white'
            }),
            html.Div("Ajoutez un nouveau film à votre collection", style={
                'fontSize': '1.1em',
                'opacity': '0.9',
                'fontWeight': '300',
                'color': 'white'
            })
        ], style={
            'background': 'linear-gradient(45deg, #667eea, #764ba2)',
            'color': 'white',
            'textAlign': 'center',
            'padding': '30px'
        }),
        
        # Contenu principal
        html.Div([
            html.Div([
                html.Label("Lien allociné du film", htmlFor="film-link", style={
                    'display': 'block',
                    'marginBottom': '10px',
                    'fontWeight': '500',
                    'color': '#333',
                    'fontSize': '1.1em'
                }),
                dcc.Input(
                    id="film-link",
                    type="text",
                    placeholder="Entrez le lien du film Allociné",
                    value="",
                    style={
                        'width': '100%',
                        'padding': '15px',
                        'border': '2px solid #e8e8e8',
                        'borderRadius': '10px',
                        'fontSize': '1em',
                        'transition': 'border-color 0.3s ease'
                    }
                ),
            ], style={'marginBottom': '25px'}),
            
            html.Div([
                html.Label("Commentaire", htmlFor="film-commentaire", style={
                    'display': 'block',
                    'marginBottom': '10px',
                    'fontWeight': '500',
                    'color': '#333',
                    'fontSize': '1.1em'
                }),
                dcc.Input(
                    id="film-commentaire",
                    type="text",
                    placeholder="Entrez votre commentaire",
                    value="",
                    style={
                        'width': '100%',
                        'padding': '15px',
                        'border': '2px solid #e8e8e8',
                        'borderRadius': '10px',
                        'fontSize': '1em',
                        'transition': 'border-color 0.3s ease'
                    }
                ),
            ], style={'marginBottom': '30px'}),
            
            html.Button("Valider", id="valider-btn", n_clicks=0, style={
                'backgroundColor': '#667eea',
                'color': 'white',
                'border': 'none',
                'padding': '15px 30px',
                'borderRadius': '25px',
                'fontSize': '1.1em',
                'fontWeight': '600',
                'cursor': 'pointer',
                'transition': 'all 0.3s ease',
                'boxShadow': '0 4px 15px rgba(102, 126, 234, 0.3)',
                'marginBottom': '20px'
            }),
            
            html.Div(id="confirmation", style={'marginTop': '20px'}),
            
            html.Div([
                dcc.Link(
                    'Retour au menu principal',
                    id='retour-link',
                    href="/main",
                    style={
                        'display': 'inline-block',
                        'padding': '12px 24px',
                        'backgroundColor': '#764ba2',
                        'color': 'white',
                        'textDecoration': 'none',
                        'borderRadius': '25px',
                        'fontSize': '0.9em',
                        'fontWeight': '500',
                        'transition': 'all 0.3s ease',
                        'boxShadow': '0 4px 15px rgba(118, 75, 162, 0.3)'
                    }
                )
            ], style={'textAlign': 'center', 'marginTop': '30px'})
            
        ], style={
            'padding': '40px',
            'backgroundColor': 'white',
            'maxWidth': '600px',
            'margin': '0 auto'
        })
        
    ], style={
        'maxWidth': '800px',
        'margin': '0 auto',
        'background': 'rgba(255, 255, 255, 0.95)',
        'borderRadius': '15px',
        'boxShadow': '0 20px 40px rgba(0, 0, 0, 0.1)',
        'overflow': 'hidden'
    })
    
], style={
    'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'minHeight': '100vh',
    'padding': '20px'
})

# --- Callback pour le retour au menu principal ---
@app.callback(
    Output('retour-link', 'href'),
    Input('url-ajout-films', 'search')
)
def update_retour_link(search):
    if search:
        params = urllib.parse.parse_qs(search.lstrip('?'))
        username = params.get('username', [''])[0]
        if username:
            return f"/main?username={urllib.parse.quote(username)}"
    return "/main"

# --- Callback pour ajouter un film ---
@app.callback(
    Output("confirmation", "children"),
    Input("valider-btn", "n_clicks"),
    State("film-link", "value"),
    State("film-commentaire", "value"),
    prevent_initial_call=True
)
def ajouter_film(n_clicks, film_avis_link, film_commentaire):
    if not film_avis_link:
        return html.Div([
            "⚠️ Veuillez entrer le lien Allociné du film."
        ], style={
            'color': '#f39c12',
            'backgroundColor': '#fefbf3',
            'border': '1px solid #f39c12',
            'borderRadius': '10px',
            'padding': '15px',
            'textAlign': 'center',
            'fontSize': '1.1em'
        })

    lien = film_avis_link.rstrip("/")
    avis = film_commentaire if film_commentaire else ""
    csv_path = "./data/avis_film_fr_sample.csv"

    # Extraire l'ID Allociné
    allocine_id = extract_allocine_id(lien)

    # Film url critiques
    film_url_critiques = lien + "/critiques/spectateurs"

    # Titre et poster
    titre = get_film_title(lien)
    poster_url = get_poster_url(lien)

    # Calculer l'Id interne pour CSV
    next_id = 1
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8", newline='') as f:
            reader = csv.DictReader(f, delimiter=';')
            rows = list(reader)
            next_id = len(rows) + 1

    # Ligne à écrire
    row = {
        "Id": next_id,
        "Film url critiques": film_url_critiques,
        "Review": avis,
        "Id Allocine": allocine_id,
        "Allocine_url": lien,
        "titre": titre,
        "poster_url": poster_url
    }

    # Écriture CSV
    write_header = not os.path.exists(csv_path)
    with open(csv_path, "a", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Id","Film url critiques","Review","Id Allocine","Allocine_url","titre","poster_url"],
            delimiter=';',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL
        )
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    # Confirmation visuelle
    return html.Div([
        html.Div([
            html.H4("✅ Film ajouté avec succès !", style={
                'color': '#27ae60',
                'margin': '0 0 15px 0',
                'fontSize': '1.3em'
            }),
            html.P(f"📽️ Lien critiques : {film_url_critiques}", style={'margin': '8px 0', 'fontSize': '0.95em'}),
            html.P(f"💬 Commentaire : {avis if avis else 'Aucun commentaire'}", style={'margin': '8px 0', 'fontSize': '0.95em'}),
            html.P(f"🎬 Titre : {titre}", style={'margin': '8px 0', 'fontSize': '0.95em'}),
            html.Img(src=poster_url, style={'marginTop': '10px', 'maxWidth': '200px', 'borderRadius': '8px'})
        ], style={
            'backgroundColor': '#f8fff9',
            'border': '2px solid #27ae60',
            'borderRadius': '12px',
            'padding': '20px',
            'textAlign': 'center'
        })
    ])

# --- Lancer l'application ---
if __name__ == "__main__":
    app.run_server(debug=True)
