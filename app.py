import dash
from dash import html, dcc, Output, Input, State
import pandas as pd
from app_instance import app 
import urllib.parse
import os
import random
import plotly.express as px

# --- Fonction pour charger les données ---
def load_data():
    """Recharge les données du CSV à chaque appel"""
    df = pd.read_csv('data/avis_film_fr_sample.csv', delimiter=';')
    return df

# --- Fonction pour générer la section des avis multiples ---
def get_multiple_reviews_section(film_title, selected_review_index):
    """Génère la section d'affichage des avis multiples s'il y en a plus d'un"""
    df = load_data()
    
    # Trouver tous les avis pour ce film
    film_reviews = df[df['titre'] == film_title]
    
    if len(film_reviews) <= 1:
        return html.Div()  # Pas d'avis multiples
    
    # Créer les boutons pour chaque avis
    review_buttons = []
    for idx, (_, row) in enumerate(film_reviews.iterrows()):
        review_text = row['review']
        # Prendre les 5 premiers mots
        words = review_text.split()[:5]
        preview_text = ' '.join(words) + '...' if len(review_text.split()) > 5 else review_text
        
        # Style différent pour l'avis sélectionné
        button_style = {
            'padding': '8px 12px',
            'margin': '5px',
            'border': '2px solid #667eea' if selected_review_index == idx else '1px solid #ddd',
            'borderRadius': '8px',
            'backgroundColor': '#e8f4fd' if selected_review_index == idx else 'white',
            'cursor': 'pointer',
            'fontSize': '0.9em',
            'transition': 'all 0.3s ease',
            'display': 'inline-block',
            'textAlign': 'center',
            'minWidth': '120px'
        }
        
        review_buttons.append(
            html.Button(
                preview_text,
                id={'type': 'review-btn', 'index': idx},
                style=button_style
            )
        )
    
    return html.Div([
        html.H4(f"📝 {len(film_reviews)} avis disponibles pour ce film :", style={
            'textAlign': 'center',
            'color': '#667eea',
            'marginBottom': '15px',
            'fontSize': '1.2em'
        }),
        html.Div(review_buttons, style={
            'textAlign': 'center',
            'marginBottom': '20px'
        }),
        html.P("Cliquez sur un avis pour l'annoter spécifiquement !", style={
            'textAlign': 'center',
            'color': '#666',
            'fontSize': '0.9em',
            'fontStyle': 'italic'
        })
    ], style={
        'backgroundColor': '#f8f9ff',
        'padding': '20px',
        'borderRadius': '10px',
        'border': '1px solid #e8e8e8',
        'marginBottom': '20px'
    })

CSV_FILE = "./data/avis_user.csv"  # Historique des avis

# --- Pages ---
from pages.connexion import layout as connexion_layout
from pages.ajout_films import layout as add_film_layout
from pages.historique import layout as historique_layout

# --- Layout principal ---
def get_main_layout(username=None, selected_film=None, review_index=None):
    df = load_data()  # Recharger les données
    
    # Si un film spécifique est demandé, le trouver dans le dataset
    if selected_film:
        try:
            film_index = None
            for idx, row in df.iterrows():
                if 'code_film' in df.columns and pd.notna(row['code_film']) and str(row['code_film']) == str(selected_film):
                    film_index = idx
                    break
                elif str(row['Id']) == str(selected_film):
                    film_index = idx
                    break
                elif str(row['titre']) == str(selected_film):
                    film_index = idx
                    break
            
            if film_index is not None:
                random_index = film_index
            else:
                random_index = random.randint(0, len(df) - 1)
        except:
            random_index = random.randint(0, len(df) - 1)
    else:
        random_index = random.randint(0, len(df) - 1)
    
    return html.Div([
        html.Div([
            # En-tête avec navigation
            html.Div([
                html.Div([
                    html.H2(f"🎬 Espace de {username}" if username else "🎬 Annotation de Films", style={
                        'fontSize': '2em',
                        'fontWeight': '300',
                        'margin': '0',
                        'textShadow': '0 2px 4px rgba(0, 0, 0, 0.3)',
                        'color': 'white'
                    })
                ], style={'flex': '1'}),
                
                html.Div([
                    dcc.Link('Historique',
                        href=f'/historique?username={urllib.parse.quote(username)}' if username else '/historique',
                        style={'display': 'inline-block','padding': '10px 16px','backgroundColor': 'rgba(255, 255, 255, 0.2)',
                               'color': 'white','textDecoration': 'none','borderRadius': '20px','fontSize': '0.9em',
                               'fontWeight': '500','marginLeft': '10px','transition': 'all 0.3s ease','border': '1px solid rgba(255, 255, 255, 0.3)'}),
                    dcc.Link('Statistiques',
                        href=f'/stat?username={urllib.parse.quote(username)}' if username else '/stat',
                        style={'display': 'inline-block','padding': '10px 16px','backgroundColor': 'rgba(255, 255, 255, 0.2)',
                               'color': 'white','textDecoration': 'none','borderRadius': '20px','fontSize': '0.9em',
                               'fontWeight': '500','marginLeft': '10px','transition': 'all 0.3s ease','border': '1px solid rgba(255, 255, 255, 0.3)'}),
                    dcc.Link('Ajout films',
                        href=f'/add_film?username={urllib.parse.quote(username)}' if username else '/add_film',
                        style={'display': 'inline-block','padding': '10px 16px','backgroundColor': 'rgba(255, 255, 255, 0.2)',
                               'color': 'white','textDecoration': 'none','borderRadius': '20px','fontSize': '0.9em',
                               'fontWeight': '500','marginLeft': '10px','transition': 'all 0.3s ease','border': '1px solid rgba(255, 255, 255, 0.3)'}),
                    dcc.Link('🚪 Déconnexion',
                        href='/connexion',
                        style={'display': 'inline-block','padding': '10px 16px','backgroundColor': 'rgba(231, 76, 60, 0.8)',
                               'color': 'white','textDecoration': 'none','borderRadius': '20px','fontSize': '0.9em',
                               'fontWeight': '500','marginLeft': '10px','transition': 'all 0.3s ease','border': '1px solid rgba(231, 76, 60, 0.8)',
                               'boxShadow': '0 2px 8px rgba(231, 76, 60, 0.3)'}),
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], style={'display': 'flex','justifyContent': 'space-between','alignItems': 'center',
                      'background': 'linear-gradient(45deg, #667eea, #764ba2)','color': 'white','padding': '20px 30px'}),
            
            # Contenu principal
            html.Div([
                # Colonne principale
                html.Div([
                    dcc.Store(id='current-index', data=random_index),
                    dcc.Store(id='current-film-id'),
                    dcc.Store(id='current-film-title'),  # <-- Nouveau store pour le titre
                    dcc.Store(id='selected-review-index', data=None),  # <-- Store pour l'avis sélectionné
                    html.Div(id='film-selection-message', style={
                        'backgroundColor': '#e8f4fd','color': '#1976d2','padding': '10px 20px',
                        'borderRadius': '8px','marginBottom': '20px','textAlign': 'center','fontSize': '0.9em',
                        'border': '1px solid #bbdefb'
                    }) if selected_film else None,
                    
                    # Titre du film
                    html.Div(id='film-title', style={
                        'fontSize': '2em','fontWeight': '600','marginBottom': '10px','textAlign': 'center','color': '#333'
                    }),
                    
                    # Section des avis multiples
                    html.Div(id='multiple-reviews-section', style={
                        'marginBottom': '20px'
                    }),
                    
                    # Message d'avis au-dessus de l'affiche
                    html.Div(id='annotation-result', style={
                        'fontSize': '1.2em','color': '#667eea','textAlign': 'center','fontWeight': '500','marginBottom': '20px',
                        'minHeight': '24px'
                    }),
                    
                    html.Div([
                        html.Button('👎', id='neg-btn', style={
                            'backgroundColor': '#e74c3c','color': 'white','fontSize': '2em','borderRadius': '50%',
                            'width': '80px','height': '80px','border': 'none','cursor': 'pointer','transition': 'all 0.3s ease',
                            'boxShadow': '0 4px 15px rgba(231, 76, 60, 0.3)','marginRight': '20px'
                        }),
                        html.Div([
                            html.Img(id='film-poster', style={
                                'height': '400px','borderRadius': '15px','boxShadow': '0 10px 30px rgba(0, 0, 0, 0.2)',
                                'display': 'block','marginBottom': '20px'
                            }),
                            html.Button('😐', id='neutral-btn', style={
                                'backgroundColor': '#95a5a6','color': 'white','fontSize': '1.8em','borderRadius': '50%',
                                'width': '70px','height': '70px','border': 'none','cursor': 'pointer','transition': 'all 0.3s ease',
                                'boxShadow': '0 4px 15px rgba(149, 165, 166, 0.3)','margin': '0 auto','display': 'block'
                            })
                        ], style={'textAlign': 'center'}),
                        html.Button('👍', id='pos-btn', style={
                            'backgroundColor': '#27ae60','color': 'white','fontSize': '2em','borderRadius': '50%',
                            'width': '80px','height': '80px','border': 'none','cursor': 'pointer','transition': 'all 0.3s ease',
                            'boxShadow': '0 4px 15px rgba(39, 174, 96, 0.3)','marginLeft': '20px'
                        }),
                    ], style={'display': 'flex','alignItems': 'center','justifyContent': 'center','marginBottom': '40px'}),
                    
                    html.Div(id='film-review', style={
                        'fontSize': '1.1em','lineHeight': '1.6','textAlign': 'center','color': '#555',
                        'maxWidth': '600px','margin': '0 auto 40px auto','fontStyle': 'italic'
                    })
                    
                ], style={'flex': '1','padding': '40px','backgroundColor': 'white','textAlign': 'center'}),
                
                # Colonne droite
                html.Div([
                    html.H3("🎬 Choisir un film", style={
                        'fontSize': '1.5em','fontWeight': '600','marginBottom': '20px','color': '#333','textAlign': 'center'
                    }),
                    dcc.Input(id='film-search', type='text', placeholder='Rechercher un film...', style={
                        'width': '100%','padding': '10px','borderRadius': '8px','border': '1px solid #ddd','marginBottom': '15px','fontSize': '0.9em'
                    }),
                    html.Div(id='films-list', style={
                        'maxHeight': '500px','overflowY': 'auto','border': '1px solid #e8e8e8','borderRadius': '10px','backgroundColor': '#fafafa'
                    })
                ], style={'width': '300px','padding': '20px','backgroundColor': '#f8f9ff','borderLeft': '1px solid #e8e8e8'})
            ], style={'display': 'flex','minHeight': '600px'})
        ], style={'maxWidth': '1400px','margin': '0 auto','background': 'rgba(255, 255, 255, 0.95)',
                  'borderRadius': '15px','boxShadow': '0 20px 40px rgba(0, 0, 0, 0.1)','overflow': 'hidden'})
    ], style={'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
              'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)','minHeight': '100vh','padding': '20px'})

# --- Layout global ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False, pathname='/connexion'),
    html.Div(id='page-content')
])

# --- Affichage des pages ---
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('url', 'search')
)
def display_page(pathname, search):
    params = urllib.parse.parse_qs(search[1:]) if search else {}
    username = params.get('username', [None])[0]
    selected_film = params.get('film', [None])[0]
    review_index = params.get('review_index', [None])[0]
    review_index = int(review_index) if review_index is not None else None

    if pathname == '/connexion':
        return connexion_layout
    elif pathname == '/add_film':
        return add_film_layout
    elif pathname == '/historique':
        return historique_layout
    elif pathname == '/stat':
        from pages.stat import layout as stat_layout
        return stat_layout(search)
    elif pathname == '/main':
        return get_main_layout(username, selected_film, review_index)
    else:
        return get_main_layout(username, selected_film, review_index)

# --- Callback pour la liste des films ---
@app.callback(
    Output('films-list', 'children'),
    [Input('film-search', 'value'), Input('url', 'search')]
)
def update_films_list(search_term, url_search):
    df = load_data()
    params = urllib.parse.parse_qs(url_search[1:]) if url_search else {}
    username = params.get('username', [None])[0]

    try:
        df['Id'] = pd.to_numeric(df['Id'], errors='coerce')
    except:
        pass

    filtered_df = df.copy()
    if search_term:
        filtered_df = df[df['titre'].str.contains(search_term, case=False, na=False)]
    filtered_df = filtered_df.sort_values('Id', ascending=False).head(50)
    titre_doublons = [] # Pour éviter les doublons dans l'affichage

    films_buttons = []
    for idx, row in filtered_df.iterrows():
        if row['titre'] not in titre_doublons:
            titre_doublons.append(row['titre'])
            title = row['titre']
            film_id = row['code_film'] if 'code_film' in df.columns and pd.notna(row['code_film']) and str(row['code_film']).strip() != '' else row['Id']
            films_buttons.append(
                html.Div([
                    dcc.Link([html.Div([html.Div(title, style={'fontSize': '0.9em','color': '#333','fontWeight': '500','textOverflow': 'ellipsis',
                                                            'overflow': 'hidden','whiteSpace': 'nowrap'})])],
                            href=f"/main?username={urllib.parse.quote(username)}&film={urllib.parse.quote(str(film_id))}" 
                                if username else f"/main?film={urllib.parse.quote(str(film_id))}",
                            style={'display': 'block','textDecoration': 'none','color': 'inherit'})
                ], style={'padding': '10px 15px','borderBottom': '1px solid #e8e8e8','cursor': 'pointer','transition': 'background-color 0.2s ease','backgroundColor': 'white'},
                className='film-item')
            )

    if not films_buttons:
        films_buttons.append(html.Div("Aucun film trouvé", style={'padding': '20px','textAlign': 'center','color': '#666','fontStyle': 'italic'}))

    return films_buttons

# --- Callback pour afficher un message si film sélectionné ---
@app.callback(
    Output('film-selection-message', 'children'),
    Input('url', 'search'),
    prevent_initial_call=True
)
def update_selection_message(search):
    params = urllib.parse.parse_qs(search[1:]) if search else {}
    selected_film = params.get('film', [None])[0]
    
    if selected_film:
        return f"🎯 Film sélectionné (ID: {selected_film}). Vous pouvez maintenant donner votre avis."
    return ""

# --- Mise à jour du film affiché ---
@app.callback(
    [Output('film-title', 'children'),
     Output('film-poster', 'src'),
     Output('film-review', 'children'),
     Output('current-film-id', 'data'),
     Output('current-film-title', 'data'),
     Output('multiple-reviews-section', 'children')],
    [Input('current-index', 'data'),
     Input('selected-review-index', 'data'),
     Input('url', 'search')]  # Ajouter l'URL comme input
)
def update_film(index, selected_review_index, search):
    df = load_data()
    
    # Vérifier s'il y a un review_index dans l'URL
    params = urllib.parse.parse_qs(search[1:]) if search else {}
    url_review_index = params.get('review_index', [None])[0]
    url_review_index = int(url_review_index) if url_review_index is not None else None
    
    # Si on a un review_index de l'URL et pas encore de selected_review_index, l'utiliser
    if url_review_index is not None and selected_review_index is None:
        selected_review_index = url_review_index
    
    if index is None or index >= len(df):
        index = random.randint(0, len(df) - 1)
    row = df.iloc[index]
    title = row['titre']
    poster_url = row['poster_url']
    review = row['review']
    film_id = row['code_film'] if 'code_film' in df.columns and pd.notna(row['code_film']) and str(row['code_film']).strip() != '' else row['Id']
    
    # Vérifier s'il y a plusieurs avis pour ce film
    multiple_reviews_section = get_multiple_reviews_section(title, selected_review_index)
    
    # Si un avis spécifique est sélectionné, l'afficher
    if selected_review_index is not None:
        film_reviews = df[df['titre'] == title]
        if not film_reviews.empty and selected_review_index < len(film_reviews):
            selected_row = film_reviews.iloc[selected_review_index]
            review = selected_row['review']
            poster_url = selected_row['poster_url']
    
    return title, poster_url, review, film_id, title, multiple_reviews_section

# --- Callback pour sélectionner un avis spécifique ---
@app.callback(
    Output('selected-review-index', 'data'),
    [Input({'type': 'review-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
     Input('url', 'search')],
    prevent_initial_call=True
)
def select_review(n_clicks_list, search):
    ctx = dash.callback_context
    if not ctx.triggered:
        return None
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Si c'est un bouton d'avis qui a été cliqué
    if 'review-btn' in trigger_id:
        import json
        button_data = json.loads(trigger_id.split('.')[0])
        return button_data['index']
    
    # Si c'est l'URL qui a changé, vérifier s'il y a un review_index
    elif 'url' in trigger_id:
        params = urllib.parse.parse_qs(search[1:]) if search else {}
        url_review_index = params.get('review_index', [None])[0]
        if url_review_index is not None:
            return int(url_review_index)
    
    return None

# --- Annotation film et passage au suivant ---
@app.callback(
    [Output('annotation-result', 'children'),
     Output('current-index', 'data')],
    [Input('neg-btn', 'n_clicks'), Input('pos-btn', 'n_clicks'), Input('neutral-btn', 'n_clicks')],
    [State('current-index', 'data'),
     State('current-film-title', 'data'),  # <-- On récupère le titre réel
     State('selected-review-index', 'data'),  # <-- Index de l'avis sélectionné
     State('url', 'search')],
    prevent_initial_call=True
)
def annotate_and_next(neg_clicks, pos_clicks, neutral_clicks, index, title, selected_review_index, search):
    df = load_data()
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return "", index
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    annotation = ""
    message = ""
    if button_id == 'neg-btn':
        annotation = "Negatif"
        message = "👎 Avis négatif enregistré !"
    elif button_id == 'pos-btn':
        annotation = "Positif"
        message = "👍 Avis positif enregistré !"
    elif button_id == 'neutral-btn':
        annotation = "Neutre"
        message = "😐 Avis neutre enregistré !"

    params = urllib.parse.parse_qs(search[1:]) if search else {}
    username = params.get('username', ["user"])[0]

    if title is not None and annotation:
        # Récupérer le Film_ID correspondant au titre et à l'avis sélectionné
        df_films = load_data()
        film_id = None
        film_match = df_films[df_films['titre'] == title]
        if not film_match.empty:
            # Si un avis spécifique est sélectionné, utiliser son ID correspondant
            if selected_review_index is not None and selected_review_index < len(film_match):
                film_id = film_match.iloc[selected_review_index]['Id']
            else:
                film_id = film_match.iloc[0]['Id']  # Par défaut, le premier
        
        # Utiliser le titre simple
        film_key = str(title)
        
        if selected_review_index is not None:
            message += f" pour l'avis {selected_review_index + 1}"
        
        if os.path.exists(CSV_FILE):
            existing_df = pd.read_csv(CSV_FILE, delimiter=';')
            
            # Vérifier si les colonnes nécessaires existent
            if 'Review_Index' not in existing_df.columns:
                existing_df['Review_Index'] = 0
            if 'Film_ID' not in existing_df.columns:
                existing_df['Film_ID'] = None
            
            # LOGIQUE MODIFIÉE : Chercher une entrée existante pour ce user ET ce Film_ID spécifique
            mask = (existing_df['Username'] == username) & (existing_df['Film_ID'] == film_id)
            
            if mask.any():
                # Mise à jour de l'annotation existante pour ce user + Film_ID
                existing_df.loc[mask, 'Avis'] = annotation
                existing_df.to_csv(CSV_FILE, index=False, sep=';')
                message += " (Avis mis à jour)"
            else:
                # Créer une nouvelle entrée pour ce user + Film_ID
                review_index = selected_review_index if selected_review_index is not None else 0
                new_row = {
                    "Username": username, 
                    "Code_Film": film_key, 
                    "Avis": annotation,
                    "Film_ID": film_id,
                    "Review_Index": review_index
                }
                pd.DataFrame([new_row]).to_csv(CSV_FILE, mode='a', header=False, index=False, sep=';')
        else:
            # Créer un nouveau fichier
            review_index = selected_review_index if selected_review_index is not None else 0
            new_row = {
                "Username": username, 
                "Code_Film": film_key, 
                "Avis": annotation,
                "Film_ID": film_id,
                "Review_Index": review_index
            }
            pd.DataFrame([new_row]).to_csv(CSV_FILE, mode='w', header=True, index=False, sep=';')

    # Tirer un film aléatoire pour le suivant
    next_index = random.randint(0, len(df) - 1)
    return message, next_index

# --- Ajout du CSS pour hover ---
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .film-item:hover {
                background-color: #f0f4ff !important;
                border-left: 3px solid #667eea;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

@app.callback(
    Output('graph-avis-film', 'figure'),
    Input('dropdown-film', 'value'),
    Input('dropdown-user', 'value')
)
def update_graph_avis_film(selected_film, selected_user):
    df = pd.read_csv("./data/avis_user.csv", delimiter=';')
    df['Username'] = df['Username'].astype(str).str.strip()
    df['Code_Film'] = df['Code_Film'].astype(str).str.strip()
    df['Avis'] = df['Avis'].astype(str).str.strip()

    if not selected_film:
        return px.pie(names=[], values=[], title="Sélectionnez un film")

    if selected_user and selected_user != 'Tous':
        df = df[df['Username'] == selected_user]

    # Filtrer par titre de film (grouper tous les avis du même titre)
    df_film = df[df['Code_Film'] == selected_film]
    
    # Grouper les avis par titre de film (somme des annotations)
    avis_counts = df_film['Avis'].value_counts()
    
    if avis_counts.empty:
        return px.pie(names=[], values=[], title=f"Aucun avis pour '{selected_film}'")
    
    # Créer les couleurs personnalisées
    colors = []
    for avis_type in avis_counts.index:
        if avis_type == 'Positif':
            colors.append('#27ae60')  # Vert
        elif avis_type == 'Negatif':
            colors.append('#e74c3c')   # Rouge
        else:  # Neutre
            colors.append('#95a5a6')   # Gris
    
    fig = px.pie(
        names=avis_counts.index,
        values=avis_counts.values,
        title=f"Répartition des avis pour '{selected_film}'" + (f" ({selected_user})" if selected_user and selected_user != 'Tous' else ""),
        color_discrete_sequence=colors
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, sans-serif", size=12),
        title_font=dict(size=18, color='#333'),
        margin=dict(t=50, b=20, l=20, r=20)
    )
    return fig

# --- Lancement de l'application ---
if __name__ == '__main__':
    app.run(debug=True)
